
import pytest

from backend.process import Process
from backend.scheduler import run_scheduler


ALGORITHMS = [
    "FCFS",
    "SJF_NP",
    "SJF_P",
    "PRIORITY_NP",
    "PRIORITY_P",
    "RR"
]


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_all_processes_arrive_at_same_time(algorithm):

    processes = [
        Process(pid="P1", arrival_time=0, burst_time=4, priority=2),
        Process(pid="P2", arrival_time=0, burst_time=2, priority=1),
        Process(pid="P3", arrival_time=0, burst_time=1, priority=3)
    ]

    result = run_scheduler(processes, algorithm, quantum=2)

    expected = {
        "FCFS": [
            ("P1", 0, 4),
            ("P2", 4, 6),
            ("P3", 6, 7)
        ],
        "SJF_NP": [
            ("P3", 0, 1),
            ("P2", 1, 3),
            ("P1", 3, 7)
        ],
        "SJF_P": [
            ("P3", 0, 1),
            ("P2", 1, 3),
            ("P1", 3, 7)
        ],
        "PRIORITY_NP": [
            ("P2", 0, 2),
            ("P1", 2, 6),
            ("P3", 6, 7)
        ],
        "PRIORITY_P": [
            ("P2", 0, 2),
            ("P1", 2, 6),
            ("P3", 6, 7)
        ],
        "RR": [
            ("P1", 0, 2),
            ("P2", 2, 4),
            ("P3", 4, 5),
            ("P1", 5, 7)
        ]
    }

    actual = [
        (slot["pid"], slot["start_time"], slot["end_time"])
        for slot in result["timeline"]
    ]

    assert actual == expected[algorithm]


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_single_process(algorithm):

    processes = [
        Process(
            pid="P1",
            arrival_time=5,
            burst_time=10000,
            priority=1
        )
    ]

    result = run_scheduler(processes, algorithm, quantum=7)

    metrics = result["metrics"]["process_metrics"]["P1"]

    assert metrics["completion_time"] == 10005
    assert metrics["turnaround_time"] == 10000
    assert metrics["waiting_time"] == 0
    assert metrics["response_time"] == 0

    assert result["timeline"][0] == {
        "pid": None,
        "start_time": 0,
        "end_time": 5
    }

    execution_time = sum(
        slot["end_time"] - slot["start_time"]
        for slot in result["timeline"]
        if slot["pid"] == "P1"
    )

    assert execution_time == 10000


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_empty_process_list(algorithm):

    result = run_scheduler([], algorithm, quantum=2)

    assert result["timeline"] == []

    metrics = result["metrics"]

    assert metrics["process_metrics"] == {}
    assert metrics["average_waiting_time"] == 0
    assert metrics["average_turnaround_time"] == 0
    assert metrics["average_response_time"] == 0
    assert metrics["cpu_utilization"] == 0
    assert metrics["throughput"] == 0
