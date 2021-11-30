r"""
Util functions
"""
from datetime import datetime, timedelta


def is_business_day(date_) ->bool:
    """
    Holidays: weekends, christmas and new year
    :param date_:
    :return: bool
    """
    is_holiday = date_.weekday() >= 5 or (date_.month == 1 and date_.day == 1) or \
        (date_.month == 12 and date_.day == 25)

    return not is_holiday


def next_business_day(date_str) ->str:
    """
    get the next business date of date_str
    :param date_str:
    :return:
    """
    _date = datetime.strptime(date_str, '%Y/%m/%d')
    one_more_day = timedelta(days=1)
    next_date = _date + one_more_day
    while not is_business_day(next_date):
        next_date = next_date + one_more_day
    return next_date.strftime('%Y/%m/%d')


def traverse_complex_data(data, func):
    """
    traverse the data structure and run func on the leaf node
    :param data: input data to traverse
    :param func: function to run on leaf node
    :return: None
    """
    if isinstance(data, dict):
        for _value in data.values():
            traverse_complex_data(_value, func)
    elif isinstance(data, (list, tuple)):
        for _value in data:
            traverse_complex_data(_value, func)
    else:
        func(data)


def traverse_process_complex_data(data, processor):
    """
    traverse the data structure, run processor and replace leaf node
    :param data: input data
    :param processor: function to run on and replace leaf node
    :return: processed data
    """
    if isinstance(data, dict):
        return {key: traverse_process_complex_data(value, processor) for key, value in data.items()}
    elif isinstance(data, (list, tuple)):
        return [traverse_process_complex_data(i, processor) for i in data]
    else:
        return processor(data)
