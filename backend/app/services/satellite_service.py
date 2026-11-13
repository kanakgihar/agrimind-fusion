
"""Sentinel-2 (COPERNICUS/S2_SR_HARMONIZED) NDVI / NDMI time series via Google Earth Engine.

NDVI and NDMI are vegetation / moisture indicators for a field area,
NOT disease diagnoses.
"""
from app.config import settings

_ready = False


class SatelliteUnavailable(Exception):
    pass


def status() -> dict:
    try:
        import ee  # noqa: F401
        installed = True
    except ImportError:
        installed = False

    service_account_configured = bool(
        settings.ee_service_account
        and (settings.ee_private_key_json or settings.ee_key_file)
    )

    return {
        "earthengine_api_installed": installed,
        "project_configured": bool(settings.ee_project),
        "auth_mode": (
            "service account"
            if service_account_configured
            else "local user credentials (earthengine authenticate)"
        ),
        "collection": "COPERNICUS/S2_SR_HARMONIZED",
        "tested": False,
    }


def _init():
    global _ready

    if _ready:
        return

    try:
        import ee
    except ImportError as e:
        raise SatelliteUnavailable(
            "earthengine-api is not installed. Run: pip install earthengine-api"
        ) from e

    if not settings.ee_project:
        raise SatelliteUnavailable(
            "EE_PROJECT is not set in backend/.env "
            "(your Google Cloud project registered for Earth Engine)."
        )

    try:
        if settings.ee_service_account and settings.ee_private_key_json:
            creds = ee.ServiceAccountCredentials(
                settings.ee_service_account,
                key_data=settings.ee_private_key_json,
            )
            ee.Initialize(creds, project=settings.ee_project)

        elif settings.ee_service_account and settings.ee_key_file:
            creds = ee.ServiceAccountCredentials(
                settings.ee_service_account,
                settings.ee_key_file,
            )
            ee.Initialize(creds, project=settings.ee_project)

        else:
            ee.Initialize(project=settings.ee_project)

    except Exception as e:
        raise SatelliteUnavailable(
            f"Earth Engine initialisation failed: {e}"
        ) from e

    _ready = True


def _mask_clouds(img):
    scl = img.select("SCL")

    # 3 cloud shadow, 8/9 cloud medium/high probability,
    # 10 thin cirrus, 11 snow
    ok = (
        scl.neq(3)
        .And(scl.neq(8))
        .And(scl.neq(9))
        .And(scl.neq(10))
        .And(scl.neq(11))
    )

    return img.updateMask(ok)


def indices(
    lat: float,
    lon: float,
    start: str,
    end: str,
    radius_m: int = 200,
    max_cloud: int = 60,
) -> dict:
    _init()
    import ee

    geom = ee.Geometry.Point([lon, lat]).buffer(radius_m)

    col = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(geom)
        .filterDate(start, end)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", max_cloud))
    )

    def per_image(img):
        m = _mask_clouds(img)

        ndvi = m.normalizedDifference(["B8", "B4"]).rename("ndvi")
        ndmi = m.normalizedDifference(["B8", "B11"]).rename("ndmi")

        stats = ndvi.addBands(ndmi).reduceRegion(
            ee.Reducer.mean(),
            geom,
            20,
            maxPixels=1e8,
        )

        return ee.Feature(
            None,
            {
                "date": img.date().format("YYYY-MM-dd"),
                "cloud_pct": img.get("CLOUDY_PIXEL_PERCENTAGE"),
                "ndvi": stats.get("ndvi"),
                "ndmi": stats.get("ndmi"),
            },
        )

    feats = col.map(per_image).limit(60).getInfo()["features"]

    rows = [
        f["properties"]
        for f in feats
        if f["properties"].get("ndvi") is not None
    ]

    rows.sort(key=lambda r: r["date"])

    return {
        "observations": rows,
        "count": len(rows),
        "collection": "COPERNICUS/S2_SR_HARMONIZED",
        "radius_m": radius_m,
        "max_cloud_pct": max_cloud,
        "message": (
            None
            if rows
            else "No suitable cloud-free Sentinel-2 observation found "
                 "for this place and date range."
        ),
        "disclaimer": (
            "NDVI/NDMI are vegetation and moisture indicators "
            "for a field area, not disease diagnoses."
        ),
    }
