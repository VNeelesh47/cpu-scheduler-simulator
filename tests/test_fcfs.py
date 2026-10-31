from backend.process import Process
from backend.fcfs import fcfs_scheduling


def test_fcfs_basic():

    processes = [
        Process(pid="P1", arrival_time=0, burst_time=5),
        Process(pid="P2", arrival_time=1, burst_time=3),
        Process(pid="P3", arrival_time=2, burst_time=8)
    ]

    timeline = fcfs_scheduling(processes)

    expected = [
        {"pid": "P1", "start_time": 0, "end_time": 5},
        {"pid": "P2", "start_time": 5, "end_time": 8},
        {"pid": "P3", "start_time": 8, "end_time": 16}
    ]

    assert timeline == expected


def test_fcfs_idle_time():

    processes = [
        Process(pid="P1", arrival_time=3, burst_time=4)
    ]

    timeline = fcfs_scheduling(processes)

    assert timeline == [
        {"pid": None, "start_time": 0, "end_time": 3},
        {"pid": "P1", "start_time": 3, "end_time": 7}
    ]