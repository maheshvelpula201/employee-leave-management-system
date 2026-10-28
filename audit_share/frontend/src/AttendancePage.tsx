
import { useEffect, useMemo, useState } from "react";
import {
  CalendarDays,
  CheckCircle2,
  Clock3,
  RefreshCw,
  Search,
  UploadCloud,
  Users,
  XCircle,
} from "lucide-react";
import { apiRequest } from "./lib/api";
import "./AttendancePage.css";

type Status =
  | "PRESENT"
  | "ABSENT"
  | "LATE"
  | "HALF_DAY"
  | "ON_LEAVE"
  | "WORK_FROM_HOME"
  | "HOLIDAY"
  | "WEEK_OFF";

type Employee = {
  id: number;
  name: string;
  department?: string | null;
};

type Attendance = {
  id: number;
  employee_id: number;
  attendance_date: string;
  status: Status;
  notes?: string | null;
};

const statuses: Status[] = [
  "PRESENT",
  "ABSENT",
  "LATE",
  "HALF_DAY",
  "ON_LEAVE",
  "WORK_FROM_HOME",
  "HOLIDAY",
  "WEEK_OFF",
];

const statusLabels: Record<Status, string> = {
  PRESENT: "Present",
  ABSENT: "Absent",
  LATE: "Late",
  HALF_DAY: "Half day",
  ON_LEAVE: "On leave",
  WORK_FROM_HOME: "Work from home",
  HOLIDAY: "Holiday",
  WEEK_OFF: "Week off",
};

function todayLocal() {
  const now = new Date();
  const offset = now.getTimezoneOffset();

  return new Date(now.getTime() - offset * 60000)
    .toISOString()
    .slice(0, 10);
}

