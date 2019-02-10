
class User:

    def __init__(self, discord_id, timezone, intervals=list()):
        """
        :param discord_id: string
        :param timezone: enum(TIMEZONES from timezone.py)
        :param intervals: list(Interval)
        """
        self.discord_id = discord_id
        self.timezone = timezone
        self.intervals = intervals

    def __str__(self):
        intervals = '\n\t'.join([str(i) for i in self.intervals])

        return (f"\nDiscord ID: {self.discord_id}"
                f"\nTimezone: {self.timezone}"
                f"\nIntervals:\n\t{intervals}")


class Interval:

    def __init__(self, _id, day, start_hour, end_hour):
        """
        :param _id: int
            The id of the interval
        :param day: enum(DAYS from timezone.py)
        :param start_hour: int
        :param end_hour: int
        """
        self._id = _id
        self.day = day
        self.start_hour = start_hour
        self.end_hour = end_hour

    def __str__(self):
        return f"{self.day} {str(self.start_hour).rjust(2, '0')}:00 - {str(self.end_hour).rjust(2, '0')}:00"
