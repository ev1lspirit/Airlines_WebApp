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

    pnr_query = BookingQueries.FIND_PNR.format(fields="*", clause=f"pnr = '{pnr}'")
    last_name_query = PassengerQueries.FIND_TEMPLATE
    last_name_match = None

    with connector as conn:
        pnr_response = conn.select(pnr_query)
        if pnr_response:
            pnr, passport = pnr_response
            last_name_query.format(fields="last_name", clause=f"passport = {passport}")
            last_name_match = conn.select(last_name_query)

    if not pnr_response:
        return make_json(status=422, desc="PNR not found!")

    if last_name_match != last_name.capitalize():
        return make_json(status=422, desc="Last name doesn't match")

    return make_json(status=200, desc="PNR found!", resp=pnr)


@status_router.get("/flight/status", tags=tags)
def get_status(flight_no: tp.Annotated[str, Query(max_length=8, description="flight number")]):
    pass
