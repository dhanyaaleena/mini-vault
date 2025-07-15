
from pydantic import BaseModel


class CodeRequest(BaseModel):
    email: str
    device_id: str
    
class VerifyCodeRequest(BaseModel):
    code:str
    device_id:str

class ShareFileRequest(BaseModel):
    file_id: str
    email: str
