from backend.process import Process
from backend.metrics import calculate_metrics


def test_metrics_basic():

    processes = [
        Process(pid="P1", arrival_time=0, burst_time=5),
        Process(pid="P2", arrival_time=1, burst_time=3)
    ]

    timeline = [
        {"pid": "P1", "start_time": 0, "end_time": 2},
        {"pid": "P2", "start_time": 2, "end_time": 5},
        {"pid": "P1", "start_time": 5, "end_time": 8}
    ]

    result = calculate_metrics(processes, timeline)

    p1 = result["process_metrics"]["P1"]
    p2 = result["process_metrics"]["P2"]

    # P1 metrics
    assert p1["completion_time"] == 8
    assert p1["turnaround_time"] == 8
    assert p1["waiting_time"] == 3
    assert p1["response_time"] == 0

    # P2 metrics
    assert p2["completion_time"] == 5
    assert p2["turnaround_time"] == 4
    assert p2["waiting_time"] == 1
    assert p2["response_time"] == 1

    # Average metrics
    assert result["average_waiting_time"] == 2
    assert result["average_turnaround_time"] == 6
    assert result["average_response_time"] == 0.5

    # CPU metrics
    assert result["cpu_utilization"] == 100
    assert result["throughput"] == 0.25


def test_metrics_with_idle_time():

    processes = [
        Process(pid="P1", arrival_time=3, burst_time=2)
    ]

    timeline = [
        {"pid": None, "start_time": 0, "end_time": 3},
        {"pid": "P1", "start_time": 3, "end_time": 5}
    ]

    result = calculate_metrics(processes, timeline)

    assert result["process_metrics"]["P1"]["waiting_time"] == 0

    assert result["cpu_utilization"] == 40

    assert result["throughput"] == 0.2


def test_metrics_empty_processes():

    result = calculate_metrics([], [])

    assert result["process_metrics"] == {}
    assert result["average_waiting_time"] == 0
    assert result["average_turnaround_time"] == 0
    assert result["average_response_time"] == 0
    assert result["cpu_utilization"] == 0
    assert result["throughput"] == 0

def test_metrics_reject_incomplete_process_execution():
    import pytest

    processes = [Process(pid="P1", arrival_time=0, burst_time=5)]
    timeline = [
        {"pid": "P1", "start_time": 0, "end_time": 3}
    ]

    with pytest.raises(ValueError, match="expected 5"):
        calculate_metrics(processes, timeline)


def test_metrics_reject_unknown_process_id():
    import pytest

    processes = [Process(pid="P1", arrival_time=0, burst_time=2)]
    timeline = [
        {"pid": "P2", "start_time": 0, "end_time": 2}
    ]

    with pytest.raises(ValueError, match="unknown process ID"):
        calculate_metrics(processes, timeline)
