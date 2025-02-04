import sqlparse

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