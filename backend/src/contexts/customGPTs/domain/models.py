from uuid import uuid4





class CustomGPT:
    def __init__(
        self,
        name: str,
        instructions: str,
        description: str | None = None,
        id: str | None = None,
    ) -> None:
        self.id = id if id else str(uuid4())
        self.name = name
        self.instructions: str = instructions
        self.description: str | None = description

    id: str
    name: str
    instructions: str
    description: str | None = None
