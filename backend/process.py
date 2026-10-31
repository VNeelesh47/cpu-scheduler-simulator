from pydantic import BaseModel, ConfigDict, Field, field_validator


class Process(BaseModel):
    """Input data for one CPU process."""

    model_config = ConfigDict(extra="forbid")

    pid: str = Field(min_length=1, description="Unique process identifier")
    arrival_time: int = Field(ge=0, description="Time at which the process arrives")
    burst_time: int = Field(gt=0, description="Total CPU time required")
    priority: int = Field(default=0, description="Smaller values represent higher priority")

    @field_validator("pid")
    @classmethod
    def validate_pid(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Process ID must not be empty or whitespace")
        return value
