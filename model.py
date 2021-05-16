from datetime import datetime

class ApiAlarm():
    def __init__(self, location: str, timestamp: datetime):
        self.location = location
        self.timestamp = timestamp
