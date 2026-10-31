from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

from backend.process import Process
from backend.scheduler import compare_algorithms, run_scheduler


app = FastAPI(
    title="CPU Scheduling Simulator API",
    description=(
        "Simulate FCFS, SJF, Priority, and Round Robin CPU scheduling "
        "algorithms, and compare their performance metrics."
    ),
    version="1.1.0"
)

# Allow the local React development servers to call this API from a browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


class SimulationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    processes: list[Process]
    algorithm: Literal[
        "FCFS",
        "SJF_NP",
        "SJF_P",
        "PRIORITY_NP",
        "PRIORITY_P",
        "RR"
    ]
    quantum: int | None = Field(default=None, gt=0)


class ComparisonRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    processes: list[Process]
    quantum: int = Field(default=2, gt=0)


def validate_processes(processes: list[Process]) -> None:
    """Apply request-level validation shared by both API endpoints."""
    if not processes:
        raise HTTPException(
            status_code=400,
            detail="At least one process is required"
        )

    process_ids = [process.pid for process in processes]
    if len(process_ids) != len(set(process_ids)):
        raise HTTPException(
            status_code=400,
            detail="Process IDs must be unique"
        )


@app.get("/")
@app.get("/api")
def home():
    return {
        "message": "CPU Scheduling Simulator API is running"
    }


@app.post("/simulate")
@app.post("/api/simulate")
def simulate(request: SimulationRequest):
    validate_processes(request.processes)

    if request.algorithm == "RR" and request.quantum is None:
        raise HTTPException(
            status_code=400,
            detail="Time quantum is required for Round Robin"
        )

    try:
        return run_scheduler(
            processes=request.processes,
            algorithm=request.algorithm,
            quantum=request.quantum
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error


@app.post("/compare")
@app.post("/api/compare")
def compare(request: ComparisonRequest):
    validate_processes(request.processes)

    try:
        return compare_algorithms(
            processes=request.processes,
            quantum=request.quantum
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error