export default function AttendancePage() {
  const [selectedDate, setSelectedDate] = useState(todayLocal());
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [records, setRecords] = useState<Record<number, Status>>({});
  const [savedIds, setSavedIds] = useState<number[]>([]);
  const [department, setDepartment] = useState("ALL");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [batchInfo, setBatchInfo] = useState<{
    batch_id: number;
    uploaded_at?: string;
    closes_at?: string;
  } | null>(null);

  const departments = useMemo(
    () =>
      Array.from(
        new Set(
          employees
            .map((employee) => employee.department?.trim())
            .filter((value): value is string => Boolean(value)),
        ),
      ).sort(),
    [employees],
  );

  const filteredEmployees = useMemo(
    () =>
      employees.filter((employee) => {
        const matchesDepartment =
          department === "ALL" || employee.department === department;

        const matchesSearch = employee.name
          .toLowerCase()
          .includes(search.trim().toLowerCase());

        return matchesDepartment && matchesSearch;
      }),
    [employees, department, search],
  );

  const counts = useMemo(() => {
    const result: Record<Status, number> = {
      PRESENT: 0,
      ABSENT: 0,
      LATE: 0,
      HALF_DAY: 0,
      ON_LEAVE: 0,
      WORK_FROM_HOME: 0,
      HOLIDAY: 0,
      WEEK_OFF: 0,
    };

    for (const employee of filteredEmployees) {
      const status = records[employee.id];

      if (status) {
        result[status] += 1;
      }
    }

    return result;
  }, [filteredEmployees, records]);

  const markedCount = filteredEmployees.filter(
    (employee) => Boolean(records[employee.id]),
  ).length;

  async function loadAttendance() {
    setLoading(true);
    setError("");
    setMessage("");
    setBatchInfo(null);

    try {
      const [employeeData, attendanceData] = await Promise.all([
        apiRequest<unknown>("/employees/"),
        apiRequest<unknown>(
          `/attendance/?attendance_date=${selectedDate}`,
        ),
      ]);

      const employeeList: Employee[] = Array.isArray(employeeData)
        ? employeeData as Employee[]
        : (
            employeeData as { items?: Employee[] } | null
          )?.items ?? [];

      const attendanceList: Attendance[] = Array.isArray(attendanceData)
        ? attendanceData as Attendance[]
        : [];

      const saved: Record<number, Status> = {};

      for (const record of attendanceList) {
        if (statuses.includes(record.status)) {
          saved[record.employee_id] = record.status;
        }
      }

      setEmployees(employeeList);
      setRecords(saved);
      setSavedIds(attendanceList.map((record) => record.employee_id));
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not load attendance data.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadAttendance();
  }, [selectedDate]);

  function updateStatus(employeeId: number, value: string) {
    setRecords((previous) => {
      const next = { ...previous };

      if (value && statuses.includes(value as Status)) {
        next[employeeId] = value as Status;
      } else {
        delete next[employeeId];
      }

      return next;
    });

    setMessage("");
    setError("");
    setBatchInfo(null);
  }

  async function uploadAttendance() {
    setError("");
    setMessage("");
    setBatchInfo(null);

    if (filteredEmployees.length === 0) {
      setError("No employees are available in this selection.");
      return;
    }

    const unmarked = filteredEmployees.filter(
      (employee) => !records[employee.id],
    );

    if (unmarked.length > 0) {
      setError(
        `Mark attendance for all ${unmarked.length} unmarked employee(s) before uploading.`,
      );
      return;
    }

    const entries = filteredEmployees.map((employee) => ({
      employee_id: employee.id,
      status: records[employee.id],
    }));

    setUploading(true);

    try {
      const result = await apiRequest<{
        message?: string;
        batch_id: number;
        uploaded_at?: string;
        closes_at?: string;
      }>("/attendance/upload", {
        method: "POST",
        body: {
          attendance_date: selectedDate,
          entries,
        },
      });

      setSavedIds((previous) => [
        ...new Set([
          ...previous,
          ...filteredEmployees.map((employee) => employee.id),
        ]),
      ]);

      setBatchInfo({
        batch_id: result.batch_id,
        uploaded_at: result.uploaded_at,
        closes_at: result.closes_at,
      });

      setMessage(
        result.message ?? "Attendance batch uploaded successfully.",
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not upload attendance.",
      );
    } finally {
      setUploading(false);
    }
  }

  return (
    <section className="attendance-page">
      <div className="attendance-hero">
        <div>
          <span className="attendance-eyebrow">
            <Clock3 size={14} />
            PEOPLE OPERATIONS
          </span>
          <h2>Attendance management</h2>
          <p>
            Review employee attendance, validate daily records, and
            publish the completed attendance batch.
          </p>
        </div>

        <button
          className="attendance-refresh"
          type="button"
          onClick={() => void loadAttendance()}
          disabled={loading || uploading}
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      <div className="attendance-controls">
        <label className="attendance-control">
          <span>Attendance date</span>
          <span className="attendance-input-wrap">
            <CalendarDays size={17} />
            <input
              type="date"
              value={selectedDate}
              onChange={(event) => setSelectedDate(event.target.value)}
            />
          </span>
        </label>

        <label className="attendance-control">
          <span>Department</span>
          <select
            value={department}
            onChange={(event) => setDepartment(event.target.value)}
          >
            <option value="ALL">All departments</option>
            {departments.map((item) => (
              <option value={item} key={item}>
                {item}
              </option>
            ))}
          </select>
        </label>

        <label className="attendance-control attendance-search-control">
          <span>Search employees</span>
          <span className="attendance-input-wrap">
            <Search size={17} />
            <input
              type="search"
              placeholder="Search by employee name"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
          </span>
        </label>
      </div>

      <div className="attendance-stat-grid">
        <article className="attendance-stat">
          <span className="attendance-stat-icon attendance-stat-neutral">
            <Users size={19} />
          </span>
          <span className="attendance-stat-label">Employees shown</span>
          <strong>{filteredEmployees.length}</strong>
          <small>In current selection</small>
        </article>

        <article className="attendance-stat">
          <span className="attendance-stat-icon attendance-stat-green">
            <CheckCircle2 size={19} />
          </span>
          <span className="attendance-stat-label">Present</span>
          <strong>{counts.PRESENT}</strong>
          <small>Marked present</small>
        </article>

        <article className="attendance-stat">
          <span className="attendance-stat-icon attendance-stat-red">
            <XCircle size={19} />
          </span>
          <span className="attendance-stat-label">Absent</span>
          <strong>{counts.ABSENT}</strong>
          <small>Marked absent</small>
        </article>

        <article className="attendance-stat">
          <span className="attendance-stat-icon attendance-stat-blue">
            <Clock3 size={19} />
          </span>
          <span className="attendance-stat-label">Marked</span>
          <strong>{markedCount}/{filteredEmployees.length}</strong>
          <small>Completed entries</small>
        </article>
      </div>

      {error && (
        <div className="attendance-alert attendance-alert-error" role="alert">
          <XCircle size={18} />
          {error}
        </div>
      )}

      {message && (
        <div className="attendance-alert attendance-alert-success" role="status">
          <CheckCircle2 size={18} />
          <div>
            <strong>{message}</strong>
            {batchInfo && (
              <p>
                Batch #{batchInfo.batch_id}
                {batchInfo.closes_at
                  ? ` · Corrections close at ${new Date(
                      batchInfo.closes_at,
                    ).toLocaleString()}`
                  : ""}
              </p>
            )}
          </div>
        </div>
      )}

      <div className="attendance-table-panel">
        <div className="attendance-table-heading">
          <div>
            <h3>Daily employee records</h3>
            <p>
              {new Date(`${selectedDate}T00:00:00`).toLocaleDateString(
                undefined,
                {
                  weekday: "long",
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                },
              )}
            </p>
          </div>
          <span className="attendance-completion">
            {markedCount} of {filteredEmployees.length} marked
          </span>
        </div>

        {loading ? (
          <div className="attendance-empty">
            <RefreshCw size={22} />
            <p>Loading attendance records…</p>
          </div>
        ) : filteredEmployees.length === 0 ? (
          <div className="attendance-empty">
            <Users size={25} />
            <h3>No employees found</h3>
            <p>Try another department or search term.</p>
          </div>
        ) : (
          <div className="attendance-table-scroll">
            <table className="attendance-table">
              <thead>
                <tr>
                  <th>Employee</th>
                  <th>Department</th>
                  <th>Attendance status</th>
                  <th>Record state</th>
                </tr>
              </thead>
              <tbody>
                {filteredEmployees.map((employee) => {
                  const status = records[employee.id];

                  return (
                    <tr key={employee.id}>
                      <td>
                        <div className="attendance-employee">
                          <span className="attendance-avatar">
                            {employee.name
                              .split(/\s+/)
                              .slice(0, 2)
                              .map((part) => part[0]?.toUpperCase())
                              .join("")}
                          </span>
                          <span>
                            <strong>{employee.name}</strong>
                            <small>Employee #{employee.id}</small>
                          </span>
                        </div>
                      </td>

                      <td>{employee.department || "Unassigned"}</td>

                      <td>
                        <select
                          className="attendance-status-select"
                          aria-label={`Attendance status for ${employee.name}`}
                          value={status ?? ""}
                          onChange={(event) =>
                            updateStatus(employee.id, event.target.value)
                          }
                          disabled={uploading}
                        >
                          <option value="">Select status</option>
                          {statuses.map((item) => (
                            <option value={item} key={item}>
                              {statusLabels[item]}
                            </option>
                          ))}
                        </select>
                      </td>

                      <td>
                        <span
                          className={`attendance-record-state ${
                            savedIds.includes(employee.id)
                              ? "attendance-record-saved"
                              : status
                                ? "attendance-record-marked"
                                : "attendance-record-pending"
                          }`}
                        >
                          <span />
                          {savedIds.includes(employee.id)
                            ? "Previously saved"
                            : status
                              ? "Ready to upload"
                              : "Unmarked"}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        <div className="attendance-upload-footer">
          <div>
            <strong>Ready to publish?</strong>
            <p>
              All employees in the current selection must have a status.
            </p>
          </div>

          <button
            className="attendance-upload-button"
            type="button"
            onClick={() => void uploadAttendance()}
            disabled={
              loading ||
              uploading ||
              filteredEmployees.length === 0 ||
              markedCount !== filteredEmployees.length
            }
          >
            <UploadCloud size={18} />
            {uploading ? "Uploading…" : "Upload attendance"}
          </button>
        </div>
      </div>
    </section>
  );
}
