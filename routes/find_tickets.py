from datetime import datetime
from fastapi import APIRouter, Query
import typing as tp
from additional import make_json
from enum import Enum
from db import Connector
import os


__all__ = "search_router",

search_router = APIRouter(prefix="/search")
tags = ["search"]
connector = Connector.get(dbase="WebAirlines", password=os.environ["PASSWORD"])

print(connector)

class Cabin(Enum):
    ECONOMY = "Y"
    BUSINESS = "C"


@search_router.get("/tickets", tags=tags)
def find_tickets(adults: tp.Annotated[int, Query(ge=0, le=10, description="Amount of tickets for adults")],
                 cabin: tp.Annotated[Cabin, Query(description="Class")],
                 depcity: tp.Annotated[str, Query(description="Departure city")],
                 arrcity: tp.Annotated[str, Query(description="Arrival city")],
                 date: tp.Annotated[tp.Union[datetime], Query()]):

    if depcity.lower() == arrcity.lower():
        return make_json(status=422, desc="Departure city must not be equal to arrival city")








