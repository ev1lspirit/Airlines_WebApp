from starlette.responses import JSONResponse


def make_json(*, status, desc, resp=None) -> JSONResponse:
    return JSONResponse({"status": status, "desc": desc, "resp": resp})