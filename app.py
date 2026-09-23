import re

import pandas as pd
from flask import Flask, jsonify, render_template, request
from pymongo import InsertOne, MongoClient, UpdateOne
from werkzeug.exceptions import RequestEntityTooLarge

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

client = MongoClient("mongodb://localhost:27017/")
db = client["bigdata_db"]
collection = db["sales"]
SEARCH_RESULT_LIMIT = 100
REQUIRED_COLUMNS = {
    "sale_id",
    "date",
    "product",
    "category",
    "quantity",
    "price",
    "city",
    "state"
}
INDEXES = {
    "idx_product": "product",
    "idx_city": "city",
    "idx_date": "date",
    "idx_category": "category"
}


def ensure_search_indexes():
    existing_indexes = collection.index_information()
    existing_fields = {
        tuple(index.get("key", []))
        for index in existing_indexes.values()
    }

    for index_name, field in INDEXES.items():
        if index_name not in existing_indexes and ((field, 1),) not in existing_fields:
            collection.create_index(field, name=index_name)


ensure_search_indexes()


@app.errorhandler(RequestEntityTooLarge)
def handle_large_upload(error):
    return jsonify({
        "success": False,
        "message": "The CSV file is too large. The maximum size is 16 MB."
    }), 413


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/dashboard")
def dashboard():
    try:
        total_records = collection.count_documents({})

        pipeline = [
            {
                "$project": {
                    "revenue": {
                        "$multiply": ["$quantity", "$price"]
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_revenue": {
                        "$sum": "$revenue"
                    }
                }
            }
        ]

        result = list(collection.aggregate(pipeline))
        total_revenue = result[0]["total_revenue"] if result else 0
        products = len([
            value for value in collection.distinct("product")
            if value
        ])
        cities = len([
            value for value in collection.distinct("city")
            if value
        ])
        average_order = total_revenue / total_records if total_records > 0 else 0

        return jsonify({
            "total_sales": total_records,
            "total_revenue": total_revenue,
            "average_order": average_order,
            "total_records": total_records,
            "products": products,
            "cities": cities
        })
    except Exception:
        return jsonify({
            "error": "Unable to load dashboard statistics."
        }), 500


@app.route("/api/sales-by-city")
def sales_by_city():

    pipeline = [
        {
            "$project": {
                "city": 1,
                "revenue": {
                    "$multiply": ["$quantity", "$price"]
                }
            }
        },
        {
            "$group": {
                "_id": "$city",
                "revenue": {
                    "$sum": "$revenue"
                }
            }
        },
        {
            "$sort": {
                "revenue": -1
            }
        }
    ]

    result = list(collection.aggregate(pipeline))

    data = []

    for item in result:
        data.append({
            "city": item["_id"],
            "revenue": item["revenue"]
        })

    return jsonify(data)


@app.route("/api/sales-by-category")
def sales_by_category():

    pipeline = [
        {
            "$project": {
                "category": 1,
                "revenue": {
                    "$multiply": ["$quantity", "$price"]
                }
            }
        },
        {
            "$group": {
                "_id": "$category",
                "revenue": {
                    "$sum": "$revenue"
                }
            }
        },
        {
            "$sort": {
                "revenue": -1
            }
        }
    ]

    result = list(collection.aggregate(pipeline))

    return jsonify([
        {
            "category": item["_id"],
            "revenue": item["revenue"]
        }
        for item in result
    ])


@app.route("/api/monthly-revenue")
def monthly_revenue():

    pipeline = [
        {
            "$set": {
                "parsed_date": {
                    "$dateFromString": {
                        "dateString": "$date",
                        "format": "%Y-%m-%d",
                        "onError": None,
                        "onNull": None
                    }
                }
            }
        },
        {
            "$match": {
                "parsed_date": {
                    "$ne": None
                }
            }
        },
        {
            "$project": {
                "month": {
                    "$month": "$parsed_date"
                },
                "revenue": {
                    "$multiply": ["$quantity", "$price"]
                }
            }
        },
        {
            "$group": {
                "_id": "$month",
                "revenue": {
                    "$sum": "$revenue"
                }
            }
        },
        {
            "$sort": {
                "_id": 1
            }
        }
    ]

    result = list(collection.aggregate(pipeline))

    return jsonify([
        {
            "month": item["_id"],
            "revenue": item["revenue"]
        }
        for item in result
    ])


@app.route("/api/categories")
def categories():
    values = collection.distinct("category")
    return jsonify(sorted(value for value in values if value))


@app.route("/api/cities")
def cities():
    values = collection.distinct("city")
    return jsonify(sorted(value for value in values if value))


@app.route("/api/search")
def search():
    product = request.args.get("product", "").strip()
    category = request.args.get("category", "").strip()
    city = request.args.get("city", "").strip()
    date = request.args.get("date", "").strip()

    filters = {}

    if product:
        filters["product"] = {
            "$regex": re.escape(product),
            "$options": "i"
        }
    if category:
        filters["category"] = category
    if city:
        filters["city"] = city
    if date:
        filters["date"] = date

    projection = {"_id": 0}
    results = collection.find(filters, projection).limit(SEARCH_RESULT_LIMIT)

    return jsonify(list(results))


@app.route("/api/indexes")
def indexes():
    index_data = []
    for name, information in collection.index_information().items():
        index_data.append({
            "name": name,
            "fields": [field for field, direction in information["key"]]
        })
    return jsonify(index_data)


