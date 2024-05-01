from datetime import datetime, timedelta

import sentinelhub
from sentinelhub import filter_times

import log

LOGGER = log.get_logger(__name__)
TIME_DIFFERENCE = timedelta(hours=1)


def Create_Month_Interval(year: int, month: int) -> tuple:
    """
    This function takes a year and month as input and Tuple from start of month and end of month.

    Args:
        year (int): Year value.
        month (int): Month value (1-12).

    Returns:
        List: List of tuples representing time intervals (start, end) for a month.
    """

    try:
        if month < 1 or month > 12:
            raise ValueError
        firstDay = datetime(year, month, 1)
        if month == 12:
            lastDay = firstDay + timedelta(days=(datetime(year + 1, 1, 1) - firstDay).days - 1)
        else:
            lastDay = firstDay + timedelta(days=(datetime(year, month + 1, 1) - firstDay).days - 1)

        return firstDay.replace(hour=0, minute=0, second=0).isoformat(), lastDay.replace(hour=23, minute=59,
                                                                                         second=59).isoformat()
    except ValueError as ve:
        LOGGER.warning(ve)
    except Exception as e:
        LOGGER.error(e)


def Create_One_Hour_Interval_On_Data(all_timestamps) -> list:
    unique_acquisitions = filter_times(all_timestamps, TIME_DIFFERENCE)
    return unique_acquisitions


def Time_Interval(timestamp: datetime) -> tuple:
    return timestamp - TIME_DIFFERENCE, timestamp + TIME_DIFFERENCE
