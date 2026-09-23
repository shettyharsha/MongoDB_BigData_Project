# MongoDB Big Data Analytics Project

## Project Overview

This college project demonstrates how a sales dataset can be stored, processed, and analyzed with MongoDB. Python and Pandas are used to read and prepare CSV data, Flask provides the web application and API routes, and MongoDB stores the sales records. The browser dashboard uses Chart.js to display revenue charts and provides tools for searching, filtering, uploading, and analyzing sales data.

## Objectives

- Store sales records in a MongoDB database.
- Import CSV data into MongoDB using Python and Pandas.
- Calculate useful sales statistics such as total revenue and average order value.
- Provide a simple Flask web dashboard for viewing and searching sales data.
- Demonstrate MongoDB queries, aggregation pipelines, indexes, and bulk operations.

## Technologies Used

- Python
- Flask
- MongoDB
- PyMongo
- Pandas
- HTML, CSS, and JavaScript
- Chart.js, loaded in the dashboard from jsDelivr

## Project Structure

```text
MongoDB_BigData_Project/
|-- app.py
|-- database.py
|-- import_data.py
|-- requirements.txt
|-- sales.csv
|-- .gitignore
|-- README.md
|-- templates/
|   `-- index.html
|-- venv/                 # Local virtual environment, not uploaded to GitHub
`-- __pycache__/          # Generated Python files, not uploaded to GitHub
```

## Database

The application connects to the local MongoDB server at:

```text
mongodb://localhost:27017/
```

It uses:

- **Database:** `bigdata_db`
- **Collection:** `sales`

Each sales record contains these important fields:

- `sale_id`
- `date`
- `product`
- `category`
- `quantity`
- `price`
- `city`
- `state`

The application also creates indexes for `product`, `city`, `date`, and `category` to support common searches and filters.

## Data Processing

The `import_data.py` script reads `sales.csv` with Pandas, converts the rows to records, and inserts them into the `bigdata_db.sales` collection using PyMongo.

The Flask application uses MongoDB queries and aggregation pipelines to:

- Calculate total revenue from `quantity * price`.
- Calculate average order value.
- Group revenue by city and category.
- Group monthly revenue using the `date` field.
- Filter and search records.
- Process uploaded CSV files after checking their required columns and removing duplicate `sale_id` values from the uploaded data.

## Features

- Dashboard cards for total records, total revenue, average order value, product count, and city count.
- Monthly revenue line chart.
- Revenue by category bar chart.
- Revenue totals by city.
- Product, category, city, and date search filters.
- Search results displayed in a table, with a limit of 100 records.
- CSV dataset upload with file-type, required-column, empty-data, and duplicate checks.
- MongoDB index viewing and automatic creation of the main search indexes.
- Advanced aggregation showing the top five cities by revenue for a category.
- Advanced filtering by category and city.
- Bulk insert demonstration using JSON records, with validation and duplicate handling.

## How to Run the Project

These instructions are for Windows using the VS Code terminal.

### 1. Open the project folder

Open `MongoDB_BigData_Project` in VS Code and open a terminal in the project folder.

### 2. Create a virtual environment

If a virtual environment does not already exist, run:

```powershell
python -m venv venv
```

### 3. Activate the virtual environment

In PowerShell, run:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks the activation script, run this once in the current terminal and then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

### 4. Install the Python requirements

```powershell
python -m pip install -r requirements.txt
```

### 5. Start MongoDB

Make sure the MongoDB server is running locally on its default address:

```text
mongodb://localhost:27017/
```

### 6. Import the sample data

Run this from the project folder:

```powershell
python import_data.py
```

### 7. Start the Flask application

```powershell
python app.py
```

### 8. Open the dashboard

Open this address in a browser:

```text
http://127.0.0.1:5000/
```

## Sample Dataset

The `sales.csv` file contains sample sales records for the project. It includes sale IDs, dates, products, categories, quantities, prices, cities, and states. The file can be imported with `import_data.py` or uploaded through the dashboard.

## Results / Dashboard

After MongoDB is running and sales data has been imported, the dashboard shows:

- The number of sales records.
- Total revenue and average order value.
- The number of products and cities.
- Monthly revenue in a line chart.
- Category revenue in a bar chart.
- Revenue totals by city.
- Matching sales records from the search and filter tools.
- Results from the indexing, aggregation, filtering, upload, and bulk-operation tools.

The displayed results depend on the records currently stored in the `bigdata_db.sales` collection.

## Future Enhancements

- Add user authentication and role-based access.
- Add date-range filters and more dashboard visualizations.
- Add export options for filtered results.
- Add stronger data type validation for uploaded CSV fields.
- Add automated tests for the Flask routes and database operations.
- Deploy the application with a secured MongoDB connection.

## Conclusion

This project provides a practical example of using MongoDB, Python, Pandas, and Flask together for sales data storage and analysis. The dashboard makes the results easier to explore while demonstrating important database operations such as querying, aggregation, indexing, and bulk processing.

## Author

Harsha Shetty
