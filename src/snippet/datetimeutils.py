from datetime import datetime, time


def get_today_midnight_rfc_string():
    today = datetime.combine(datetime.today().date(), time.min)
    return today.isoformat() + 'Z'  # UTC
