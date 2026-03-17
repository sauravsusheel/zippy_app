# Supported Datasets for Zippy AI

## File Formats Supported

✅ **CSV Files** (.csv)
- Comma-separated values
- Plain text format
- Most common data format

✅ **Excel Files** (.xlsx)
- Microsoft Excel spreadsheets
- Modern Excel format
- Can contain multiple sheets (first sheet is used)

✅ **JSON Files** (.json)
- JavaScript Object Notation
- Array of objects format
- Each object becomes a row

❌ **Not Supported**
- .xls (old Excel format)
- .xml
- .txt
- .pdf
- Other formats

## Dataset Structure Requirements

### Column Requirements
- **Column Names**: Must be present in the first row
- **Data Types**: Automatically detected (text, numbers, dates)
- **No Empty Columns**: Columns should have meaningful names
- **Special Characters**: Avoid special characters in column names (use underscores instead)

### Data Requirements
- **Minimum Rows**: At least 1 row of data (plus header)
- **Consistent Format**: All rows should have the same number of columns
- **No Merged Cells**: Excel files should not have merged cells
- **Encoding**: UTF-8 encoding recommended

## Example Dataset Structures

### Sales Data (Recommended)
```
Date,Product,Region,Revenue,Quantity,Category
2024-01-01,Laptop,North,5000,2,Electronics
2024-01-02,Mouse,South,150,10,Accessories
2024-01-03,Keyboard,East,300,5,Accessories
2024-01-04,Monitor,West,2000,3,Electronics
```

### JSON Format
```json
[
  {
    "Date": "2024-01-01",
    "Product": "Laptop",
    "Region": "North",
    "Revenue": 5000,
    "Quantity": 2,
    "Category": "Electronics"
  },
  {
    "Date": "2024-01-02",
    "Product": "Mouse",
    "Region": "South",
    "Revenue": 150,
    "Quantity": 10,
    "Category": "Accessories"
  }
]
```

### Business Metrics
```
Month,Sales,Profit,Expenses,Customers
January,50000,15000,35000,250
February,55000,16500,38500,280
March,60000,18000,42000,300
```

### Product Performance
```
Product_ID,Product_Name,Category,Price,Stock,Sales_Count
1,Laptop,Electronics,1200,50,150
2,Mouse,Accessories,25,500,2000
3,Keyboard,Accessories,75,300,800
4,Monitor,Electronics,400,100,300
```

### Customer Data
```
Customer_ID,Name,Email,City,Purchase_Amount,Purchase_Date
1,John Doe,john@example.com,New York,5000,2024-01-15
2,Jane Smith,jane@example.com,Los Angeles,3500,2024-01-20
3,Bob Johnson,bob@example.com,Chicago,2000,2024-01-25
```

## How to Use

### Step 1: Prepare Your Dataset
- Ensure file is in CSV or XLSX format
- Add meaningful column headers
- Check data consistency

### Step 2: Upload Dataset
1. Go to http://localhost:3000
2. Login with face authentication
3. Click "Upload Dataset"
4. Select your CSV or XLSX file
5. Wait for upload to complete

### Step 3: View Preview
- System shows first few rows
- Displays column names and types
- Shows total rows and columns

### Step 4: Ask Questions
- Type natural language questions
- Examples:
  - "Show total sales by region"
  - "What is the average revenue?"
  - "List top 5 products by sales"
  - "Compare Q1 vs Q2 performance"

## Data Type Support

### Supported Data Types
- **Text/String**: Names, categories, descriptions
- **Numbers**: Integer and decimal values
- **Dates**: Various date formats (auto-detected)
- **Boolean**: Yes/No, True/False, 1/0

### Automatic Detection
The system automatically detects:
- Column data types
- Date formats
- Numeric ranges
- Text categories

## Best Practices

✅ **Do**
- Use clear, descriptive column names
- Keep data consistent and clean
- Use standard date formats (YYYY-MM-DD)
- Remove duplicate rows
- Use meaningful values

❌ **Don't**
- Use special characters in column names
- Mix data types in same column
- Leave empty cells (use 0 or "N/A")
- Use merged cells in Excel
- Upload files larger than 50MB

## Example Queries

Once you upload a dataset, you can ask:

**Sales Analysis**
- "Show total sales by region"
- "Which product has highest revenue?"
- "What is the average order value?"

**Time Series**
- "Display monthly revenue trend"
- "Compare Q1 vs Q2 performance"
- "Show sales growth over time"

**Comparisons**
- "Compare product categories"
- "Which region performs best?"
- "Top 5 customers by spending"

**Aggregations**
- "Total revenue by category"
- "Average price by product type"
- "Count of transactions per month"

## Troubleshooting

### Upload Fails
- Check file format (must be .csv or .xlsx)
- Ensure file is not corrupted
- Try with smaller file first

### Query Returns No Results
- Check column names match your data
- Verify data exists in the dataset
- Try simpler query first

### Unexpected Results
- Review the generated SQL query
- Check data types are correct
- Verify data values are as expected

## File Size Limits

- **Maximum File Size**: 50MB
- **Recommended Size**: < 10MB for best performance
- **Optimal Size**: 1-5MB

## Sample Datasets

You can create sample datasets using these templates:

**sales.csv**
```
Date,Product,Region,Revenue,Quantity
2024-01-01,Laptop,North,5000,2
2024-01-02,Mouse,South,150,10
2024-01-03,Keyboard,East,300,5
```

**customers.csv**
```
Customer_ID,Name,City,Total_Spent,Purchase_Count
1,John Doe,New York,5000,10
2,Jane Smith,Los Angeles,3500,8
3,Bob Johnson,Chicago,2000,5
```

---

**Summary**: Zippy supports CSV and XLSX files with any business data structure. The system automatically detects columns and data types, then converts natural language questions into SQL queries to analyze your data.
