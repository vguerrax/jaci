from fastapi.templating import Jinja2Templates
from app.utils.datetime import format_local_datetime, format_local_date

# Create templates instance once
templates = Jinja2Templates(directory="app/templates")

# Register filters
def localdatetime_filter(dt, fmt="%d/%m/%Y %H:%M"):
    return format_local_datetime(dt, fmt)

def localdate_filter(dt, fmt="%d/%m/%Y"):
    return format_local_date(dt, fmt)


def quantity_filter(value):
    return f"{value:.3f}".rstrip("0").rstrip(".")


templates.env.filters["localdatetime"] = localdatetime_filter
templates.env.filters["localdate"] = localdate_filter
templates.env.filters["quantity"] = quantity_filter
