from pydantic import BaseModel
from bson.objectid import ObjectId

class IResult(BaseModel):
    result: list
    type: str
    criterias: list
    date: str
    id: str
    def ToDict(this):
        return dict({"result": this.result, "type": this.type, "criterias": this.criterias, "date": this.date, "id": ObjectId(this.id)})
        