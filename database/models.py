from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    user_id: int
    username: Optional[str] = None


@dataclass
class Workshop:
    id: int
    name: str
    code: str


@dataclass
class Project:
    id: int
    name: str
    code: str
