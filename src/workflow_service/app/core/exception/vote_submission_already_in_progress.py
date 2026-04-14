class VoteSubmissionAlreadyInProgressException(Exception):
    def __init__(self) -> None:
        super().__init__("A vote submission is already in progress")
