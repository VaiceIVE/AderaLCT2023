from pydantic import BaseModel

class ICriteria(BaseModel):
    obj: str
    work: str
    date: list

class ICriteriaURL(BaseModel):
    obj: str
    work: str
    date: list
    files: dict