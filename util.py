from app import db
from sqlalchemy import text
import traceback

def execute_raw_query(query):
    try:
        print(f"Executing raw SQL query: {query}")
        result = db.session.execute(text(query))
        
        columns = result.keys()
        print(f"Query columns: {columns}")
        rows = []
        for row in result:
            row_dict = {}
            for i, column in enumerate(columns):
                row_dict[column] = row[i]
            rows.append(row_dict)
            
        db.session.commit()
        print(f"Query returned {len(rows)} rows")
        return rows
    except Exception as e:
        db.session.rollback()
        print(f"Error executing query: {str(e)}")
        print(traceback.format_exc())
        raise e
