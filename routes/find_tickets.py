import datetime
import itertools
from collections import defaultdict
from functools import wraps
from random import random, choice

from fastapi import APIRouter, Query, Form, Depends
import typing as tp

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles
from db import (
    Flight,
    Airport,
    Service,
    Passenger,
    Booking,
    Seat,
    Ticket,
    TicketService
)
import pydantic as pd
from enum import Enum
from db import Connector
import os
from fastapi.templating import Jinja2Templates
from fastapi_pagination import Page, Params, paginate


__all__ = "search_router",

from db.models import Field

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
async def search_tickets_handler(request: Request):
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


@search_router.get("/xwings/none")
def none(request: Request):
    return templates.TemplateResponse("nothing.html", {"request": request})


@search_router.get("/xwings/failed")
def failed(request: Request):
    return templates.TemplateResponse("not_successful.html", {"request": request})


@search_router.get("/xwings/tickets/seatmap")
async def seatmap(request: Request):
    return templates.TemplateResponse("seatmap.html", {"request": request})


@search_router.get("/xwings/tickets/passenger_info")
async def get_passenger_info(request: Request, flight_no: tp.Annotated[int, Query()], hometown: tp.Annotated[str, Query()],
                       destination: tp.Annotated[str, Query()],
                departure_date: tp.Annotated[str, Query()],
                cabin_type: tp.Annotated[str, Query()], alcohol: tp.Annotated[str, Query()],
                       pets: tp.Annotated[str, Query()]):
    print("hello!")
    return templates.TemplateResponse("passenger_info.html", {"request": request})


@search_router.get("/xwings/tickets/services/")
async def services_handle(flight_no: tp.Annotated[int, Query()], hometown: tp.Annotated[str, Query()], destination: tp.Annotated[str, Query()],
                departure_date: tp.Annotated[str, Query()],
                cabin_type: tp.Annotated[str, Query()], request: Request):
    return templates.TemplateResponse("services.html", {"request": request})


@search_router.get("/xwings/tickets/available", response_model=Page[FlightModel], tags=tags)
async def get_list_of_tickets(params: Params = Depends()):
    print(shared)
    if "flight_search" not in shared:
        return JSONResponse({})
    return paginate(shared["flight_search"], params)


@search_router.get("/xwings/tickets/", tags=tags)
async def find_tickets(hometown: tp.Annotated[str, Query()], destination: tp.Annotated[str, Query()],
                departure_date: tp.Annotated[str, Query()], request: Request):
    found_fligts = []
    with connector as conn:
        home_airport = conn.select(what=[Airport.alias], from_=[Airport.name]).filter(Airport.city == hometown)
        dest_airport = conn.select(what=[Airport.alias], from_=[Airport.name]).filter(Airport.city == destination)

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


class AppliedServices(pd.BaseModel):
    pets: bool
    alcohol: bool
    meal: bool


class TicketMetadata(pd.BaseModel):
    name: str
    passport: int
    hometown: str
    email: str
    phone: str
    birth_date: str
    destination: str
    cabin_type: str
    flight_no: int
    departure_date: str
    sex: str
    services: AppliedServices


def generate_pnr_code():
    data = [*range(10), *(chr(letter) for letter in range(65, 90))]
    return "".join(str(choice(data)) for _ in range(13))


def insert_validator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        query_resp = func(*args, **kwargs)
        if not query_resp:
            return None
        if not query_resp.response:
            return None
        return query_resp.response
    return wrapper


@insert_validator
def try_insert_passenger(data):
    with connector as conn:
        passenger = conn.select(what=['1'], from_=[Passenger.name]).filter(Passenger.passport == data.passport)
        first_name, last_name = data.name.split()
        if not passenger.response:
            query_resp = conn.insert(into=Passenger.name,
                                     values=[data.passport, first_name, last_name, data.birth_date, data.phone])
        else:
            return passenger
    return query_resp


@insert_validator
def check_pnr_equals_two(passport):
    with connector as conn:
        query_resp = conn.select(what=[f"COUNT({Booking.pnr.value})"], from_=[Booking.name]).filter(Booking.holder_passport == passport)
    return query_resp


def create_pnr(holder_passport):
    pnr = generate_pnr_code()
    pnr_count = check_pnr_equals_two(holder_passport)
    print("pnr_count", pnr_count)
    if not pnr_count:
        return None

    pnr_count = pnr_count[0][0]
    if pnr_count >= 1:
        return None

    with connector as conn:
         conn.insert(into=Booking.name,
                        values=[pnr, holder_passport])
    return pnr


@insert_validator
def available_seats_exist(cabin_type, flight_no):
    print("SELECT seatno, rowno, title from Seat where Seat.title = '{cabin_type}') EXCEPT (select Ticket.seatno,Ticket.rowno, "
                                   "Ticket.title from Ticket where Ticket.filght_no = {flight_no}) "
                                   "limit 1;".format(flight_no=flight_no, cabin_type=cabin_type))
    with connector as conn:
        seats = conn._select(query="(SELECT seatno, rowno, title from Seat where Seat.title = '{cabin_type}') EXCEPT (select Ticket.seatno,Ticket.rowno, "
                                   "Ticket.title from Ticket where Ticket.filght_no = {flight_no}) "
                                   "limit 1;".format(flight_no=flight_no, cabin_type=cabin_type))
        print(seats)
    return seats


def insert_ticket(pnr, seat, flight_no):
    def generate_ticket_no():
        data = range(13)
        result = []
        for _ in range(7):
            result.append(str(choice(data)))
        return int("".join(result))

    seatno, rowno, title = seat
    ticketno = generate_ticket_no()
    with connector as conn:
        query_resp = conn.insert(into=Ticket.name, values=[ticketno, pnr, seatno, rowno, title, flight_no])

    if query_resp.error is None:
        return ticketno
    raise TypeError("Ticket wasn't created")


@insert_validator
def add_services(ticket, services: AppliedServices):
    with connector as conn:
        if services.meal is True:
            conn.insert(into=TicketService.name, values=[ticket, 1])
        if services.pets is True:
            conn.insert(into=TicketService.name, values=[ticket, 2])
        if services.alcohol is True:
            conn.insert(into=TicketService.name, values=[ticket, 3])


@search_router.post("/xwings/tickets/book_ticket", response_class=JSONResponse)
async def create_ticket(data: TicketMetadata):
    try_insert_passenger(data)
    seats = available_seats_exist(data.cabin_type, data.flight_no)
    print(seats)
    if not seats:
        return JSONResponse({"status": 500})

    pnr = create_pnr(data.passport)
    print(pnr)
    if not pnr:
        return JSONResponse({"status": 500})

    random_seat = seats[0]
    ticketno = insert_ticket(pnr, random_seat, data.flight_no)
    add_services(ticketno, data.services)
    return JSONResponse({"status": 200})









