from __future__ import annotations
from typing import Generic, Iterable, TypeVar

from pydantic import BaseModel, field_validator

from datetime import datetime

class FunctionCall(BaseModel):
    run_id: str
    call_id: str


class FunctionCallStatus(BaseModel):
    requested_at: datetime | None = None
    responded_at: datetime | None = None
    approved: bool | None = None
    comment: str | None = None
    reject_option_name: str | None = None
    slack_message_ts: str | None = None


class AgentStore:
    """
    allows for creating and checking the status of
    """

    def add(self, item: FunctionCall) -> FunctionCall:
        raise NotImplementedError()

    def get(self, call_id: str) -> FunctionCall:
        raise NotImplementedError()

    def respond(self, call_id: str, status: FunctionCallStatus) -> FunctionCall:
        raise NotImplementedError()


class AgentBackend:
    def functions(self) -> AgentStore:
        raise NotImplementedError()
