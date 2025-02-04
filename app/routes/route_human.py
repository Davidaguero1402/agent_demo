from app import app
from ..models.posthumanquerypayload import PostHumanQueryPayload
from ..models.posthumanqueryresponse import PostHumanQueryResponse

from ..services.utils_human_query import human_query_to_sql
from ..services.utils_build_answer import build_answer
from ..services.utils_query import query
from fastapi import HTTPException



@app.post("/human_query", response_model=PostHumanQueryResponse)
async def human_query(payload: PostHumanQueryPayload):
    sql_query = await human_query_to_sql(payload.human_query)
    if not sql_query:
        raise HTTPException(status_code=400, detail="No se pudo generar una consulta SQL válida")
    print(f"Generated SQL query: {sql_query}")  # Agregar esta línea
    result = query(sql_query)
    if result is None:
        raise HTTPException(status_code=500, detail="Error al ejecutar la consulta SQL")
    print(f"Query result: {result[:5]}")  # Agregar esta línea para ver los primeros 5 resultados
    answer = await build_answer(result, payload.human_query)
    if not answer:
        raise HTTPException(status_code=500, detail="No se pudo generar una respuesta")
    return {"answer": answer}
