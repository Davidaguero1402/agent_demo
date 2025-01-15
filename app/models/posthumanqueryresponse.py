from pydantic import BaseModel

class PostHumanQueryResponse(BaseModel):
    answer: str