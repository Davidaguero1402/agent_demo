from app import agent
import json
from .utils_schema import get_schema
from .controlers import query, clean_json_response
from .utils_validate import validate_sql_query
async def human_query_to_sql(human_query: str, max_attempts: int = 3) -> str | None:
    database_schema = get_schema()
    attempts = 0

    while attempts < max_attempts:
        # Paso 1: Generar consulta SQL
        system_message = f"""
        Given the following schema, write a SQL query that retrieves the requested information. 
        Return the SQL query inside a JSON structure with the key "sql_query".
        Only use columns that exist in the schema.
        <example>{{"sql_query": "SELECT * FROM users WHERE age > 18;", "original_query": "Show me all users older than 18 years old."}}</example>
        <schema>
        {json.dumps(database_schema, indent=2)}
        </schema>
        """
        response = await agent.generate_content(system_message + human_query)
        cleaned_response = clean_json_response(response.text)

        try:
            response_json = json.loads(cleaned_response)
            sql_query = response_json.get("sql_query")

            # Paso 2: Validar consulta SQL
            if sql_query and validate_sql_query(sql_query, database_schema):
                # Paso 3: Ejecutar consulta SQL
                result = query(sql_query)

                # Paso 4: Verificar si hay resultados
                if result:
                    return sql_query
                else:
                    # Paso 5: Pedir al modelo que revise y regenere la consulta
                    human_query = "La consulta SQL no devolvió resultados. Por favor, revisa y regenera la consulta SQL."
            else:
                # Paso 5: Pedir al modelo que revise y regenere la consulta
                human_query = "La consulta SQL generada no es válida. Por favor, revisa y regenera la consulta SQL."
        except json.JSONDecodeError:
            human_query = "La respuesta del modelo no es válida. Por favor, revisa y regenera la consulta SQL."

        attempts += 1

    # Si se supera el límite de intentos, devolver un error
    raise ValueError("No se pudo generar una consulta SQL válida después de varios intentos.")