from app import engine
from sqlalchemy import inspect

def get_schema():
    schema = {}
    inspector = inspect(engine)
    
    # Obtener todas las tablas
    tables = inspector.get_table_names()
    
    for table_name in tables:
        # Obtener columnas de cada tabla
        columns = inspector.get_columns(table_name)
        
        # Obtener información de las columnas
        schema[table_name] = [
            {
                "name": col['name'], 
                "type": str(col['type']),
                "nullable": col.get('nullable', True),
                "primary_key": col.get('primary_key', False)
            } for col in columns
        ]
    
    return schema