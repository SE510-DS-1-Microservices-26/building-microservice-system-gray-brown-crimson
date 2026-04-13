class PollServiceUnavailableException(Exception):
    def __init__(self, *, timeout: bool = False) -> None:
        self.timeout = timeout
        msg = "Poll service timeout" if timeout else "Poll service is unavailable"
        super().__init__(msg)
