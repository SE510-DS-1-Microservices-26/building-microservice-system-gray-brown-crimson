from typing import Protocol, Any

class OutboxRepositoryProtocol(Protocol):
    def save(self, event: Any) -> None: ...
