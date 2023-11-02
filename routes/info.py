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
        resp = conn.select(what=Fields(PlaneModel.model), from_=Tables(PlaneModel.name,
                                                          Alias(name=PlaneModel.name, alias='model2'),
                                                          Alias(name=PlaneModel.name, alias='model3')))
        print(resp)
    return make_json(status=200, desc="Planes found!", resp=resp.response)
