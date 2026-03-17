import sqlite3
import os
from datetime import datetime, timedelta
import random
import pandas as pd
from typing import Dict, List, Tuple

DATABASE_PATH = "business_data.db"
UPLOADED_DATASETS_DIR = "uploaded_datasets"

# Create directory for uploaded datasets if it doesn't exist
os.makedirs(UPLOADED_DATASETS_DIR, exist_ok=True)

def init_database():
    """Initialize SQLite database with sample business data"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Drop existing tables
    cursor.execute("DROP TABLE IF EXISTS sales")
    cursor.execute("DROP TABLE IF EXISTS products")
    cursor.execute("DROP TABLE IF EXISTS regions")
    
    # Create tables
    cursor.execute("""
        CREATE TABLE regions (
            region_id INTEGER PRIMARY KEY,
            region_name TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE sales (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            region_id INTEGER,
            sale_date DATE,
            quantity INTEGER,
            revenue REAL,
            FOREIGN KEY (product_id) REFERENCES products(product_id),
            FOREIGN KEY (region_id) REFERENCES regions(region_id)
        )
    """)
    
    # Insert sample data
    regions = [
        (1, "North America"),
        (2, "Europe"),
        (3, "Asia Pacific"),
        (4, "Latin America")
    ]
    cursor.executemany("INSERT INTO regions VALUES (?, ?)", regions)
    
    products = [
        (1, "Laptop Pro", "Electronics", 1299.99),
        (2, "Wireless Mouse", "Electronics", 29.99),
        (3, "Office Chair", "Furniture", 299.99),
        (4, "Standing Desk", "Furniture", 599.99),
        (5, "Monitor 27\"", "Electronics", 399.99),
        (6, "Keyboard Mechanical", "Electronics", 149.99),
        (7, "Desk Lamp", "Furniture", 79.99),
        (8, "Webcam HD", "Electronics", 89.99),
        (9, "Bookshelf", "Furniture", 199.99),
        (10, "Tablet", "Electronics", 499.99)
    ]
    cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", products)
    
    # Generate sales data for the last 12 months
    sales_data = []
    start_date = datetime.now() - timedelta(days=365)
    
    for day in range(365):
        current_date = start_date + timedelta(days=day)
        # Generate 5-15 sales per day
        for _ in range(random.randint(5, 15)):
            product_id = random.randint(1, 10)
            region_id = random.randint(1, 4)
            quantity = random.randint(1, 10)
            
            # Get product price
            cursor.execute("SELECT price FROM products WHERE product_id = ?", (product_id,))
            price = cursor.fetchone()[0]
            revenue = price * quantity
            
            sales_data.append((
                product_id,
                region_id,
                current_date.strftime("%Y-%m-%d"),
                quantity,
                revenue
            ))
    
    cursor.executemany(
        "INSERT INTO sales (product_id, region_id, sale_date, quantity, revenue) VALUES (?, ?, ?, ?, ?)",
        sales_data
    )
    
    conn.commit()
    conn.close()
    print(f"✓ Database initialized with {len(sales_data)} sales records")

def execute_query(sql_query: str):
    """Execute SQL query and return results"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql_query)
        
        # Fetch results
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        # Convert to list of dictionaries
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        
        conn.close()
        return {"success": True, "data": results, "columns": columns}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_schema():
    """Get database schema for LLM context — dynamically reads all tables"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        schema_parts = []
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            cols = cursor.fetchall()
            col_defs = ", ".join(f"{col[1]} ({col[2]})" for col in cols)
            schema_parts.append(f"Table: {table}\nColumns: {col_defs}")

        conn.close()
        return "\n\n".join(schema_parts)
    except Exception as e:
        return f"Schema unavailable: {str(e)}"

def get_table_schema(table_name: str) -> Dict:
    """Get schema information for a table, including sample values for LLM context"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Get column information
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        schema = {
            "table_name": table_name,
            "columns": []
        }

        for col in columns:
            schema["columns"].append({
                "name": col[1],
                "type": col[2],
                "notnull": col[3],
                "default": col[4],
                "pk": col[5]
            })

        # Fetch a few sample rows so LLM can understand actual values
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
        rows = cursor.fetchall()
        col_names = [col[1] for col in columns]
        schema["sample_rows"] = [dict(zip(col_names, row)) for row in rows]

        conn.close()
        return schema
    except Exception as e:
        return {"error": str(e)}

def upload_dataset(file_path: str, table_name: str) -> Dict:
    """Upload a CSV, Excel, or JSON file and create a table"""
    try:
        # Read file based on extension
        if file_path.endswith('.csv'):
            # Try different encodings for CSV files
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'utf-16']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    break
                except (UnicodeDecodeError, LookupError):
                    continue
            
            if df is None:
                # If all encodings fail, try with errors='ignore'
                df = pd.read_csv(file_path, encoding='utf-8', errors='ignore')
        
        elif file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        
        elif file_path.endswith('.json'):
            df = pd.read_json(file_path)
        
        else:
            return {"success": False, "error": "Unsupported file format. Use CSV, XLSX, or JSON."}
        
        # Check if dataframe is empty
        if df.empty:
            return {"success": False, "error": "Uploaded file is empty"}
        
        # Clean column names (remove spaces, special characters)
        df.columns = [col.strip().replace(' ', '_').replace('-', '_').lower() for col in df.columns]
        
        # Connect to database
        conn = sqlite3.connect(DATABASE_PATH)
        
        # Drop existing table if it exists
        cursor = conn.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        
        # Create table from dataframe
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        
        conn.commit()
        conn.close()
        
        # Get schema information
        schema = get_table_schema(table_name)
        
        return {
            "success": True,
            "table_name": table_name,
            "rows": len(df),
            "columns": len(df.columns),
            "schema": schema,
            "column_names": list(df.columns)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_dataset_preview(table_name: str, limit: int = 10) -> Dict:
    """Get preview of uploaded dataset"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        rows = cursor.fetchall()
        
        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Convert to list of dictionaries
        data = [dict(zip(columns, row)) for row in rows]
        
        # Get total row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_rows = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "success": True,
            "data": data,
            "columns": columns,
            "total_rows": total_rows,
            "preview_rows": len(data)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def list_tables() -> List[str]:
    """List all tables in the database"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return tables
    except Exception as e:
        return []

if __name__ == "__main__":
    init_database()
