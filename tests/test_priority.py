# Test file
from backend.process import Process
from backend.priority import (
    priority_non_preemptive,
    priority_preemptive
)


def test_priority_non_preemptive():

    processes = [
        Process(pid="P1", arrival_time=0, burst_time=5, priority=2),
        Process(pid="P2", arrival_time=1, burst_time=3, priority=1),
        Process(pid="P3", arrival_time=2, burst_time=2, priority=3)
    ]

    timeline = priority_non_preemptive(processes)

    expected = [
        {"pid": "P1", "start_time": 0, "end_time": 5},
        {"pid": "P2", "start_time": 5, "end_time": 8},
        {"pid": "P3", "start_time": 8, "end_time": 10}
    ]

    assert timeline == expected


def test_priority_preemptive():

    processes = [
        Process(pid="P1", arrival_time=0, burst_time=5, priority=2),
        Process(pid="P2", arrival_time=1, burst_time=3, priority=1),
        Process(pid="P3", arrival_time=2, burst_time=2, priority=3)
    ]

    timeline = priority_preemptive(processes)

    expected = [
        {"pid": "P1", "start_time": 0, "end_time": 1},
        {"pid": "P2", "start_time": 1, "end_time": 4},
        {"pid": "P1", "start_time": 4, "end_time": 8},
        {"pid": "P3", "start_time": 8, "end_time": 10}
    ]

    assert timeline == expected