from pydantic import BaseModel, Field, field_validator
from enum import Enum
from typing import Optional


class Language(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    CPP = "cpp"


class ExecutionRequest(BaseModel):
    language: Language = Field(..., description="Programming language to execute")
    code: str = Field(..., description="Source code to execute", min_length=1, max_length=10000)
    stdin: Optional[str] = Field(default="", description="Standard input for the program")
    timeout: Optional[int] = Field(default=10, ge=1, le=30, description="Execution timeout in seconds")

    @field_validator("code")
    def code_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Code cannot be empty or whitespace only")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "language": "python",
                "code": "name = input()\nprint(f'Hello, {name}!')",
                "stdin": "World",
                "timeout": 10,
            }
        }


class ExecutionStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    COMPILE_ERROR = "compile_error"


class ExecutionResponse(BaseModel):
    status: ExecutionStatus
    stdout: str
    stderr: str
    exit_code: int
    execution_time_ms: float
    language: Language
    job_id: str | None = None
    files: list[str] = []
