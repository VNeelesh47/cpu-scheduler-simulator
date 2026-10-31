# CPU Scheduling Simulator

A Python and FastAPI backend for simulating common CPU scheduling algorithms. It produces an execution timeline (Gantt-chart data), per-process metrics, average metrics, CPU utilization, throughput, and cross-algorithm comparisons.

## Features

- First Come, First Served (FCFS)
- Shortest Job First, non-preemptive (SJF-NP)
- Shortest Remaining Time First (SJF-P / SRTF)
- Priority scheduling, non-preemptive
- Priority scheduling, preemptive
- Round Robin (RR) with a configurable time quantum
- Per-process completion, turnaround, waiting, and response times
- Average waiting, turnaround, and response times
- CPU utilization and throughput
- FastAPI endpoints for individual simulation and algorithm comparison
- Request validation and local React development CORS support

## Project structure

```text
CPU_Scheduling_Simulator/
│
├── backend/
│   ├── __init__.py
│   ├── fcfs.py
│   ├── sjf.py
│   ├── priority.py
│   ├── round_robin.py
│   ├── process.py
│   ├── metrics.py
│   └── scheduler.py
│
├── frontend/
│   ├── src/
│   │   ├── App.css
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── index.html
│   ├── package.json
│   └── package-lock.json
│
├── tests/
│
├── .gitignore
├── main.py
├── README.md
└── requirements.txt
```

The React frontend will be maintained separately from this Python backend.

## Requirements

- Python 3.10 or newer
- pip

## Setup on Windows

Open PowerShell or Command Prompt in the project directory.

```powershell
python -m venv .venv
```

Activate the environment in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or in Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

Install dependencies:

```cmd
python -m pip install -r requirements.txt
```

## Run the API

```cmd
python -m uvicorn main:app --reload
```

The API is available at `http://127.0.0.1:8000`.

Interactive API documentation: `http://127.0.0.1:8000/docs`.

## API endpoints

### `GET /`

Returns an API status message and the documentation path.

### `POST /simulate`

Runs one selected scheduling algorithm.

Example request:

```json
{
  "processes": [
    {"pid": "P1", "arrival_time": 0, "burst_time": 5, "priority": 2},
    {"pid": "P2", "arrival_time": 1, "burst_time": 3, "priority": 1}
  ],
  "algorithm": "RR",
  "quantum": 2
}
```

Supported `algorithm` values:

- `FCFS`
- `SJF_NP`
- `SJF_P`
- `PRIORITY_NP`
- `PRIORITY_P`
- `RR`

The `quantum` field is required for `RR` and must be a positive integer. It is ignored by other algorithms.

### `POST /compare`

Runs all six algorithms against the same process list and returns comparable summary metrics.

Example request:

```json
{
  "processes": [
    {"pid": "P1", "arrival_time": 0, "burst_time": 5, "priority": 2},
    {"pid": "P2", "arrival_time": 1, "burst_time": 3, "priority": 1}
  ],
  "quantum": 2
}
```

If `quantum` is omitted, Round Robin comparison uses a default quantum of `2`.

## Input validation

- Process IDs must be non-empty and unique. Leading and trailing whitespace is removed.
- Arrival time must be a non-negative integer.
- Burst time must be a positive integer.
- Priority is an integer; a smaller value means a higher priority.
- Round Robin quantum must be a positive integer.
- Unknown request fields are rejected.
- Empty process lists are rejected by the API.

## Scheduling and tie-breaking rules

- **FCFS:** Processes execute in arrival order. Equal arrival times retain input order.
- **SJF-NP:** Among arrived processes, the shortest original burst executes next. Ties prefer earlier arrival, then input order.
- **SJF-P / SRTF:** The process with the shortest remaining time runs. A new arrival can cause preemption. Ties prefer earlier arrival, then input order.
- **Priority-NP:** Among arrived processes, the smallest priority number executes next. Ties prefer earlier arrival, then input order.
- **Priority-P:** A newly arrived process preempts the running process only when it has a strictly higher priority (a smaller number). Ties prefer earlier arrival, then input order.
- **Round Robin:** The ready queue is FIFO. Processes arriving during a time slice enter the queue before the unfinished process is re-queued.

Preemptive SJF and Priority simulations advance between process-arrival and completion events rather than iterating through every individual time unit.

## Metric definitions

For each process:

- Completion Time (CT): time at which the process finishes.
- Turnaround Time (TAT): `CT - Arrival Time`.
- Waiting Time (WT): `TAT - Burst Time`.
- Response Time (RT): `First Execution Time - Arrival Time`.

Overall:

- CPU Utilization: `(Busy CPU Time / Total Elapsed Time) * 100`.
- Throughput: `Number of completed processes / Total Elapsed Time`.

Total elapsed time is measured from time zero to the final completion, so initial CPU idle time is included. If the process list is empty in a direct scheduler call, metrics are returned as zero; API requests reject an empty list.

## Run tests

From the project root:

```cmd
python -m pytest -v
```

## CORS configuration

The API allows local React development origins on ports `5173` (Vite) and `3000` (commonly used by React tooling), for both `localhost` and `127.0.0.1`. Add the deployed frontend origin to `allow_origins` in `main.py` before production deployment.
