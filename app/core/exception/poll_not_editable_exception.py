class PollNotEditableException(Exception):
    def __init__(self, poll_id: str, status: str) -> None:
        self.poll_id = poll_id
        self.status = status
        super().__init__(
            f"Poll '{poll_id}' cannot be edited: questions are locked once a poll leaves DRAFT (current status: {status})."
        )
