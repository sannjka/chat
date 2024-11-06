from pydantic import BaseModel, EmailStr


class Message(BaseModel):
    sender: EmailStr
    recipient: EmailStr
    content: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "sender": "fiona@mail.com",
                "recipient": "shrek@mail.com",
                "content": "What kind of knight are you?!",
            },
        }
    }

class MessageRead(Message):
    id: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 0,
                "sender": "fiona@mail.com",
                "recipient": "shrek@mail.com",
                "content": "What kind of knight are you?!",
            },
        }
    }
