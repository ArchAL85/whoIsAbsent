import datetime


def get_int_time(date: datetime.datetime = datetime.datetime(2022, 9, 5, 0, 0, 0)):
    x = (datetime.datetime(2022, 9, 5, 0, 0, 0) - datetime.datetime(1970, 1, 1, 0, 0, 0)).total_seconds()
    return x
