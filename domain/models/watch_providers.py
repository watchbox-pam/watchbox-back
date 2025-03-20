from dataclasses import dataclass    


@dataclass(frozen=True)
class WatchProviders:
    id: int
    results: dict
