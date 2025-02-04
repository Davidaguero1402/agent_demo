from app import engine
from sqlalchemy import text

def query(sql_query: str):
    try:
        with engine.connect() as connection:
            result = connection.execute(text(sql_query))
            columns = result.keys()
            rows = result.fetchall()
            return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print(f"Error executing SQL query: {e}")
        print(f"SQL query: {sql_query}")
        # Imprimir más detalles sobre el resultado si es posible
        if 'result' in locals():
            print(f"Result keys: {result.keys()}")
            print(f"First row: {result.fetchone()}")
        return None