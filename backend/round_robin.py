from collections import deque


def round_robin_scheduling(processes, quantum):

    if quantum <= 0:
        raise ValueError("Time quantum must be greater than zero")

    processes = sorted(
        processes,
        key=lambda p: p.arrival_time
    )

    n = len(processes)

    remaining_time = {
        p.pid: p.burst_time for p in processes
    }

    ready_queue = deque()
    timeline = []

    current_time = 0
    process_index = 0
    completed = 0

    while completed < n:

        # Add newly arrived processes to ready queue
        while (
            process_index < n
            and processes[process_index].arrival_time <= current_time
        ):
            ready_queue.append(processes[process_index])
            process_index += 1

        # Handle CPU idle time
        if not ready_queue:

            next_arrival = processes[process_index].arrival_time

            timeline.append({
                "pid": None,
                "start_time": current_time,
                "end_time": next_arrival
            })

            current_time = next_arrival
            continue

        # Select process from front of ready queue
        selected = ready_queue.popleft()

        start_time = current_time

        # Execute for quantum or remaining burst time
        execution_time = min(
            quantum,
            remaining_time[selected.pid]
        )

        current_time += execution_time

        remaining_time[selected.pid] -= execution_time

        # Record execution interval
        timeline.append({
            "pid": selected.pid,
            "start_time": start_time,
            "end_time": current_time
        })

        # Add processes that arrived during execution
        while (
            process_index < n
            and processes[process_index].arrival_time <= current_time
        ):
            ready_queue.append(processes[process_index])
            process_index += 1

        # Check whether process has completed
        if remaining_time[selected.pid] == 0:
            completed += 1

        else:
            # Move unfinished process to the back
            ready_queue.append(selected)

    return timeline