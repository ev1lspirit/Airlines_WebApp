from fastapi import FastAPI, Response, File, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
import uvicorn
from db import Connector
from db.models import ExecutionResponse
import routes
from auth import auth_router
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


# psql -p 9090 -U dankosmynin -d WebAirlines

WebAirlineApp = FastAPI()
WebAirlinesDB = Connector.get(dbase="WebAirlines")

WebAirlineApp.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")
templates = Jinja2Templates(directory="templates")

WebAirlineApp.include_router(routes.search_router)
WebAirlineApp.include_router(routes.status_router)
WebAirlineApp.include_router(routes.info_router)
WebAirlineApp.include_router(routes.booking_router)
WebAirlineApp.include_router(auth_router)


@WebAirlineApp.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@WebAirlineApp.get("/earth_texture.jpg")
def get_texture():
    import os
    print(os.getcwd())
    return FileResponse("{cwd}/frontend/earth_texture.jpg".format(cwd=os.getcwd()))


@WebAirlineApp.get('/admin/db')
def get_db():
    with WebAirlinesDB as conn:
        resp: ExecutionResponse = conn.select(query="SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
    return {"resp": resp.response}


if __name__ == "__main__":
    uvicorn.run(WebAirlineApp, host="192.168.16.151", port=8000)


