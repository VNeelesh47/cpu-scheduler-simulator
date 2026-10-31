# Test file
import pytest

from backend.process import Process
from backend.round_robin import round_robin_scheduling


def test_round_robin_basic():

    processes = [
        Process(pid="P1", arrival_time=0, burst_time=5),
        Process(pid="P2", arrival_time=1, burst_time=3),
        Process(pid="P3", arrival_time=2, burst_time=1)
    ]

    timeline = round_robin_scheduling(processes, quantum=2)

    expected = [
        {"pid": "P1", "start_time": 0, "end_time": 2},
        {"pid": "P2", "start_time": 2, "end_time": 4},
        {"pid": "P3", "start_time": 4, "end_time": 5},
        {"pid": "P1", "start_time": 5, "end_time": 7},
        {"pid": "P2", "start_time": 7, "end_time": 8},
        {"pid": "P1", "start_time": 8, "end_time": 9}
    ]

    assert timeline == expected


def test_round_robin_invalid_quantum():

    processes = [
        Process(pid="P1", arrival_time=0, burst_time=5)
    ]

    with pytest.raises(ValueError):
        round_robin_scheduling(processes, quantum=0)