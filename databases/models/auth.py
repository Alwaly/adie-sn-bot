from pydantic import BaseModel
from typing import List
class Auth(BaseModel):
    email: str
    password: str

class SendLinkPassword(BaseModel):
    email: str

class Entity(BaseModel):
    name: str
    type: str

class Document_Content(BaseModel):
    fict_id: str
    value: str

class Entity_create(Entity):
    owners : List[str]
    unused_token : int

class ResetPassword(BaseModel):
    newPassword: str

class Chat(BaseModel):
    role:str
    content: str

class Message(BaseModel):
    content: str

class Register(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    unused_token : int
    account_type: str
    historique: List[Chat] = []