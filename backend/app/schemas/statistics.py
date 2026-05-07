from pydantic import BaseModel


class StatisticsOverviewResponse(BaseModel):
    total_archives: int
    monthly_new: int
    expiring_soon: int
    department_count: int


class DistributionItem(BaseModel):
    id: int
    name: str
    code: str
    count: int
    percentage: float


class DistributionResponse(BaseModel):
    items: list[DistributionItem]
    total: int


class DepartmentRankingItem(BaseModel):
    id: int
    name: str
    code: str
    count: int


class DepartmentRankingResponse(BaseModel):
    items: list[DepartmentRankingItem]


class MonthlyTrendItem(BaseModel):
    month: str
    count: int


class MonthlyTrendResponse(BaseModel):
    items: list[MonthlyTrendItem]
