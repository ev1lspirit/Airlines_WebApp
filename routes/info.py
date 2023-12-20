from fastapi import APIRouter
from db import Connector, Passenger, PlaneModel
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import os


__all__ = "info_router",


info_router = APIRouter(prefix="/about")
tags = ["about"]
connector = Connector.get(dbase="WebAirlines", password=os.environ["PASSWORD"])

# info_router.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
print(connector)


@info_router.get("/planes", tags=tags, response_class=HTMLResponse)
def get_planes(request: Request):

    with connector as conn:
        planes = conn.select(what=[PlaneModel.model, PlaneModel.manufacturer,
                                   PlaneModel.maxdistance, PlaneModel.maxaltitude],
                           from_=[PlaneModel.name])()

    return templates.TemplateResponse("planes.html", {"request": request, "planes": planes.response})
