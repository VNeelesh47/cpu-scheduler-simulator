from backend.process import Process
from backend.scheduler import compare_algorithms


def test_compare_all_algorithms():

    processes = [
        Process(pid="P1", arrival_time=0, burst_time=5, priority=2),
        Process(pid="P2", arrival_time=1, burst_time=3, priority=1),
        Process(pid="P3", arrival_time=2, burst_time=2, priority=3)
    ]

    result = compare_algorithms(processes, quantum=2)

    expected_algorithms = [
        "FCFS",
        "SJF_NP",
        "SJF_P",
        "PRIORITY_NP",
        "PRIORITY_P",
        "RR"
    ]

    assert list(result.keys()) == expected_algorithms

    for algorithm in expected_algorithms:

        assert "average_waiting_time" in result[algorithm]
        assert "average_turnaround_time" in result[algorithm]
        assert "average_response_time" in result[algorithm]
        assert "cpu_utilization" in result[algorithm]
        assert "throughput" in result[algorithm]


def test_comparison_uses_same_processes():

    processes = [
        Process(pid="P1", arrival_time=0, burst_time=4, priority=1),
        Process(pid="P2", arrival_time=2, burst_time=3, priority=2)
    ]

    result = compare_algorithms(processes, quantum=2)

    assert len(result) == 6

    for metrics in result.values():
        assert metrics["average_waiting_time"] >= 0
        assert metrics["average_turnaround_time"] >= 0
        assert metrics["cpu_utilization"] <= 100