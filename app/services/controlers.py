from app import engine
from sqlalchemy import text
import sqlparse
import json
from app import agent
from typing import Any, List

def get_schema():
    schema = {}
    with engine.connect() as connection:
        # Obtener columnas para la tabla clasificacion_general
        columns_query = text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'clasificacion_general' 
            ORDER BY ordinal_position
        """)
        columns = connection.execute(columns_query).fetchall()
        
        schema['clasificacion_general'] = [
            {"name": col[0], "type": col[1]} for col in columns
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
    model = agent.genai.GenerativeModel("models/gemini-1.5-flash")
    response = model.generate_content(system_message + user_message)
    
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


async def build_answer(result: List[dict[str, Any]], human_query: str) -> str | None:
    system_message = f"""
    Given a user's question and the SQL rows response from the database from which the user wants to get the answer,
    write a response to the user's question.
    <user_question>
    {human_query}
    </user_question>
    <sql_response>
    {result}
    </sql_response>
    """
    model = agent
    response = model.generate_content(system_message)
    return response.text


