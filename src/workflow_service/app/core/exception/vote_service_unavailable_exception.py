class VoteServiceUnavailableException(Exception):
    def __init__(self) -> None:
        super().__init__("Vote service is unavailable")
