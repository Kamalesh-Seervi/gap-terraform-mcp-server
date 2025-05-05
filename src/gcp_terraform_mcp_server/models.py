class MCPResponse:
    """Local MCPResponse model stub used by handlers"""
    def __init__(self, content: str, metadata: dict | None = None) -> None:
        self.content = content
        self.metadata = metadata or {}
