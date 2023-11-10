from fastapi import APIRouter, Query
from db import Connector, Fields, Passenger, PlaneModel, Tables, Alias
from additional import make_json
import os


__all__ = "info_router",


info_router = APIRouter(prefix="/about")
tags = ["about"]
connector = Connector.get(dbase="WebAirlines", password=os.environ["PASSWORD"])
print(connector)


@info_router.get("/planes", tags=tags)
def get_planes():
    with connector as conn:
        resp = conn.select(what=[PlaneModel.model, Passenger.first_name, Passenger.last_name],
                           from_=[PlaneModel.name, Passenger.name]
                           ).filter((Passenger.first_name != "Daniel") | (PlaneModel.model == "737"))
        print(resp)
    return make_json(status=200, desc="Planes found!", resp=resp.response)
