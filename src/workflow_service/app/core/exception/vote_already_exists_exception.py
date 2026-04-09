class VoteAlreadyExistsException(Exception):
    def __init__(self, user_id: str, poll_id: str) -> None:
        self.user_id = user_id
        self.poll_id = poll_id
        super().__init__(f"User {user_id} has already voted in poll {poll_id}")
