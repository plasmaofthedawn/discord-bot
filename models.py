DAYS = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]


def readable_time(time):
    hour, minute = str(time).split('.')

    minute = str(int(minute)*.6).split('.')[0]

    if len(minute) == 1:
        minute += '0'

    return hour + ":" + minute


class User:

    def __init__(self, discord_id, timezone, intervals=list()):
        """
        :param discord_id: string
        :param timezone: double
        :param intervals: list(Interval)
        """
        self.discord_id = discord_id
        self.timezone = timezone
        self.intervals = intervals

    def __str__(self):
        intervals = '\n\t'.join([str(i) for i in self.intervals])

        return (f"\nTimezone: UTC{self.timezone}"
                f"\nIntervals (UTC Adjusted):\n\t{intervals}")


class Interval:

    def __init__(self, _id, start_day, end_day, start_hour, end_hour):
        """
        :param _id: int
            The id of the interval
        :param start_day: int
        :param end_day: int
        :param start_hour: double
        :param end_hour: double
        """
        self._id = _id
        self.start_day = start_day
        self.end_day = end_day
        self.start_hour = start_hour
        self.end_hour = end_hour

    def __str__(self):
        print(self.start_day)
        return f"{DAYS[self.start_day]} {readable_time(self.start_hour)} - " \
               f"{DAYS[self.end_day]} {readable_time(self.end_hour)}"

    def get_id(self):
        return self._id
