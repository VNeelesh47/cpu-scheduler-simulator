def priority_non_preemptive(processes):
    """Run non-preemptive priority scheduling.

    A smaller priority number means a higher priority. Ties are resolved by
    earlier arrival, then original input order.
    """
    processes = sorted(processes, key=lambda p: p.arrival_time)

    timeline = []
    completed = set()
    current_time = 0
    n = len(processes)

    while len(completed) < n:
        available = [
            p for p in processes
            if p.arrival_time <= current_time and p.pid not in completed
        ]

        if not available:
            next_arrival = min(
                p.arrival_time for p in processes if p.pid not in completed
            )
            timeline.append({
                "pid": None,
                "start_time": current_time,
                "end_time": next_arrival
            })
            current_time = next_arrival
            continue

        selected = min(
            available,
            key=lambda p: (p.priority, p.arrival_time)
        )

        end_time = current_time + selected.burst_time
        timeline.append({
            "pid": selected.pid,
            "start_time": current_time,
            "end_time": end_time
        })

        current_time = end_time
        completed.add(selected.pid)

    return timeline


def priority_preemptive(processes):
    """Run preemptive priority scheduling using arrival-event simulation.

    A smaller priority number means a higher priority. The running process
    is reconsidered only at a new arrival or completion event. Ties prefer
    earlier arrival, then original input order.
    """
    n = len(processes)
    remaining_time = {p.pid: p.burst_time for p in processes}
    completed = set()
    timeline = []
    current_time = 0

    while len(completed) < n:
        available = [
            p for p in processes
            if p.arrival_time <= current_time and p.pid not in completed
        ]

        if not available:
            next_arrival = min(
                p.arrival_time for p in processes if p.pid not in completed
            )
            timeline.append({
                "pid": None,
                "start_time": current_time,
                "end_time": next_arrival
            })
            current_time = next_arrival
            continue

        selected = min(
            available,
            key=lambda p: (p.priority, p.arrival_time)
        )

        future_arrivals = [
            p.arrival_time for p in processes
            if p.pid not in completed and p.arrival_time > current_time
        ]
        next_arrival = min(future_arrivals) if future_arrivals else None

        run_duration = remaining_time[selected.pid]
        if next_arrival is not None:
            run_duration = min(run_duration, next_arrival - current_time)

        start_time = current_time
        current_time += run_duration
        remaining_time[selected.pid] -= run_duration

        if (
            timeline
            and timeline[-1]["pid"] == selected.pid
            and timeline[-1]["end_time"] == start_time
        ):
            timeline[-1]["end_time"] = current_time
        else:
            timeline.append({
                "pid": selected.pid,
                "start_time": start_time,
                "end_time": current_time
            })

        if remaining_time[selected.pid] == 0:
            completed.add(selected.pid)

    return timeline
