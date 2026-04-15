class VoteServiceUnavailableException(Exception):
    def __init__(self, *, timeout: bool = False) -> None:
        self.timeout = timeout
        msg = "Vote service timeout" if timeout else "Vote service is unavailable"
        super().__init__(msg)
