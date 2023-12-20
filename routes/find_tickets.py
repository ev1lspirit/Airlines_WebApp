import datetime
import itertools
from collections import defaultdict

from fastapi import APIRouter, Query, Form, Depends
import typing as tp

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles
from db import Flight, Airport
import pydantic as pd
from enum import Enum
from db import Connector
import os
from fastapi.templating import Jinja2Templates
from fastapi_pagination import Page, Params, paginate


__all__ = "search_router",

search_router = APIRouter(prefix="/search")
tags = ["search"]

search_router.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")
templates = Jinja2Templates(directory="templates")

connector = Connector.get(dbase="WebAirlines", password=os.environ["PASSWORD"])
print(connector)


class Cabin(Enum):
    ECONOMY = "Economy"
    ECONOMY_PLUS = "Economy+"
    BUSINESS = "Business"


@search_router.get("/tickets")
def search_tickets_handler(request: Request):
    return templates.TemplateResponse("tickets.html", {"request": request})


class Data(pd.BaseModel):
    hometown: str
    destination: str
    cabintype: str
    departure_date: str


def get_datetime(date_str: str):
    if not date_str:
        return datetime.datetime.now()

    date_format = '%Y-%m-%d'
    date = datetime.datetime.strptime(date_str, date_format)
    return date


class FlightModel(pd.BaseModel):
    id: int
    home_code: str
    dest_code: str
    dep_date: str
    arr_date: str
    dep_time: str
    arr_time: str
    flight_no: int


def json_tickets(response):
    output = defaultdict(dict)
    for collection in response:
        child = dict()
        print(collection)
        child["home_ap"] = collection[1]
        child["dest"] = collection[2]
        child["dep"] = collection[3].strftime("%d/%m/%Y")
        child["arr"] = collection[4].strftime("%d/%m/%Y")
        child["dep_time"] = collection[5].strftime("%H:%M:%S")
        child["arr_time"] = collection[6].strftime("%H:%M:%S")
        child["flight_no"] = collection[7]
        output[child["flight_no"]] = child
    return output


def get_airport_tag_condition(response, tag):
    tag_or = tag == response[0][0]
    if len(response) > 1:
        for collection in itertools.islice(response, 1, None):
            tag_or |= (tag == collection[0])

    return tag_or


shared = {}


@search_router.get("/xwings/tickets/available", response_model=Page[FlightModel], tags=tags)
def get_list_of_tickets(params: Params = Depends()):
    print(shared)
    if "flight_search" not in shared:
        return JSONResponse({})
    return paginate(shared["flight_search"], params)


@search_router.get("/xwings/tickets/", tags=tags)
def find_tickets(hometown: tp.Annotated[str, Query()], destination: tp.Annotated[str, Query()],
                departure_date: tp.Annotated[str, Query()],
                cabin_type: tp.Annotated[str, Query()], request: Request):

    found_fligts = []

    with connector as conn:
        home_airport = conn.select(what=[Airport.alias], from_=[Airport.name]).filter(Airport.city == hometown)
        dest_airport = conn.select(what=[Airport.alias], from_=[Airport.name]).filter(Airport.city == destination)

        if home_airport.error is not None or dest_airport.error is not None:
            return

        home_airport_tag_condition = get_airport_tag_condition(home_airport.response, Flight.departureairport)
        destination_airport_tag_condition = get_airport_tag_condition(dest_airport.response, Flight.arrivalairport)

        flights = conn.select(what=["*"], from_=[Flight.name]).filter((Flight.departuredate == departure_date)
                                                & (home_airport_tag_condition & destination_airport_tag_condition))

        print(flights.response)
        for flight in flights.response:
            found_fligts.append(FlightModel(
                id=flight[0],
                home_code=flight[1],
                dest_code=flight[2],
                dep_date=flight[3].strftime("%d %b"),
                arr_date=flight[4].strftime("%d %b"),
                dep_time=flight[5].strftime("%H:%M"),
                arr_time=flight[6].strftime("%H:%M"),
                flight_no=flight[7]
            ))
    print("flight_search is set")
    shared["flight_search"] = found_fligts
    print(shared)

    return templates.TemplateResponse("found_tickets.html", {"request": request, "flights": found_fligts})










