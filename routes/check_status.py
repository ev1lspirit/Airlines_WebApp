from fastapi import APIRouter, Query
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from db import Connector, Ticket, Booking, Flight
import typing as tp
import pydantic as pd
from dataclasses import dataclass
import os


__all__ = "status_router",

status_router = APIRouter(prefix="/info")
connector = Connector.get(dbase="WebAirlines", password=os.environ["PASSWORD"])
status_router.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")
templates = Jinja2Templates(directory="templates")
tags = ["info"]


@status_router.get("/booking/find", tags=tags)
def find_booking(pnr: tp.Annotated[str, Query(max_length=13, description="Airline PNR, booking code")],
                 passport: tp.Annotated[int, Query(description="last name of a passenger")]):
    response = {}
    with connector as conn:
        pnr = conn.select(what=[Booking.pnr],
                          from_=[Booking.name]).filter(
            (Booking.pnr == pnr) & (Booking.holder_passport == passport))

        if pnr.response:
            response.update({"pnr": pnr.response[0]})
        else:
            return JSONResponse({"status": 500})

        flight_info = conn.select(what=["*"],
                                  from_=[Flight.join(Ticket).on(Flight.airplane == Ticket.filght_no)])\
            .filter(Ticket.pnr == pnr.response[0][0])

        if flight_info.response:
            response["tickets"] = []
            arrd = {}
            arrd["airport"] = flight_info.response[0][0]
            arrd["hometown"] = flight_info.response[0][1]
            arrd["destination"] = flight_info.response[0][2]
            arrd["dep_date"] = flight_info.response[0][3].strftime("%d %b")
            arrd["arr_date"] = flight_info.response[0][4].strftime("%d %b")
            arrd["dep_time"] = flight_info.response[0][5].strftime("%H:%M")
            arrd["arr_time"] = flight_info.response[0][6].strftime("%H:%M")
            arrd["seat"] = flight_info.response[0][10]
            arrd["row"] = flight_info.response[0][11]
            arrd["type"] = flight_info.response[0][12]
            response["tickets"].append(arrd)

        else:
            return JSONResponse({"status": 500})

    return JSONResponse(response)


@status_router.get("/flight/status", tags=tags)
def get_status(request: Request):
    return templates.TemplateResponse("find_booking.html", {"request": request})
