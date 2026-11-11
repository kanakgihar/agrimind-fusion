import re

from fastapi import Header, HTTPException


def get_session_id(x_session_id: str | None = Header(default=None)) -> str | None:
    if x_session_id is None:
        return None
    if not re.fullmatch(r"[A-Za-z0-9_-]{8,64}", x_session_id):
        raise HTTPException(400, "Invalid X-Session-Id header.")
    return x_session_id
