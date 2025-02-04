from typing import Any
from app import agent

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

