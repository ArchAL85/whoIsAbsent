import datetime


def get_int_time(date: datetime.datetime = datetime.datetime(2022, 9, 26, 0, 0, 0)):
    x = (date - datetime.datetime(1970, 1, 1, 0, 0, 0)).total_seconds()
    return int(x)
