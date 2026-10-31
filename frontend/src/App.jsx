
import React, { useEffect, useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  Activity,
  Plus,
  Play,
  Pause,
  RotateCcw,
  Trash2,
  Clock3,
  Cpu,
  Gauge,
  ChartNoAxesCombined,
} from "lucide-react";
import "./App.css";

const API_URL = import.meta.env.DEV
  ? "http://127.0.0.1:8000/api"
  : "/api";

const initialProcesses = [
  { pid: "P1", arrival_time: "0", burst_time: "5", priority: "2" },
  { pid: "P2", arrival_time: "1", burst_time: "3", priority: "1" },
  { pid: "P3", arrival_time: "2", burst_time: "4", priority: "3" },
  { pid: "P4", arrival_time: "3", burst_time: "2", priority: "2" },
];

const columns = [
  { key: "pid", label: "PROCESS ID", width: "25%" },
  { key: "arrival_time", label: "ARRIVAL TIME", width: "25%" },
  { key: "burst_time", label: "BURST TIME", width: "25%" },
  { key: "priority", label: "PRIORITY", width: "25%" },
];

const processColors = [
  "#B9684C",
  "#78836C",
  "#C29A58",
  "#687E8B",
  "#9B806F",
  "#8A8170",
];

function App() {
  const [processes, setProcesses] = useState(initialProcesses);

  const [algorithmFamily, setAlgorithmFamily] = useState("FCFS");
  const [schedulingMode, setSchedulingMode] = useState("NP");

  const algorithm =
    algorithmFamily === "SJF"
      ? `SJF_${schedulingMode}`
      : algorithmFamily === "PRIORITY"
        ? `PRIORITY_${schedulingMode}`
        : algorithmFamily;

  const [quantum, setQuantum] = useState("2");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [comparison, setComparison] = useState(null);
  const [comparisonLoading, setComparisonLoading] = useState(false);
  const [comparisonError, setComparisonError] = useState("");

  const [playhead, setPlayhead] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(1);

  const totalTime = useMemo(() => {
    if (!result?.timeline?.length) return 0;

    return Math.max(
      ...result.timeline.map((slot) => slot.end_time)
    );
  }, [result]);

  const metrics = result?.metrics;

  // Gantt chart playback
  useEffect(() => {
    if (!playing || !totalTime) return;

    const timer = setInterval(() => {
      setPlayhead((current) => {
        const next = current + 0.04 * speed;

        if (next >= totalTime) {
          setPlaying(false);
          return totalTime;
        }

        return next;
      });
    }, 40);

    return () => clearInterval(timer);
  }, [playing, totalTime, speed]);

  function updateCell(rowIndex, key, value) {
    setComparison(null);
    setProcesses((current) =>
      current.map((process, index) =>
        index === rowIndex
          ? { ...process, [key]: value }
          : process
      )
    );
  }

  function addProcess() {
    setComparison(null);
    const usedNumbers = processes
      .map((p) => Number(p.pid.replace(/\D/g, "")))
      .filter(Number.isFinite);

    let nextNumber = 1;

    while (usedNumbers.includes(nextNumber)) {
      nextNumber++;
    }

    setProcesses((current) => [
      ...current,
      {
        pid: `P${nextNumber}`,
        arrival_time: "0",
        burst_time: "1",
        priority: "1",
      },
    ]);

    setError("");
  }

  function removeProcess(index) {
    setComparison(null);
    if (processes.length === 1) {
      setError("At least one process is required.");
      return;
    }

    setProcesses((current) =>
      current.filter((_, rowIndex) => rowIndex !== index)
    );

    setError("");
    resetSimulation();
  }

  // Excel-compatible tab-separated paste
  function handlePaste(event, startRow, startColumn) {
    const pastedText = event.clipboardData.getData("text");

    if (
      !pastedText.includes("\t") &&
      !pastedText.includes("\n")
    ) {
      return;
    }

    event.preventDefault();
    setComparison(null);

    const pastedRows = pastedText
      .trim()
      .split(/\r?\n/)
      .map((line) => line.split("\t"));

    setProcesses((current) => {
      const updated = [...current];

      pastedRows.forEach((values, rowOffset) => {
        const rowIndex = startRow + rowOffset;

        if (!updated[rowIndex]) {
          updated[rowIndex] = {
            pid: `P${rowIndex + 1}`,
            arrival_time: "0",
            burst_time: "1",
            priority: "1",
          };
        }

        values.forEach((value, columnOffset) => {
          const column = columns[startColumn + columnOffset];

          if (column) {
            updated[rowIndex] = {
              ...updated[rowIndex],
              [column.key]: value.trim(),
            };
          }
        });
      });

      return updated;
    });

    setError("");
  }

  function validateProcesses() {
    if (processes.length === 0) {
      return "At least one process is required.";
    }

    const ids = processes.map((p) => p.pid.trim());

    if (ids.some((id) => !id)) {
      return "Every process must have a Process ID.";
    }

    if (new Set(ids).size !== ids.length) {
      return "Process IDs must be unique.";
    }

    for (const process of processes) {
      const arrival = Number(process.arrival_time);
      const burst = Number(process.burst_time);
      const priority = Number(process.priority);

      if (!Number.isInteger(arrival) || arrival < 0) {
        return `Invalid arrival time for ${process.pid}. Use a non-negative integer.`;
      }

      if (!Number.isInteger(burst) || burst <= 0) {
        return `Invalid burst time for ${process.pid}. Use an integer greater than zero.`;
      }

      if (!Number.isInteger(priority)) {
        return `Invalid priority for ${process.pid}. Use an integer.`;
      }
    }

    if (algorithm === "RR") {
      const q = Number(quantum);

      if (!Number.isInteger(q) || q <= 0) {
        return "Time quantum must be a positive integer.";
      }
    }

    return "";
  }

  async function runSimulation() {
    const validationError = validateProcesses();

    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);
    setPlayhead(0);
    setPlaying(false);

    const payload = {
      processes: processes.map((process) => ({
        pid: process.pid.trim(),
        arrival_time: Number(process.arrival_time),
        burst_time: Number(process.burst_time),
        priority: Number(process.priority),
      })),
      algorithm,
    };

    if (algorithm === "RR") {
      payload.quantum = Number(quantum);
    }

    try {
      const response = await fetch(`${API_URL}/simulate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Simulation request failed."
        );
      }

      setResult(data);
      setPlayhead(0);
      setPlaying(true);
    } catch (err) {
      setError(
        err.message === "Failed to fetch"
          ? "Cannot connect to the backend. Make sure FastAPI is running."
          : err.message
      );
    } finally {
      setLoading(false);
    }
  }

  async function runFaceOff() {
    const validationError = validateProcesses();
    if (validationError) {
      setComparisonError(validationError);
      return;
    }
    if (!Number.isInteger(Number(quantum)) || Number(quantum) <= 0) {
      setComparisonError("Time quantum must be a positive integer for the Round Robin comparison.");
      return;
    }

    setComparisonLoading(true);
    setComparisonError("");
    setComparison(null);

    const payload = {
      processes: processes.map((process) => ({
        pid: process.pid.trim(),
        arrival_time: Number(process.arrival_time),
        burst_time: Number(process.burst_time),
        priority: Number(process.priority),
      })),
      quantum: Number(quantum),
    };

    try {
      const response = await fetch(`${API_URL}/compare`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Comparison request failed.");
      }
      setComparison(data);
    } catch (err) {
      setComparisonError(
        err.message === "Failed to fetch"
          ? "Cannot connect to the backend. Make sure FastAPI is running."
          : err.message
      );
    } finally {
      setComparisonLoading(false);
    }
  }

  function resetSimulation() {
    setResult(null);
    setError("");
    setPlayhead(0);
    setPlaying(false);
  }

  function replay() {
    setPlayhead(0);
    setPlaying(true);
  }

  const simulationFinished =
    result !== null &&
    totalTime > 0 &&
    playhead >= totalTime;

  function getProcessColor(pid) {
    const index = processes.findIndex(
      (process) => process.pid === pid
    );

    if (index < 0) return "#8A8170";

    return processColors[index % processColors.length];
  }

  return (
    <main className="app-shell">

      {/* Header */}
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">
            <Activity size={19} strokeWidth={1.8} />
          </div>

          <div>
            <div className="brand-name">
              PULSE<span>.</span>
            </div>

            <div className="brand-subtitle">
              CPU SCHEDULING SIMULATOR
            </div>
          </div>
        </div>

        <div className="system-status">
          <span className="status-dot" />
          SIMULATION ENVIRONMENT
        </div>
      </header>

      {/* Page heading */}
      <section className="page-heading">
        <div>
          <div className="eyebrow">
            PROCESS MANAGEMENT 
          </div>

          <h1>
            Scheduling <span>workspace.</span>
          </h1>

          <p>
            Configure processes. Choose an algorithm.
            Observe how the CPU works.
          </p>
        </div>

      </section>

      {/* Process input table */}
      <section className="input-section panel">
        <div className="section-heading">
          <div>
            <div className="section-kicker">01 / INPUT</div>
            <h2>Process table</h2>
            <p>Enter process details directly into the grid.</p>
          </div>
        </div>

        <div className="spreadsheet-wrap">
          <table className="process-table">
            <colgroup>
              {columns.map((column) => (
                <col
                  key={column.key}
                  style={{ width: column.width }}
                />
              ))}
              <col style={{ width: "48px" }} />
            </colgroup>

            <thead>
              <tr>
                {columns.map((column, index) => (
                  <th key={column.key}>
                    <span className="column-index">
                      0{index + 1}
                    </span>
                    {column.label}
                  </th>
                ))}
                <th aria-label="Actions" />
              </tr>
            </thead>

            <tbody>
              <AnimatePresence initial={false}>
                {processes.map((process, rowIndex) => (
                  <motion.tr
                    key={`${rowIndex}-${process.pid}`}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    {columns.map((column, columnIndex) => (
                      <td key={column.key}>
                        <input
                          aria-label={`${column.label} for row ${rowIndex + 1}`}
                          className={
                            column.key === "pid"
                              ? "pid-input"
                              : "number-input"
                          }
                          value={process[column.key]}
                          onChange={(event) =>
                            updateCell(
                              rowIndex,
                              column.key,
                              event.target.value
                            )
                          }
                          onPaste={(event) =>
                            handlePaste(
                              event,
                              rowIndex,
                              columnIndex
                            )
                          }
                          spellCheck="false"
                        />
                      </td>
                    ))}

                    <td className="action-cell">
                      <button
                        className="icon-button delete-button"
                        onClick={() => removeProcess(rowIndex)}
                        aria-label={`Delete ${process.pid}`}
                        title="Delete process"
                      >
                        <Trash2 size={15} />
                      </button>
                    </td>
                  </motion.tr>
                ))}
              </AnimatePresence>
            </tbody>
          </table>
        </div>

        <div className="table-footer">
          <button
            className="text-button"
            onClick={addProcess}
          >
            <Plus size={15} />
            Add process
          </button>

          <span>
            TIP: Paste tab-separated cells directly from Excel.
          </span>
        </div>
      </section>

      {/* Simulation controls */}
      <section className="control-section panel">
        <div className="section-heading control-heading">
          <div>
            <div className="section-kicker">
              02 / CONFIGURATION
            </div>
            <h2>Simulation controls</h2>
          </div>
        </div>

        <div className="control-row">

          <label className="control-field">
            <span>Scheduling algorithm</span>

            <select
              value={algorithmFamily}
              onChange={(event) => {
                setAlgorithmFamily(event.target.value);
                resetSimulation();
              }}
            >
              <option value="FCFS">
                First Come First Served (FCFS)
              </option>

              <option value="SJF">
                Shortest Job First (SJF)
              </option>

              <option value="PRIORITY">
                Priority Scheduling
              </option>

              <option value="RR">
                Round Robin (RR)
              </option>
            </select>
          </label>

          {(algorithmFamily === "SJF" ||
            algorithmFamily === "PRIORITY") && (
            <div className="control-field">
              <span>Scheduling type</span>

              <div className="mode-selector">
                <button
                  type="button"
                  className={
                    schedulingMode === "NP"
                      ? "mode-active"
                      : ""
                  }
                  onClick={() => {
                    setSchedulingMode("NP");
                    resetSimulation();
                  }}
                >
                  Non-preemptive
                </button>

                <button
                  type="button"
                  className={
                    schedulingMode === "P"
                      ? "mode-active"
                      : ""
                  }
                  onClick={() => {
                    setSchedulingMode("P");
                    resetSimulation();
                  }}
                >
                  Preemptive
                </button>
              </div>
            </div>
          )}

          {algorithmFamily === "RR" && (
            <label className="control-field quantum-field">
              <span>Time quantum</span>

              <input
                type="number"
                min="1"
                step="1"
                value={quantum}
                onChange={(event) => {
                  setQuantum(event.target.value);
                  setComparison(null);
                }}
              />
            </label>
          )}

          <div className="control-actions">
            <button
              className="reset-button"
              onClick={resetSimulation}
            >
              <RotateCcw size={15} />
              Reset
            </button>

            <button
              className="run-button"
              onClick={runSimulation}
              disabled={loading}
            >
              {loading ? (
                <span className="loading-spinner" />
              ) : (
                <Play size={15} fill="currentColor" />
              )}

              {loading ? "Running..." : "Run simulation"}
            </button>
          </div>
        </div>

        {algorithmFamily === "PRIORITY" && (
          <p className="control-note">
            Lower priority number means higher priority.
          </p>
        )}
      </section>

      {/* Algorithm Face-Off */}
      <section className="faceoff-launch panel">
        <div>
          <div className="section-kicker">03 / ALGORITHM FACE-OFF</div>
          <h2>Which algorithm performs best?</h2>
          <p>
            Run all six algorithms against the same process set and compare
            their performance using one consistent input.
          </p>
        </div>
        <button
          className="run-button faceoff-button"
          onClick={runFaceOff}
          disabled={comparisonLoading}
        >
          {comparisonLoading ? (
            <span className="loading-spinner" />
          ) : (
            <ChartNoAxesCombined size={15} />
          )}
          {comparisonLoading ? "Comparing..." : "Run algorithm face-off"}
        </button>
        {comparisonError && (
          <div className="error-message faceoff-error">
            <span>!</span>{comparisonError}
          </div>
        )}
      </section>

      {comparison && (
        <motion.section
          className="faceoff-results"
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="results-heading">
            <div>
              <div className="section-kicker">04 / COMPARATIVE ANALYSIS</div>
              <h2>Algorithm Face-Off</h2>
              <p className="insight-subtitle">
                Six algorithms. Same processes. Five performance measures.
              </p>
            </div>
            <span className="faceoff-count">6 ALGORITHMS</span>
          </div>

          <div className="faceoff-grid">
            {[
              { key: "average_waiting_time", label: "AVG WAITING", unit: "units", lower: true },
              { key: "average_turnaround_time", label: "AVG TURNAROUND", unit: "units", lower: true },
              { key: "average_response_time", label: "AVG RESPONSE", unit: "units", lower: true },
              { key: "cpu_utilization", label: "CPU UTILIZATION", unit: "%", lower: false },
              { key: "throughput", label: "THROUGHPUT", unit: "proc/unit", lower: false },
            ].map((metric) => {
              const ranked = Object.entries(comparison)
                .map(([name, values]) => ({ name, value: values[metric.key] }))
                .sort((a, b) => metric.lower ? a.value - b.value : b.value - a.value);
              const winner = ranked[0];
              return (
                <article className="faceoff-metric panel" key={metric.key}>
                  <div className="faceoff-metric-label">{metric.label}</div>
                  <div className="faceoff-winner">{winner.name.replaceAll("_", " ")}</div>
                  <div className="faceoff-winner-value">
                    {Number(winner.value).toFixed(2)} <small>{metric.unit}</small>
                  </div>
                  <div className="faceoff-ranking">
                    {ranked.map((entry, index) => (
                      <div className="rank-row" key={entry.name}>
                        <span className="rank-number">{index + 1}</span>
                        <span className="rank-name">{entry.name.replaceAll("_", " ")}</span>
                        <strong>{Number(entry.value).toFixed(2)}</strong>
                      </div>
                    ))}
                  </div>
                </article>
              );
            })}
          </div>

          <div className="faceoff-table-panel panel">
            <div className="process-metrics-heading">
              <div>
                <h3>Complete comparison</h3>
                <p>Lower is better for time metrics; higher is better for utilization and throughput.</p>
              </div>
            </div>
            <div className="metrics-table-scroll">
              <table className="performance-table faceoff-table">
                <thead>
                  <tr>
                    <th>ALGORITHM</th>
                    <th>AVG WT</th>
                    <th>AVG TAT</th>
                    <th>AVG RT</th>
                    <th>CPU UTIL.</th>
                    <th>THROUGHPUT</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(comparison).map(([name, values]) => (
                    <tr key={name}>
                      <td><strong>{name.replaceAll("_", " ")}</strong></td>
                      <td>{Number(values.average_waiting_time).toFixed(2)}</td>
                      <td>{Number(values.average_turnaround_time).toFixed(2)}</td>
                      <td>{Number(values.average_response_time).toFixed(2)}</td>
                      <td>{Number(values.cpu_utilization).toFixed(2)}%</td>
                      <td>{Number(values.throughput).toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </motion.section>
      )}

      {/* Error message */}
      {error && (
        <motion.div
          className="error-message"
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <span>!</span>
          {error}
        </motion.div>
      )}

      {/* Simulation results */}
      {result && (
        <motion.section
          className="results-section"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >

          <div className="results-heading">
            <div>
              <div className="section-kicker">
                03 / OUTPUT
              </div>

              <h2>Execution timeline</h2>
            </div>

            <div className="completed-label">
              <span className="status-dot" />
              {simulationFinished
                ? "SIMULATION COMPLETE"
                : "EXECUTION IN PROGRESS"}
            </div>
          </div>

          {/* Gantt chart */}
          <div className="chart-panel panel">

            <div className="chart-topline">
              <div>
                <span className="chart-label">
                  GANTT CHART
                </span>

                <span className="chart-algorithm">
                  {algorithm.replaceAll("_", " ")}
                </span>
              </div>

              <div className="chart-duration">
                TOTAL TIME <strong>{totalTime}</strong>
              </div>
            </div>

            <div className="gantt-scroll">
              <div className="gantt-track">
                {result.timeline.map((slot, index) => {
                  const duration =
                    slot.end_time - slot.start_time;

                  const progress = Math.max(
                    0,
                    Math.min(
                      1,
                      (playhead - slot.start_time) / duration
                    )
                  );

                  const color =
                    slot.pid === null
                      ? "#E8E4DA"
                      : getProcessColor(slot.pid);

                  return (
                    <div
                      key={`${slot.pid}-${slot.start_time}-${index}`}
                      className={`gantt-block ${
                        slot.pid === null ? "idle-block" : ""
                      }`}
                      style={{
                        flexGrow: duration,
                        flexBasis: 0,
                        backgroundColor: color,
                        clipPath: `inset(0 ${
                          (1 - progress) * 100
                        }% 0 0)`,
                      }}
                      title={`${slot.pid ?? "Idle"}: ${slot.start_time} to ${slot.end_time}`}
                    >
                      <span className="block-pid">
                        {slot.pid ?? "IDLE"}
                      </span>

                      <span className="block-duration">
                        {duration} UNIT
                        {duration === 1 ? "" : "S"}
                      </span>
                    </div>
                  );
                })}
              </div>

              <div className="time-markers">
                {result.timeline.map((slot, index) => (
                  <span
                    key={`time-${index}`}
                    style={{
                      left: `${
                        (slot.start_time / totalTime) * 100
                      }%`,
                    }}
                  >
                    {slot.start_time}
                  </span>
                ))}

                <span className="last-marker">
                  {totalTime}
                </span>
              </div>

              <div className="playhead-track">
                <div
                  className="playhead"
                  style={{
                    left: `${
                      (playhead / totalTime) * 100
                    }%`,
                  }}
                />
              </div>
            </div>

            {/* Playback controls */}
            <div className="chart-controls">
              <div className="playback-buttons">
                <button
                  className="playback-button"
                  onClick={() => {
                    if (playhead >= totalTime) {
                      setPlayhead(0);
                      setPlaying(true);
                    } else {
                      setPlaying((value) => !value);
                    }
                  }}
                  title={playing ? "Pause" : "Play"}
                >
                  {playing ? (
                    <Pause size={15} />
                  ) : (
                    <Play size={15} />
                  )}
                </button>

                <button
                  className="playback-button"
                  onClick={replay}
                  title="Replay"
                >
                  <RotateCcw size={14} />
                </button>

                <span className="playback-time">
                  {playhead.toFixed(1)} / {totalTime}
                </span>
              </div>

              <div className="speed-control">
                <span>SPEED</span>

                <select
                  value={speed}
                  onChange={(event) =>
                    setSpeed(Number(event.target.value))
                  }
                >
                  <option value="0.5">0.5×</option>
                  <option value="1">1×</option>
                  <option value="2">2×</option>
                  <option value="4">4×</option>
                </select>
              </div>
            </div>
          </div>

          {/* Scheduling Insights */}
          {simulationFinished && (
            <SchedulingInsights
              algorithm={algorithm}
              timeline={result.timeline}
              metrics={metrics}
              processes={processes.map((process) => ({
                ...process,
                arrival_time: Number(process.arrival_time),
                burst_time: Number(process.burst_time),
                priority: Number(process.priority),
              }))}
            />
          )}

          {/* Metrics appear only after playback */}
          {simulationFinished && (
            <motion.div
              className="performance-results"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7 }}
            >

              <div className="metrics-heading">
                <div>
                  <div className="section-kicker">
                    04 / PERFORMANCE
                  </div>

                  <h2>Performance metrics</h2>
                </div>

                <span>
                  {algorithm.replaceAll("_", " ")}
                </span>
              </div>

              <div className="metrics-grid">
                <MetricCard
                  icon={<Clock3 size={17} />}
                  label="AVG WAITING TIME"
                  value={metrics.average_waiting_time}
                  unit="units"
                  accent="clay"
                />

                <MetricCard
                  icon={<Activity size={17} />}
                  label="AVG TURNAROUND"
                  value={metrics.average_turnaround_time}
                  unit="units"
                  accent="moss"
                />

                <MetricCard
                  icon={<Gauge size={17} />}
                  label="AVG RESPONSE"
                  value={metrics.average_response_time}
                  unit="units"
                  accent="sand"
                />

                <MetricCard
                  icon={<Cpu size={17} />}
                  label="CPU UTILIZATION"
                  value={metrics.cpu_utilization}
                  unit="%"
                  accent="blue"
                />

                <MetricCard
                  icon={<ChartNoAxesCombined size={17} />}
                  label="THROUGHPUT"
                  value={metrics.throughput}
                  unit="process / unit"
                  accent="ink"
                />
              </div>

              {/* Individual process metrics */}
              <div className="process-metrics-panel">

                <div className="process-metrics-heading">
                  <div>
                    <h3>Process breakdown</h3>
                    <p>
                      Individual execution performance
                    </p>
                  </div>

                  <span>
                    {processes.length} PROCESSES
                  </span>
                </div>

                <div className="metrics-table-scroll">
                  <table className="performance-table">
                    <thead>
                      <tr>
                        <th>PROCESS</th>
                        <th>AT</th>
                        <th>BT</th>
                        <th>CT</th>
                        <th>TAT</th>
                        <th>WT</th>
                        <th>RT</th>
                      </tr>
                    </thead>

                    <tbody>
                      {processes.map((process, index) => {
                        const data =
                          metrics.process_metrics[process.pid];

                        return (
                          <tr key={process.pid}>
                            <td>
                              <span
                                className="process-color-dot"
                                style={{
                                  backgroundColor:
                                    processColors[
                                      index % processColors.length
                                    ],
                                }}
                              />
                              <strong>{process.pid}</strong>
                            </td>

                            <td>{data.arrival_time}</td>
                            <td>{data.burst_time}</td>

                            <td>
                              <span className="metric-chip chip-ct">
                                {data.completion_time}
                              </span>
                            </td>

                            <td>
                              <span className="metric-chip chip-tat">
                                {data.turnaround_time}
                              </span>
                            </td>

                            <td>
                              <span className="metric-chip chip-wt">
                                {data.waiting_time}
                              </span>
                            </td>

                            <td>
                              <span className="metric-chip chip-rt">
                                {data.response_time}
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>

                <div className="metrics-legend">
                  <span>AT = Arrival Time</span>
                  <span>BT = Burst Time</span>
                  <span>CT = Completion Time</span>
                  <span>TAT = Turnaround Time</span>
                  <span>WT = Waiting Time</span>
                  <span>RT = Response Time</span>
                </div>
              </div>
            </motion.div>
          )}
        </motion.section>
      )}

      {/* Footer */}
      <footer className="footer">
        <span>PULSE / CPU SCHEDULING SIMULATOR</span>
        <span>BUILT FOR UNDERSTANDING THE PROCESS</span>
      </footer>
    </main>
  );
}

function SchedulingInsights({ algorithm, timeline, metrics, processes }) {
  const names = {
    FCFS: "First Come First Served",
    SJF_NP: "Shortest Job First (Non-preemptive)",
    SJF_P: "Shortest Remaining Time First",
    PRIORITY_NP: "Priority (Non-preemptive)",
    PRIORITY_P: "Priority (Preemptive)",
    RR: "Round Robin",
  };

  const rules = {
    FCFS: "Processes are selected in order of arrival. Once a process gets the CPU, it runs until its burst is complete.",
    SJF_NP: "Among the processes that have arrived, the process with the shortest burst time is selected. It then runs to completion.",
    SJF_P: "The CPU selects the arrived process with the shortest remaining time. A newly arrived process can preempt the current one if its remaining time is shorter.",
    PRIORITY_NP: "Among arrived processes, the lowest priority number is selected. The selected process runs until completion.",
    PRIORITY_P: "The process with the lowest priority number among arrived processes runs. A newly arrived higher-priority process can preempt it.",
    RR: "Processes take turns in FIFO ready-queue order. Each receives at most the configured time quantum before an unfinished process returns to the queue.",
  };

  const processMap = Object.fromEntries(processes.map((p) => [p.pid, p]));
  const busySlots = timeline.filter((slot) => slot.pid !== null);
  const idleSlots = timeline.filter((slot) => slot.pid === null);
  const processSwitches = busySlots.slice(1).filter((slot, index) => slot.pid !== busySlots[index].pid).length;
  const longestWait = Object.entries(metrics.process_metrics)
    .sort((a, b) => b[1].waiting_time - a[1].waiting_time)[0];
  const totalBusy = busySlots.reduce((sum, slot) => sum + slot.end_time - slot.start_time, 0);
  const totalIdle = idleSlots.reduce((sum, slot) => sum + slot.end_time - slot.start_time, 0);

  const explanations = timeline.map((slot, index) => {
    if (slot.pid === null) {
      return {
        title: `CPU idle: ${slot.start_time}–${slot.end_time}`,
        detail: "No process had arrived and was ready to execute during this interval.",
      };
    }

    const process = processMap[slot.pid];
    const duration = slot.end_time - slot.start_time;
    const next = timeline[index + 1];
    let ending = "This execution interval completed the process.";
    if (next && next.pid !== slot.pid) {
      const completed = metrics.process_metrics[slot.pid].completion_time === slot.end_time;
      if (completed) ending = "The process completed at the end of this interval, so the CPU moved to another process.";
      else if (algorithm === "RR") ending = "The time slice ended before the process finished, so it returned to the ready queue.";
      else if (algorithm.endsWith("_P")) ending = "The CPU switched away from this process, consistent with preemptive scheduling.";
      else ending = "The CPU moved to the next ready process.";
    } else if (!next) {
      ending = "This was the final execution interval in the schedule.";
    }

    let selected = "The scheduler selected this process according to its scheduling policy.";
    if (algorithm === "FCFS") selected = "It was the earliest-arrived process in the ready order.";
    if (algorithm.startsWith("SJF")) selected = `Its ${algorithm === "SJF_P" ? "remaining time" : "burst time"} made it the shortest eligible job at selection time.`;
    if (algorithm.startsWith("PRIORITY")) selected = `Its priority value (${process.priority}) made it the highest-priority eligible process. Lower numbers represent higher priority.`;
    if (algorithm === "RR") selected = "It was at the front of the ready queue when its turn began.";

    return {
      title: `${slot.pid} ran: ${slot.start_time}–${slot.end_time} (${duration} units)`,
      detail: `${selected} ${ending}`,
    };
  });

  return (
    <motion.section
      className="insights-panel panel"
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45 }}
    >
      <div className="results-heading">
        <div>
          <div className="section-kicker">05 / SCHEDULING INSIGHTS</div>
          <h2>Why did the CPU behave this way?</h2>
          <p className="insight-subtitle">{names[algorithm]} decision breakdown</p>
        </div>
        <span className="faceoff-count">EXPLAINED FROM TIMELINE</span>
      </div>

      <div className="insight-rule">
        <span className="insight-rule-label">SCHEDULING RULE</span>
        <p>{rules[algorithm]}</p>
      </div>

      <div className="insight-stat-grid">
        <div><strong>{processSwitches}</strong><span>PROCESS SWITCHES</span></div>
        <div><strong>{idleSlots.length}</strong><span>IDLE PERIODS</span></div>
        <div><strong>{totalIdle}</strong><span>IDLE TIME UNITS</span></div>
        <div><strong>{totalBusy}</strong><span>BUSY TIME UNITS</span></div>
      </div>

      {longestWait && (
        <div className="longest-wait-note">
          <strong>Longest waiting process: {longestWait[0]}</strong>
          <span>
            It waited {longestWait[1].waiting_time} time units before and between its CPU execution.
            Average waiting time across all processes was {Number(metrics.average_waiting_time).toFixed(2)} units.
          </span>
        </div>
      )}

      <div className="decision-list-heading">
        <h3>Execution decisions</h3>
        <span>{timeline.length} TIMELINE INTERVALS</span>
      </div>
      <div className="decision-list">
        {explanations.map((item, index) => (
          <article className="decision-item" key={`${item.title}-${index}`}>
            <span className="decision-index">{String(index + 1).padStart(2, "0")}</span>
            <div>
              <strong>{item.title}</strong>
              <p>{item.detail}</p>
            </div>
          </article>
        ))}
      </div>
    </motion.section>
  );
}

function MetricCard({ icon, label, value, unit, accent }) {
  return (
    <motion.article
      className={`metric-card metric-${accent}`}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
    >
      <div className="metric-card-top">
        <span className="metric-icon">{icon}</span>
        <span className="metric-label">{label}</span>
      </div>

      <div className="metric-value">
        {Number(value).toFixed(2)}
        <small>{unit}</small>
      </div>
    </motion.article>
  );
}

export default App;
