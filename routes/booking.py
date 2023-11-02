from fastapi import APIRouter, Query
from db import Connector
import typing as tp


__all__ = "booking_router",

booking_router = APIRouter(prefix="/book")

