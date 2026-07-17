"""Enumerated values persisted by the database models."""

from enum import Enum


class Role(str, Enum):
    ADMINISTRATOR = "ADMINISTRATOR"
    ENGINEER = "ENGINEER"


class TargetType(str, Enum):
    ROOM = "ROOM"
    OTHER = "OTHER"


class Category(str, Enum):
    LIGHTING = "LIGHTING"
    SHADE = "SHADE"
    KEYPAD = "KEYPAD"
    SENSOR = "SENSOR"
    TSTAT = "TSTAT"
    PROCESSOR = "PROCESSOR"
    NETWORK = "NETWORK"
    SERVER = "SERVER"
    INTEGRATION = "INTEGRATION"
    OTHER = "OTHER"


class Status(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
