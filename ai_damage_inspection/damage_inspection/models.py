from pydantic import BaseModel, Field
from typing import Literal


class Point(BaseModel):
    x: float
    y: float


class Rectangle(BaseModel):
    bottom_left: Point
    top_right: Point


class DamageDetection(BaseModel):
    name: str
    damage_type: Literal[
        "O", "MS", "T", "ST", "SL", "S", "RU", "R", "PC", "P",
        "M", "L", "G", "FF", "F", "D", "CR", "C", "BR", "BB", "B"
    ]
    rectangle: Rectangle
