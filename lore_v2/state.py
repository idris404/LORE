from typing import TypedDict, Optional, Annotated


def _merge_dicts(a: dict, b: dict) -> dict:
    return {**a, **b}


class LoreState(TypedDict):
    query:           str
    days:            int
    max_results:     int
    next:            str
    iteration:       int
    papers_ingested: Optional[list]
    synthesis:       Optional[dict]
    contradictions:  Optional[list]
    trends:          Optional[list]
    publish_report:  Optional[dict]
    error:           Optional[str]
    agent_errors:    Annotated[dict, _merge_dicts]
