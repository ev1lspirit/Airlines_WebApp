from fastapi import APIRouter, Query
from additional import make_json
from db import Connector
import typing as tp
from dataclasses import dataclass
import os


__all__ = "status_router",

connector = Connector.get(dbase="WebAirlines", password=os.environ["PASSWORD"])
status_router = APIRouter(prefix="/info")
tags = ["info"]

print(connector)


@dataclass(frozen=True)
class BookingQueries:
    FIND_PNR = """SELECT {fields} FROM booking WHERE {clause};"""


@dataclass(frozen=True)
class PassengerQueries:
    FIND_TEMPLATE = """SELECT {fields} FROM Passenger WHERE {clause};"""


@status_router.get("/booking/find", tags=tags)
def find_booking(pnr: tp.Annotated[str, Query(max_length=7, description="Airline PNR, booking code")],
                 last_name: tp.Annotated[str, Query(description="last name of a passenger")]):

    with connector as conn:
        pass


@status_router.get("/flight/status", tags=tags)
def get_status(flight_no: tp.Annotated[str, Query(max_length=8, description="flight number")]):
    pass
