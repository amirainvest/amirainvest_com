from pydantic import BaseModel

class ReportPostModel(BaseModel):
    post_id: int

