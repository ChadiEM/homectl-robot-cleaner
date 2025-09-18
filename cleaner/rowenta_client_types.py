from typing import List, Optional, Literal

from pydantic import BaseModel


class CleanResponse(BaseModel):
    cmd_id: int


class TimeModel(BaseModel):
    year: int
    month: int
    day: int
    hour: int
    min: int
    sec: int


class EventHistoryItem(BaseModel):
    time: TimeModel
    state_id: int
    state: str


class AreaHistoryItem(BaseModel):
    area_id: int
    start_time: TimeModel
    end_time: TimeModel
    state_id: int
    state: str


class TaskHistoryItem(BaseModel):
    id: int
    task_type_id: int
    task_type: str
    strategy: str
    cleaning_parameter_set: int
    map_id: int
    area_ids: List[int]
    source: str
    source_id: int
    start_time: TimeModel
    end_time: TimeModel
    state_id: int
    state: str
    area: Optional[int]  # Some tasks have area = 0
    continuable: int
    event_history: List[EventHistoryItem]
    area_history: List[AreaHistoryItem]
    firmware: str


class TaskHistoryResponse(BaseModel):
    task_history: List[TaskHistoryItem]
    task_requires_map_confirmation: int
    task_requires_special_area_confirmation: int


class TimeWithDayOfWeek(BaseModel):
    year: int
    month: int
    day: int
    hour: int
    min: int
    sec: int
    day_of_week: int


class StatusModel(BaseModel):
    voltage: int
    mode: Literal["ready", "cleaning", "go_home", "not_ready"]
    cleaning_parameter_set: int
    battery_level: int
    charging: Literal["connected", "unconnected"]
    time: TimeWithDayOfWeek
    startup_time: TimeWithDayOfWeek
