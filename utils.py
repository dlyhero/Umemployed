import psycopg2  
import json  
from datetime import datetime, date  
from decimal import Decimal  

# Database connection details  
DATABASE_URL = ""  

def fetch_all_tables(cursor):  
    """Fetch all table names in the public schema."""  
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")  
    return [table[0] for table in cursor.fetchall()]  

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
    query = f"SELECT * FROM {table_name};"  
    cursor.execute(query)  
    records = cursor.fetchall()  
    
    # Get column names  
    col_names = [desc[0] for desc in cursor.description]  
    
    # Create a list of dictionaries to hold the data  
    # Convert each value to a JSON serializable format  
    return [{col: convert_value(record[i]) for i, col in enumerate(col_names)} for record in records]  

def main():  
    all_data = {}  
    
    try:  
        # Create a connection to the database  
        conn = psycopg2.connect(DATABASE_URL)  
        cursor = conn.cursor()  

        # Fetch all table names  
        tables = fetch_all_tables(cursor)  

        # Loop through each table and fetch data  
        for table in tables:  
            print(f"Fetching data from table: {table}")  
            data = fetch_table_data(cursor, table)  
            all_data[table] = data  

        # Write all data to a single JSON file  
        with open('all_data.json', 'w') as json_file:  
            json.dump(all_data, json_file, indent=4)  
        
        print("All data has been written to all_data.json.")  

    except Exception as e:  
        print(f"An error occurred: {e}")  

    finally:  
        # Close database connection  
        if conn:  
            cursor.close()  
            conn.close()  

if __name__ == "__main__":  
    main()