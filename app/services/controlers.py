from app import engine
from sqlalchemy import text, inspect
import sqlparse
import json
from app import agent
from typing import Any, List

def get_schema():
#    schema = {}
#    with engine.connect() as connection:
#        # Obtener columnas para la tabla clasificacion_general
#        columns_query = text("""
#            SELECT column_name, data_type 
#            FROM information_schema.columns 
#            WHERE table_name = 'Participantes' 
#            ORDER BY ordinal_position
#        """)
#        columns = connection.execute(columns_query).fetchall()
#        
#        schema['Participantes'] = [
#            {"name": col[0], "type": col[1]} for col in columns
#        ]
#    
#    return schema
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


def validate_sql_query(sql_query: str, schema: dict) -> bool:
    parsed = sqlparse.parse(sql_query)[0]
    table_name = None

    # Buscar el nombre de la tabla
    for token in parsed.tokens:
        if isinstance(token, sqlparse.sql.Identifier):
            table_name = token.get_real_name()
            break

    if not table_name or table_name not in schema:
        return False

    columns = [col["name"] for col in schema[table_name]]

    # Recorrer tokens para validar las columnas
    for token in parsed.tokens:
        if isinstance(token, sqlparse.sql.Where):
            for where_token in token.tokens:
                if isinstance(where_token, sqlparse.sql.Comparison):
                    column_name = where_token.left.get_real_name()
                    if column_name not in columns:
                        return False

    return True


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
    
def clean_json_response(response_text):
    """
    Clean and extract JSON from the model's response text.
    Handles various formats that might be returned by the model.
    """
    # Remove code blocks if present
    cleaned = response_text.replace('```json', '').replace('```', '').strip()
    
    # Try to find JSON content between curly braces
    try:
        start_idx = cleaned.index('{')
        end_idx = cleaned.rindex('}') + 1
        json_str = cleaned[start_idx:end_idx]
        return json_str
    except ValueError:
        # If no valid JSON structure is found, return None
        return None
    
async def human_query_to_sql(human_query: str):
    database_schema = get_schema()
    system_message = f"""
    Given the following schema, write a SQL query that retrieves the requested information. 
    Return the SQL query inside a JSON structure with the key "sql_query".
    Only use columns that exist in the schema.
    <example>{{"sql_query": "SELECT * FROM users WHERE age > 18;", "original_query": "Show me all users older than 18 years old."}}</example>
    <schema>
    {json.dumps(database_schema, indent=2)}
    </schema>
    """
    user_message = human_query
    model = agent
    # Esperar correctamente el resultado de generate_content
    response = await model.generate_content(system_message + user_message)
    
    # Procesar la respuesta como texto
    cleaned_response = clean_json_response(response.text)
    try:
        response_json = json.loads(cleaned_response)
        sql_query = response_json.get("sql_query")
        if sql_query and validate_sql_query(sql_query, database_schema):
            return sql_query
        else:
            print("Generated SQL query is invalid or uses non-existent columns")
            return None
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return None



async def build_answer(result: list[dict[str, Any]], human_query: str) -> str | None:
    """
    Build an answer for the user based on SQL results and their question.
    
    Parameters:
    - result: The rows returned by the SQL query as a list of dictionaries.
    - human_query: The original query/question from the user.
    
    Returns:
    - A textual response generated by the model, or None if an error occurs.
    """
    race_description = (
        "La carrera es un evento deportivo donde los participantes compiten en diferentes categorías "
        "según su edad, sexo y distancia. Se calcula la posición general, por categoría y por sexo "
        "en función del tiempo registrado."
    )
    
    system_message = f"""
    You are assisting with a sports event database. Use the following description to understand the context:
    {race_description}

    Respond to the user's query based on the SQL rows provided. Offer additional information or insights
    related to their interest in the event.

    <user_question>
    {human_query}
    </user_question>

    <sql_response>
    {result}
    </sql_response>

    Example response:
    - Based on the data provided, here is the answer to your query...
    - Would you like to know about the top performers in another category, or detailed rankings by age group?
    Advertecia: 
    - La respuesta debe ser en español.
    - La respuesta debe ser coherente con la consulta realizada.
    - La respuesta debe ser relevante para el contexto de la carrera deportiva.
    """
    
    try:
        model = agent
        response = await model.generate_content(system_message)
        if response and response.text:
            return response.text.strip()
        else:
            print("No response from the model.")
            return None
    except Exception as e:
        print(f"Error generating response: {e}")
        return None

