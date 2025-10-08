from dataclasses import dataclass

@dataclass(frozen=True)
class CustomGPTOverview:
    id: str
    name: str

@dataclass 
class CustomGPT:
    id: str
    name: str
    instruction: str
    description: str | None = None

    # def __repr__(self) -> str:





