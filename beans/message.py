from typing import TypedDict, Literal, Optional


class Message(TypedDict, total=False):
    _id: str
    timestamp: str
    type: Literal["text", "image"]
    senderId: str
    recipientId: str
    content: str
    viewd: Optional[bool]


class MessagePayload(TypedDict):
    sessionId: str
    message: Message
