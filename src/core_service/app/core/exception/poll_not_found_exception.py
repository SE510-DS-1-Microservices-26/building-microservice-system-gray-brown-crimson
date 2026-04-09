class PollNotFoundException(Exception):
    def __init__(self, poll_id: str) -> None:
        self.poll_id = poll_id
        super().__init__(f"Poll with ID '{poll_id}' could not be located.")
