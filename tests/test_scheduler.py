import pytest

from backend.process import Process
from backend.scheduler import run_scheduler


@pytest.fixture
def sample_processes():
    return [
        Process(pid="P1", arrival_time=0, burst_time=5, priority=2),
        Process(pid="P2", arrival_time=1, burst_time=3, priority=1),
        Process(pid="P3", arrival_time=2, burst_time=2, priority=3)
    ]


@pytest.mark.parametrize("algorithm", [
    "FCFS",
    "SJF_NP",
    "SJF_P",
    "PRIORITY_NP",
    "PRIORITY_P",
    "RR"
])
def test_scheduler_algorithms(sample_processes, algorithm):

    result = run_scheduler(
        processes=sample_processes,
        algorithm=algorithm,
        quantum=2
    )

    assert result["algorithm"] == algorithm
    assert len(result["timeline"]) > 0
    assert "process_metrics" in result["metrics"]

    assert len(result["metrics"]["process_metrics"]) == 3


def test_scheduler_round_robin_quantum(sample_processes):

    with pytest.raises(ValueError):
        run_scheduler(
            processes=sample_processes,
            algorithm="RR"
        )


def test_scheduler_invalid_algorithm(sample_processes):

    with pytest.raises(ValueError):
        run_scheduler(
            processes=sample_processes,
            algorithm="INVALID"
        )