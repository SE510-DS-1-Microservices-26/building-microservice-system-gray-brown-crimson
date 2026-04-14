class VoteNotFoundException(Exception):
    def __init__(self, vote_id: str):
        self.vote_id = vote_id
        super().__init__(f"Vote '{vote_id}' not found.")
