from ethiopian_date import EthiopianDateConverter
from datetime import date

converter = EthiopianDateConverter()

def ethiopian_to_gregorian(year, month, day):
    """Convert Ethiopian date to Gregorian date object."""
    try:
        greg = converter.to_gregorian(int(year), int(month), int(day))
        return date(greg[0], greg[1], greg[2])
    except Exception as e:
        print(f"Error converting Ethiopian to Gregorian: {e}")
        return None

def gregorian_to_ethiopian(greg_date):
    """Convert Gregorian date to Ethiopian tuple (year, month, day)."""
    if not greg_date:
        return None
    try:
        eth = converter.to_ethiopian(greg_date.year, greg_date.month, greg_date.day)
        return (eth[0], eth[1], eth[2])
    except Exception as e:
        print(f"Error converting Gregorian to Ethiopian: {e}")
        return None

def format_ethiopian_date(greg_date):
    """Return string 'YYYY-MM-DD' in Ethiopian calendar."""
    if not greg_date:
        return ""
    eth = gregorian_to_ethiopian(greg_date)
    if eth:
        return f"{eth[0]}-{eth[1]:02d}-{eth[2]:02d}"
    return ""

def parse_ethiopian_date(eth_date_str):
    """Parse Ethiopian date string 'YYYY-MM-DD' and return Gregorian date object."""
    if not eth_date_str:
        return None
    try:
        parts = eth_date_str.split('-')
        if len(parts) != 3:
            return None
        year, month, day = map(int, parts)
        return ethiopian_to_gregorian(year, month, day)
    except Exception as e:
        print(f"Error parsing Ethiopian date: {e}")
        return None
