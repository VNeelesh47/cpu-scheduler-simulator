from backend.process import Process

from backend.fcfs import fcfs_scheduling

from backend.sjf import (
    sjf_non_preemptive,
    sjf_preemptive
)

from backend.priority import (
    priority_non_preemptive,
    priority_preemptive
)

from backend.round_robin import round_robin_scheduling


# 1. Simultaneous arrivals in FCFS
def test_fcfs_simultaneous_arrivals():

    processes = [
        Process(pid="P1", arrival_time=0, burst_time=3),
        Process(pid="P2", arrival_time=0, burst_time=2),
        Process(pid="P3", arrival_time=0, burst_time=1)
    ]

    timeline = fcfs_scheduling(processes)

    assert [slot["pid"] for slot in timeline] == [
        "P1", "P2", "P3"
    ]


# 2. Same burst time in SJF
def test_sjf_equal_burst_time():

    processes = [
        Process(pid="P1", arrival_time=0, burst_time=3),
        Process(pid="P2", arrival_time=0, burst_time=2),
        Process(pid="P3", arrival_time=0, burst_time=2)
    ]

    timeline = sjf_non_preemptive(processes)

    assert [slot["pid"] for slot in timeline] == [
        "P2", "P3", "P1"
    ]


# 3. SRTF: Equal remaining time
def test_srtf_equal_remaining_time():

    processes = [
        Process(pid="P1", arrival_time=0, burst_time=4),
        Process(pid="P2", arrival_time=2, burst_time=2)
    ]

    timeline = sjf_preemptive(processes)

    assert timeline == [
        {"pid": "P1", "start_time": 0, "end_time": 4},
        {"pid": "P2", "start_time": 4, "end_time": 6}
    ]


# 4. Same priority in non-preemptive scheduling
def test_priority_equal_priority():

    processes = [
        Process(pid="P1", arrival_time=0, burst_time=3, priority=1),
        Process(pid="P2", arrival_time=0, burst_time=2, priority=1)
    ]

    timeline = priority_non_preemptive(processes)

    assert [slot["pid"] for slot in timeline] == [
        "P1", "P2"
    ]


# 5. Equal priority should not cause preemption
def test_priority_preemptive_equal_priority():

    processes = [
        Process(pid="P1", arrival_time=0, burst_time=4, priority=2),
        Process(pid="P2", arrival_time=2, burst_time=2, priority=2)
    ]

    timeline = priority_preemptive(processes)

    assert timeline == [
        {"pid": "P1", "start_time": 0, "end_time": 4},
        {"pid": "P2", "start_time": 4, "end_time": 6}
    ]


# 6. Higher priority process should preempt
def test_priority_preemption():

    processes = [
        Process(pid="P1", arrival_time=0, burst_time=5, priority=3),
        Process(pid="P2", arrival_time=2, burst_time=2, priority=1)
    ]

    timeline = priority_preemptive(processes)

    assert timeline == [
        {"pid": "P1", "start_time": 0, "end_time": 2},
        {"pid": "P2", "start_time": 2, "end_time": 4},
        {"pid": "P1", "start_time": 4, "end_time": 7}
    ]


# 7. Round Robin: New arrival at quantum boundary
def test_rr_arrival_at_quantum_boundary():

    processes = [
        Process(pid="P1", arrival_time=0, burst_time=4),
        Process(pid="P2", arrival_time=2, burst_time=1)
    ]

    timeline = round_robin_scheduling(processes, quantum=2)

    assert timeline == [
        {"pid": "P1", "start_time": 0, "end_time": 2},
        {"pid": "P2", "start_time": 2, "end_time": 3},
        {"pid": "P1", "start_time": 3, "end_time": 5}
    ]


# 8. CPU idle gaps
def test_cpu_idle_gaps():

    processes = [
        Process(pid="P1", arrival_time=2, burst_time=1),
        Process(pid="P2", arrival_time=6, burst_time=1)
    ]

    expected = [
        {"pid": None, "start_time": 0, "end_time": 2},
        {"pid": "P1", "start_time": 2, "end_time": 3},
        {"pid": None, "start_time": 3, "end_time": 6},
        {"pid": "P2", "start_time": 6, "end_time": 7}
    ]

    algorithms = [
        fcfs_scheduling,
        sjf_non_preemptive,
        sjf_preemptive,
        priority_non_preemptive,
        priority_preemptive
    ]

    for algorithm in algorithms:
        assert algorithm(processes) == expected

    assert round_robin_scheduling(processes, quantum=2) == expected