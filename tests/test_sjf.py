# Test file
from backend.process import Process
from backend.sjf import (
    sjf_non_preemptive,
    sjf_preemptive
)


def test_sjf_non_preemptive():

    processes = [
        Process(pid="P1", arrival_time=0, burst_time=7),
        Process(pid="P2", arrival_time=2, burst_time=4),
        Process(pid="P3", arrival_time=4, burst_time=1)
    ]

    timeline = sjf_non_preemptive(processes)

    expected = [
        {"pid": "P1", "start_time": 0, "end_time": 7},
        {"pid": "P3", "start_time": 7, "end_time": 8},
        {"pid": "P2", "start_time": 8, "end_time": 12}
    ]

    assert timeline == expected


def test_sjf_preemptive():

    processes = [
        Process(pid="P1", arrival_time=0, burst_time=7),
        Process(pid="P2", arrival_time=2, burst_time=4),
        Process(pid="P3", arrival_time=4, burst_time=1)
    ]

    timeline = sjf_preemptive(processes)

    expected = [
        {"pid": "P1", "start_time": 0, "end_time": 2},
        {"pid": "P2", "start_time": 2, "end_time": 4},
        {"pid": "P3", "start_time": 4, "end_time": 5},
        {"pid": "P2", "start_time": 5, "end_time": 7},
        {"pid": "P1", "start_time": 7, "end_time": 12}
    ]

    assert timeline == expected