from datetime import datetime

from pydantic import BaseModel


class SigninRequest(BaseModel):
    email: str = "operator@linewatch.local"
    device_id: str = "portfolio-device"


class RefreshRequest(BaseModel):
    user_id: str
    device_id: str
    refresh_token: str


class LogoutRequest(BaseModel):
    user_id: str
    device_id: str


class TokenResponse(BaseModel):
    user_id: str
    access_token: str
    refresh_token: str


class LineResponse(BaseModel):
    id: str
    name: str
    plant: str
    status: str


class QualityEventResponse(BaseModel):
    id: str
    lineId: str
    machineId: str
    severity: str
    status: str
    reason: str
    defectScore: float
    openedAt: datetime


class SensorPointResponse(BaseModel):
    time: str
    value: float


class StatusPatch(BaseModel):
    status: str
    actor_id: str = "user-operator"
    memo: str = "status changed from dashboard"


class IngestRequest(BaseModel):
    machine_id: str = "cam-01"
    metric: str = "vibration"
    value: float = 88
    unit: str = "hz"
    defect_score: float = 0.91
    label: str = "scratch"
