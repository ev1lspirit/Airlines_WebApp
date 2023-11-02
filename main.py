from fastapi import FastAPI
import uvicorn
from db import ExecutionResponse, Connector
import routes
from auth import auth_router


# psql -p 9090 -U dankosmynin -d WebAirlines

WebAirlineApp = FastAPI()
WebAirlinesDB = Connector.get(dbase="WebAirlines")


WebAirlineApp.include_router(routes.search_router)
WebAirlineApp.include_router(routes.status_router)
WebAirlineApp.include_router(routes.info_router)
WebAirlineApp.include_router(routes.booking_router)
WebAirlineApp.include_router(auth_router)


@WebAirlineApp.get("/")
def root():
    return {"Welcome": "Hi"}


@WebAirlineApp.get('/admin/db')
def get_db():
    with WebAirlinesDB as conn:
        resp: ExecutionResponse = conn.select(query="SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
    return {"resp": resp.response}


if __name__ == "__main__":
    uvicorn.run(WebAirlineApp, host="192.168.68.151", port=8000)


