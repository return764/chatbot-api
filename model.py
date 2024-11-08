from typing import List, Literal, Optional, Union, Any
from pydantic import BaseModel, ConfigDict, Field, model_validator
import json

class MessageData(BaseModel):
    type: str
    data: dict

class Sender(BaseModel):
    user_id: int
    nickname: str
    card: Optional[str] = None
    role: Optional[str] = None

class Anonymous(BaseModel):
    id: int
    name: str
    flag: str

class BasicMessage(BaseModel):
    time: int
    self_id: int
    post_type: Literal["message", "message_sent", "request", "notice", "meta_event"]
    
    model_config = ConfigDict(extra='allow')
    
    @classmethod
    def model_validate_json(cls, json_data: Union[str, bytes, bytearray]) -> Any:
        if isinstance(json_data, (bytes, bytearray)):
            data = json.loads(json_data.decode())
        else:
            data = json.loads(json_data)
            
        post_type = data.get('post_type')
        message_type = data.get('message_type')
        
        if post_type == 'message' and message_type == 'group':
            return GroupMessage.model_validate(data)
        elif post_type == 'message' and message_type == 'private':
            return PrivateMessage.model_validate(data)
        elif post_type == 'request':
            return RequestReport.model_validate(data)
        elif post_type == 'notice':
            return NoticeReport.model_validate(data)
        elif post_type == 'meta_event':
            return MetaEventReport.model_validate(data)
        
        return cls.model_validate(data)

class MessageReport(BasicMessage):
    message_type: Literal["group", "private"]
    sub_type: str
    message_id: int = Field(..., alias="message_id")
    user_id: int
    message: List[MessageData]
    raw_message: str
    font: int
    sender: Sender

class RequestReport(BasicMessage):
    request_type: str

class NoticeReport(BasicMessage):
    notice_type: str

class MetaEventReport(BasicMessage):
    meta_event_type: str

class GroupMessage(MessageReport):
    group_id: int
    anonymous: Optional[Anonymous] = None

class PrivateMessage(MessageReport):
    target_id: Optional[int] = None
    temp_source: Optional[int] = None