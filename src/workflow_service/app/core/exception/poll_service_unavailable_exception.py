class PollServiceUnavailableException(Exception):
    def __init__(self) -> None:
        super().__init__("Poll service is unavailable")
