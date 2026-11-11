from fastapi import APIRouter, HTTPException, Query
from fastapi.concurrency import run_in_threadpool

from app.services import risk_engine, weather_service

router = APIRouter(prefix="/api/weather", tags=["weather"])


def _wrap(fn, *args):
    try:
        return fn(*args)
    except weather_service.WeatherError as e:
        raise HTTPException(502, str(e))
    except ValueError as e:
        raise HTTPException(422, str(e))


@router.get("/geocode")
async def geocode(q: str = Query(min_length=2, max_length=80)):
    return {"results": await run_in_threadpool(_wrap, weather_service.geocode, q)}


@router.get("")
async def weather(lat: float = Query(ge=-90, le=90), lon: float = Query(ge=-180, le=180)):
    data = await run_in_threadpool(_wrap, weather_service.forecast, lat, lon)
    c = data["current"]
    today = data["daily"][0] if data["daily"] else {}
    data["current_risk"] = risk_engine.assess(c["temperature_c"], c["humidity_pct"],
                                              today.get("precipitation_mm"), c["soil_moisture"])
    for d in data["daily"]:
        d["risk"] = risk_engine.assess(d["temp_mean"], d["humidity_mean"], d["precipitation_mm"], d["soil_moisture_mean"])
        if d["risk"]:  # keep payload small
            d["risk"] = {"category": d["risk"]["category"], "score": d["risk"]["score"], "stress_flags": d["risk"]["stress_flags"]}
    return data


@router.get("/history")
async def history(lat: float = Query(ge=-90, le=90), lon: float = Query(ge=-180, le=180),
                  start: str = Query(pattern=r"^\d{4}-\d{2}-\d{2}$"), end: str = Query(pattern=r"^\d{4}-\d{2}-\d{2}$")):
    return await run_in_threadpool(_wrap, weather_service.history, lat, lon, start, end)