@app.route("/api/create-indexes", methods=["POST"])
def create_indexes():
    ensure_search_indexes()
    return jsonify({
        "success": True,
        "message": "Search indexes are ready.",
        "indexes": list(collection.index_information().keys())
    })


@app.route("/api/advanced-aggregation")
def advanced_aggregation():
    category = request.args.get("category", "Electronics").strip()
    pipeline = [
        {
            "$match": {
                "category": category
            }
        },
        {
            "$project": {
                "city": 1,
                "revenue": {
                    "$multiply": ["$quantity", "$price"]
                }
            }
        },
        {
            "$group": {
                "_id": "$city",
                "total_revenue": {
                    "$sum": "$revenue"
                }
            }
        },
        {
            "$sort": {
                "total_revenue": -1
            }
        },
        {
            "$limit": 5
        }
    ]

    result = collection.aggregate(pipeline)
    return jsonify([
        {
            "city": item["_id"],
            "total_revenue": item["total_revenue"]
        }
        for item in result
    ])


@app.route("/api/advanced-filter")
def advanced_filter():
    filters = {}
    for field in ("product", "category", "city", "date"):
        value = request.args.get(field, "").strip()
        if value:
            filters[field] = value

    results = collection.find(filters, {"_id": 0}).limit(SEARCH_RESULT_LIMIT)
    return jsonify(list(results))


@app.route("/api/bulk-demo", methods=["POST"])
def bulk_demo():
    payload = request.get_json(silent=True)
    records = payload.get("records") if isinstance(payload, dict) else None

    if not isinstance(records, list) or not records:
        return jsonify({
            "success": False,
            "message": "Provide a non-empty records list."
        }), 400

    if len(records) > SEARCH_RESULT_LIMIT:
        return jsonify({
            "success": False,
            "message": "A maximum of 100 records can be processed at once."
        }), 400

    operations = []
    seen_sale_ids = set()
    existing_ids = set(collection.distinct(
        "sale_id",
        {"sale_id": {"$in": [record.get("sale_id") for record in records if isinstance(record, dict)]}}
    ))

    for record in records:
        if not isinstance(record, dict) or not REQUIRED_COLUMNS.issubset(record):
            return jsonify({
                "success": False,
                "message": "Each record must contain all required sales fields."
            }), 400

        sale_id = record["sale_id"]
        if sale_id in seen_sale_ids:
            continue
        seen_sale_ids.add(sale_id)

        if sale_id in existing_ids:
            operations.append(UpdateOne(
                {"sale_id": sale_id},
                {"$setOnInsert": record},
                upsert=False
            ))
        else:
            operations.append(InsertOne(record))

    if not operations:
        return jsonify({
            "success": True,
            "matched": 0,
            "modified": 0,
            "inserted": 0,
            "skipped_duplicates": len(records)
        })

    try:
        result = collection.bulk_write(operations, ordered=False)
    except Exception:
        return jsonify({
            "success": False,
            "message": "Bulk operation could not be completed."
        }), 400

    return jsonify({
        "success": True,
        "message": "Bulk operation completed successfully.",
        "matched": result.matched_count,
        "modified": result.modified_count,
        "inserted": result.inserted_count,
        "skipped_duplicates": len(records) - len(operations)
    })


@app.route("/api/upload", methods=["POST"])
def upload_dataset():
    uploaded_file = request.files.get("file")

    if uploaded_file is None or not uploaded_file.filename:
        return jsonify({
            "success": False,
            "message": "Please select a CSV file."
        }), 400

    if not uploaded_file.filename.lower().endswith(".csv"):
        return jsonify({
            "success": False,
            "message": "Only CSV files are allowed."
        }), 400

    try:
        dataframe = pd.read_csv(uploaded_file)
    except pd.errors.EmptyDataError:
        return jsonify({
            "success": False,
            "message": "CSV file is empty."
        }), 400
    except (pd.errors.ParserError, UnicodeDecodeError):
        return jsonify({
            "success": False,
            "message": "Unable to read CSV file. Please check the file format."
        }), 400

    dataframe.columns = [str(column).strip() for column in dataframe.columns]
    missing_columns = sorted(REQUIRED_COLUMNS - set(dataframe.columns))

    if missing_columns:
        return jsonify({
            "success": False,
            "message": "Invalid CSV. Missing columns: " + ", ".join(missing_columns)
        }), 400

    dataframe = dataframe.dropna(how="all")

    if dataframe.empty:
        return jsonify({
            "success": False,
            "message": "CSV file is empty."
        }), 400

    for column in dataframe.select_dtypes(include=["object"]).columns:
        dataframe[column] = dataframe[column].str.strip()

    if dataframe[list(REQUIRED_COLUMNS)].isnull().any().any():
        return jsonify({
            "success": False,
            "message": "Invalid CSV. Required fields cannot be empty."
        }), 400

    records_found = len(dataframe)
    dataframe = dataframe.drop_duplicates(subset=["sale_id"], keep="first")
    records = dataframe.to_dict("records")
    sale_ids = [record["sale_id"] for record in records]
    existing_ids = set(collection.distinct("sale_id", {"sale_id": {"$in": sale_ids}}))
    new_records = [record for record in records if record["sale_id"] not in existing_ids]

    if new_records:
        collection.insert_many(new_records)

    skipped_duplicates = records_found - len(new_records)
    return jsonify({
        "success": True,
        "message": "Dataset uploaded successfully.",
        "records_found": records_found,
        "inserted": len(new_records),
        "skipped_duplicates": skipped_duplicates
    })


if __name__ == "__main__":
    app.run(debug=True)