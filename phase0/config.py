from datetime import date
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator


class GateConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    market: str = Field(default="spot", pattern="^spot$")
    symbol: str = Field(pattern=r"^[A-Z0-9]{5,20}$")
    start_date: date
    end_date: date
    project_root: Path

    @field_validator("end_date")
    @classmethod
    def ordered_dates(cls, value: date, info):
        start = info.data.get("start_date")
        if start and value < start:
            raise ValueError("end_date must not precede start_date")
        return value

    @property
    def raw_dir(self) -> Path:
        return self.project_root / "data" / "raw" / "spot" / self.symbol

    @property
    def db_path(self) -> Path:
        return self.project_root / "data" / "phase0.duckdb"

    @property
    def report_dir(self) -> Path:
        return self.project_root / "reports" / "phase0" / f"spot_{self.symbol}"
