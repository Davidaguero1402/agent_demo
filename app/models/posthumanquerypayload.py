from pydantic import BaseModel

class PostHumanQueryPayload(BaseModel):
    human_query: str