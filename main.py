from fastapi import FastAPI, Path, Query, Body
import typing as tp
import uvicorn
import enum
import os
from starlette.responses import JSONResponse
from db import Connector, ExecutionResponse
from schemes import PlaneModel, SeatMap


class Cabin(enum.Enum):
    ECONOMY = "economy"
    BUSINESS = "business"
    FIRST = "first"


WebAirlineApp = FastAPI()
Connector.set_global_password(os.getenv("PASSWORD"))
WebAirlinesDB = Connector.get(dbase="WebAirlines")


@WebAirlineApp.get("/")
async def root():
    return {"Welcome": "Hi"}


@WebAirlineApp.get("/search")
def search_ticket(adults: tp.Annotated[int, Query(ge=1, le=10)], children: tp.Annotated[int, Query(ge=1, le=10)],
                  cabin: tp.Annotated[Cabin, Query()],
                  route: tp.Annotated[str, Query()]):
    return JSONResponse({"route": route})

# routes=ABA.20231019.AUH


@WebAirlineApp.get("/planes")
def get_planes() -> JSONResponse:
    with WebAirlinesDB() as connector:
        res = connector.execute("select * from airplane;")
    return JSONResponse({'result': res})


@WebAirlineApp.post("/planes/add")
async def add_record(data: PlaneModel) -> JSONResponse:
    with WebAirlinesDB() as connector:
        res: ExecutionResponse = connector.insert(into="Airplane",
                         fields=("mf", "model", "mf_year"),
                         values=(data.manufacturer, data.model, str(data.mf_year)))

    if res.error is not None:
        return JSONResponse({"status": 0, "data": res.error})
    return JSONResponse({"status": 200, "data": data.json()})


@WebAirlineApp.post("/tickets/{cabin_id}")
async def tickets(cabin_id: int, item: tp.Annotated[SeatMap, Body(embed=True)]):
    return JSONResponse({"cabin_id": cabin_id, "item": item.json()})


if __name__ == "__main__":
    uvicorn.run(WebAirlineApp, host="192.168.68.151", port=8000)

'''
# {"manufacturer": "Boeing", "model": "737 MAX", "seatmap": {"economy": 135, "business": 20}, "mf_year": 2017}
uvicorn.run(app)'''

# psql -p 9090 -U dankosmynin -d WebAirlines
'''
    create table seatmap(
    id serial primary key,
    economy integer default 0,
    business integer default 0,
    first integer default 0
    
    insert into seatmap(economy, business, first) values (144, 29, 0);
'''
