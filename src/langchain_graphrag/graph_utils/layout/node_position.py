from dataclasses import dataclass


@dataclass
class NodePosition:
    """Node position class definition."""

    label: str
    cluster: str
    size: float

    x: float
    y: float
    z: float | None = None

    def to_pandas(self) -> tuple[str, float, float, str, float]:
        return self.label, self.x, self.y, self.cluster, self.size


GraphLayout = list[NodePosition]
