import pydantic as pd
from datetime import datetime


__all__ = "SeatMap", "PlaneModel"


class SeatMap(pd.BaseModel):
    economy: int = pd.Field(default=0, ge=0)
    business: int = pd.Field(default=0, ge=0)
    first: int = pd.Field(default=0, ge=0)


class PlaneModel(pd.BaseModel):
    manufacturer: str
    model: str
    mf_year: int = pd.Field(ge=1970, le=datetime.now().year)

