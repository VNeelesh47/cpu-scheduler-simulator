
import pytest

from backend.process import Process
from backend.scheduler import run_scheduler


@pytest.fixture
def processes():
    return [
        Process(pid="P1", arrival_time=0, burst_time=7, priority=3),
        Process(pid="P2", arrival_time=2, burst_time=4, priority=1),
        Process(pid="P3", arrival_time=4, burst_time=1, priority=4),
        Process(pid="P4", arrival_time=5, burst_time=4, priority=2)
    ]


@pytest.mark.parametrize(
    "algorithm, expected_timeline, expected_metrics",
    [
        (
            "FCFS",
            [
                ("P1", 0, 7),
                ("P2", 7, 11),
                ("P3", 11, 12),
                ("P4", 12, 16)
            ],
            {
                "P1": (7, 7, 0, 0),
                "P2": (11, 9, 5, 5),
                "P3": (12, 8, 7, 7),
                "P4": (16, 11, 7, 7)
            }
        ),
        (
            "SJF_NP",
            [
                ("P1", 0, 7),
                ("P3", 7, 8),
                ("P2", 8, 12),
                ("P4", 12, 16)
            ],
            {
                "P1": (7, 7, 0, 0),
                "P2": (12, 10, 6, 6),
                "P3": (8, 4, 3, 3),
                "P4": (16, 11, 7, 7)
            }
        ),
        (
            "SJF_P",
            [
                ("P1", 0, 2),
                ("P2", 2, 4),
                ("P3", 4, 5),
                ("P2", 5, 7),
                ("P4", 7, 11),
                ("P1", 11, 16)
            ],
            {
                "P1": (16, 16, 9, 0),
                "P2": (7, 5, 1, 0),
                "P3": (5, 1, 0, 0),
                "P4": (11, 6, 2, 2)
            }
        ),
        (
            "PRIORITY_NP",
            [
                ("P1", 0, 7),
                ("P2", 7, 11),
                ("P4", 11, 15),
                ("P3", 15, 16)
            ],
            {
                "P1": (7, 7, 0, 0),
                "P2": (11, 9, 5, 5),
                "P3": (16, 12, 11, 11),
                "P4": (15, 10, 6, 6)
            }
        ),
        (
            "PRIORITY_P",
            [
                ("P1", 0, 2),
                ("P2", 2, 6),
                ("P4", 6, 10),
                ("P1", 10, 15),
                ("P3", 15, 16)
            ],
            {
                "P1": (15, 15, 8, 0),
                "P2": (6, 4, 0, 0),
                "P3": (16, 12, 11, 11),
                "P4": (10, 5, 1, 1)
            }
        ),
        (
            "RR",
            [
                ("P1", 0, 2),
                ("P2", 2, 4),
                ("P1", 4, 6),
                ("P3", 6, 7),
                ("P2", 7, 9),
                ("P4", 9, 11),
                ("P1", 11, 13),
                ("P4", 13, 15),
                ("P1", 15, 16)
            ],
            {
                "P1": (16, 16, 9, 0),
                "P2": (9, 7, 3, 0),
                "P3": (7, 3, 2, 2),
                "P4": (15, 10, 6, 4)
            }
        )
    ]
)
def test_algorithm_correctness(
    processes,
    algorithm,
    expected_timeline,
    expected_metrics
):

    result = run_scheduler(
        processes,
        algorithm,
        quantum=2
    )

    actual_timeline = [
        (slot["pid"], slot["start_time"], slot["end_time"])
        for slot in result["timeline"]
    ]

    assert actual_timeline == expected_timeline

    metrics = result["metrics"]["process_metrics"]

    for pid, expected in expected_metrics.items():

        completion, tat, waiting, response = expected

        assert metrics[pid]["completion_time"] == completion
        assert metrics[pid]["turnaround_time"] == tat
        assert metrics[pid]["waiting_time"] == waiting
        assert metrics[pid]["response_time"] == response


def test_cpu_utilization_and_throughput(processes):

    algorithms = [
        "FCFS",
        "SJF_NP",
        "SJF_P",
        "PRIORITY_NP",
        "PRIORITY_P",
        "RR"
    ]

    for algorithm in algorithms:

        result = run_scheduler(
            processes,
            algorithm,
            quantum=2
        )

        metrics = result["metrics"]

        assert metrics["cpu_utilization"] == pytest.approx(100.0)
        assert metrics["throughput"] == pytest.approx(0.25)
