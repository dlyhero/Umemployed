import json
import os
import argparse
from datetime import date, datetime
from decimal import Decimal

import psycopg2

# Database connection details
# Set your DATABASE_URL in the environment or replace with your connection string
# Format: postgresql://username:password@hostname:port/database
DATABASE_URL = os.environ.get("DATABASE_URL", "")


def fetch_all_tables(cursor, include_tables=None, exclude_tables=None):
    """
    Fetch all table names in the public schema.
    
    Args:
        cursor: Database cursor
        include_tables: List of specific tables to include (if None, includes all)
        exclude_tables: List of tables to exclude
    
    Returns:
        List of table names
    """
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
    all_tables = [table[0] for table in cursor.fetchall()]
    
    # Filter tables if needed
    if include_tables:
        tables = [t for t in all_tables if t in include_tables]
    else:
        tables = all_tables
    
    # Exclude tables if needed
    if exclude_tables:
        tables = [t for t in tables if t not in exclude_tables]
        
    return tables


def convert_value(value):
    """Convert values to a JSON serializable format."""
    if isinstance(value, datetime):
        return value.isoformat()  # Convert datetime to ISO 8601 string
    elif isinstance(value, date):
        return value.isoformat()  # Convert date to ISO 8601 string
    elif isinstance(value, Decimal):
        return float(value)  # Convert Decimal to float
    return value  # Return the value as is for other types


def fetch_table_data(cursor, table_name):
    """Fetch all data from the specified table."""
    # Use proper quoting for table names to avoid SQL injection
    quoted_table_name = psycopg2.extensions.quote_ident(table_name, cursor.connection)
    
    query = f"SELECT * FROM {quoted_table_name};"
    cursor.execute(query)
    records = cursor.fetchall()

    # Get column names
    col_names = [desc[0] for desc in cursor.description]

    # Create a list of dictionaries to hold the data
    # Convert each value to a JSON serializable format
    return [
        {col: convert_value(record[i]) for i, col in enumerate(col_names)} for record in records
    ]


def main(output_file="all_data.json", include_tables=None, exclude_tables=None):
    all_data = {}

    try:
        # Validate database connection string
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL is not set. Please provide a valid database connection string.")
            
        # Create a connection to the database
        print("Connecting to database...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        print("Connected successfully!")

        # Fetch all table names
        tables = fetch_all_tables(cursor, include_tables, exclude_tables)
        if not tables:
            print("No tables found or all tables were excluded.")
            return
            
        print(f"Found {len(tables)} tables: {', '.join(tables)}")

        # Loop through each table and fetch data
        for table in tables:
            print(f"Fetching data from table: {table}")
            data = fetch_table_data(cursor, table)
            all_data[table] = data
            print(f"  - Retrieved {len(data)} records")

        # Write all data to a single JSON file
        with open(output_file, "w") as json_file:
            json.dump(all_data, json_file, indent=4)

        print(f"All data has been written to {output_file}.")

    except psycopg2.Error as e:
        print(f"Database error occurred: {e}")
        print(f"Error details: {e.diag.message_primary if hasattr(e, 'diag') else 'No additional details'}")
    except ValueError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Close database connection
        if 'conn' in locals() and conn:
            print("Closing database connection...")
            cursor.close()
            conn.close()
            print("Connection closed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export database tables to JSON")
    parser.add_argument("--db-url", dest="db_url", help="Database connection URL")
    parser.add_argument("--output", dest="output_file", default="all_data.json", 
                       help="Output JSON file path (default: all_data.json)")
    parser.add_argument("--include", dest="include_tables", nargs="+", 
                       help="List of tables to include (if omitted, includes all)")
    parser.add_argument("--exclude", dest="exclude_tables", nargs="+",
                       help="List of tables to exclude")
    args = parser.parse_args()
    
    # Use command line argument if provided
    if args.db_url:
        DATABASE_URL = args.db_url
        
    main(args.output_file, args.include_tables, args.exclude_tables)
