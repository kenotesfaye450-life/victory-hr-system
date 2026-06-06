from ethiopian_date import EthiopianDateConverter
from datetime import date

converter = EthiopianDateConverter()

def ethiopian_to_gregorian(year, month, day):
    try:
        greg = converter.to_gregorian(int(year), int(month), int(day))
        # greg is a tuple (year, month, day)
        return date(greg[0], greg[1], greg[2])
    except Exception:
        return None

def gregorian_to_ethiopian(greg_date):
    if not greg_date or not isinstance(greg_date, date):
        return None
    try:
        result = converter.to_ethiopian(greg_date.year, greg_date.month, greg_date.day)
        # result could be a tuple or a date object
        if hasattr(result, 'year'):  # it's a date object
            return (result.year, result.month, result.day)
        else:  # it's a tuple
            return (result[0], result[1], result[2])
    except Exception:
        return None

def format_ethiopian_date(greg_date):
    eth = gregorian_to_ethiopian(greg_date)
    if eth:
        return f"{eth[0]}-{eth[1]:02d}-{eth[2]:02d}"
    return ""

def parse_ethiopian_date(eth_date_str):
    if not eth_date_str:
        return None
    try:
        parts = eth_date_str.split('-')
        year, month, day = map(int, parts)
        return ethiopian_to_gregorian(year, month, day)
    except Exception:
        return None