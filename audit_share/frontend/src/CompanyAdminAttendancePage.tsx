
import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  Activity,
  AlertCircle,
  CalendarDays,
  Check,
  CheckCircle2,
  Clock3,
  Download,
  RefreshCw,
  Search,
  ShieldCheck,
  Upload,
  Users,
  X,
} from 'lucide-react'
import { apiRequest } from './lib/api'
import './CompanyAdminAttendancePage.css'

type AttendanceStatus =
  | 'PRESENT'
  | 'ABSENT'
  | 'LATE'
  | 'HALF_DAY'
  | 'ON_LEAVE'
  | 'WORK_FROM_HOME'
  | 'HOLIDAY'
  | 'WEEK_OFF'

type Employee = {
  id: number
  name: string
  department?: string | null
  email?: string | null
}

type AttendanceRecord = {
  id?: number
  employee_id: number
  status: AttendanceStatus
  attendance_date?: string
  employee_name?: string
  batch_id?: number | null
}

type AttendanceResponse = {
  items?: AttendanceRecord[]
  records?: AttendanceRecord[]
  batch_id?: number | null
  uploaded_at?: string | null
  closes_at?: string | null
  is_locked?: boolean
}

const statuses: AttendanceStatus[] = [
  'PRESENT',
  'ABSENT',
  'LATE',
  'HALF_DAY',
  'ON_LEAVE',
  'WORK_FROM_HOME',
  'HOLIDAY',
  'WEEK_OFF',
]

const statusLabels: Record<AttendanceStatus, string> = {
  PRESENT: 'Present',
  ABSENT: 'Absent',
  LATE: 'Late',
  HALF_DAY: 'Half day',
  ON_LEAVE: 'On leave',
  WORK_FROM_HOME: 'Work from home',
  HOLIDAY: 'Holiday',
  WEEK_OFF: 'Week off',
}

function asArray<T>(value: unknown): T[] {
  if (Array.isArray(value)) return value as T[]

  if (value && typeof value === 'object') {
    const data = value as { items?: unknown; employees?: unknown; records?: unknown }

    if (Array.isArray(data.items)) return data.items as T[]
    if (Array.isArray(data.employees)) return data.employees as T[]
    if (Array.isArray(data.records)) return data.records as T[]
  }

  return []
}

function getErrorMessage(error: unknown) {
  return error instanceof Error ? error.message : 'Something went wrong.'
}

function todayString() {
  const now = new Date()
  const localDate = new Date(now.getTime() - now.getTimezoneOffset() * 60000)
  return localDate.toISOString().slice(0, 10)
}

function formatDate(date: string) {
  if (!date) return '—'

  return new Date(`${date}T00:00:00`).toLocaleDateString(undefined, {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

function formatDateTime(value?: string | null) {
  if (!value) return '—'

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) return value

  return date.toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  })
}

export default function CompanyAdminAttendancePage() {
  const [employees, setEmployees] = useState<Employee[]>([])
  const [records, setRecords] = useState<AttendanceRecord[]>([])
  const [selectedDate, setSelectedDate] = useState(todayString())
  const [department, setDepartment] = useState('ALL')
  const [search, setSearch] = useState('')
  const [draftStatuses, setDraftStatuses] = useState<Record<number, AttendanceStatus>>({})
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [reopening, setReopening] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [showReopenDialog, setShowReopenDialog] = useState(false)
  const [reopenReason, setReopenReason] = useState('')
  const [uploadInfo, setUploadInfo] = useState<AttendanceResponse | null>(null)

  const loadData = useCallback(async () => {
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      const [employeeResult, attendanceResult] = await Promise.all([
        apiRequest<unknown>('/employees/'),
        apiRequest<unknown>(
          `/attendance/?attendance_date=${encodeURIComponent(selectedDate)}`,
        ),
      ])

      const employeeList = asArray<Employee>(employeeResult)
      const attendanceData = attendanceResult as AttendanceResponse | AttendanceRecord[]

      const attendanceList = asArray<AttendanceRecord>(attendanceData)

      setEmployees(employeeList)
      setRecords(attendanceList)
      setDraftStatuses(
        Object.fromEntries(
          attendanceList.map((record) => [record.employee_id, record.status]),
        ),
      )

      if (!Array.isArray(attendanceData)) {
        setUploadInfo(attendanceData)
      } else {
        setUploadInfo(null)
      }
    } catch (err) {
      setError(
        `Unable to load company attendance. ${getErrorMessage(err)}`,
      )
    } finally {
      setLoading(false)
    }
  }, [selectedDate])

  useEffect(() => {
    void loadData()
  }, [loadData])

  const departments = useMemo(
    () =>
      Array.from(
        new Set(
          employees
            .map((employee) => employee.department?.trim())
            .filter((value): value is string => Boolean(value)),
        ),
      ).sort((a, b) => a.localeCompare(b)),
    [employees],
  )

  const filteredEmployees = useMemo(() => {
    const query = search.trim().toLowerCase()

    return employees.filter((employee) => {
      const matchesDepartment =
        department === 'ALL' || employee.department === department

      const matchesSearch =
        !query ||
        employee.name.toLowerCase().includes(query) ||
        String(employee.id).includes(query) ||
        (employee.email ?? '').toLowerCase().includes(query)

      return matchesDepartment && matchesSearch
    })
  }, [employees, department, search])

  const recordByEmployee = useMemo(
    () => new Map(records.map((record) => [record.employee_id, record])),
    [records],
  )

  const summary = useMemo(() => {
    const counts: Record<AttendanceStatus, number> = {
      PRESENT: 0,
      ABSENT: 0,
      LATE: 0,
      HALF_DAY: 0,
      ON_LEAVE: 0,
      WORK_FROM_HOME: 0,
      HOLIDAY: 0,
      WEEK_OFF: 0,
    }

    records.forEach((record) => {
      if (record.status in counts) counts[record.status] += 1
    })

    return counts
  }, [records])

  const markedCount = filteredEmployees.filter((employee) =>
    Boolean(draftStatuses[employee.id]),
  ).length

  const isComplete =
    employees.length > 0 &&
    employees.every((employee) => Boolean(draftStatuses[employee.id]))

  const batchId =
    uploadInfo?.batch_id ??
    records.find((record) => record.batch_id != null)?.batch_id ??
    null

  const handleStatusChange = (
    employeeId: number,
    status: AttendanceStatus,
  ) => {
    setDraftStatuses((previous) => ({
      ...previous,
      [employeeId]: status,
    }))
    setSuccess('')
  }

  const handleUpload = async () => {
    if (employees.length === 0) {
      setError('No employees were found for this company.')
      return
    }

    if (!isComplete) {
      setError('Mark attendance for every company employee before uploading.')
      return
    }

    const alreadyUploaded = records.length > 0

    if (alreadyUploaded) {
      setError(
        'Attendance records already exist for this date. Use the permitted correction workflow instead of uploading a second batch.',
      )
      return
    }

    setUploading(true)
    setError('')
    setSuccess('')

    try {
      const result = await apiRequest<AttendanceResponse>(
        '/attendance/upload',
        {
          method: 'POST',
          body: {
            attendance_date: selectedDate,
            entries: employees.map((employee) => ({
              employee_id: employee.id,
              status: draftStatuses[employee.id],
            })),
          },
        },
      )

      setUploadInfo(result)
      setSuccess('Attendance upload request completed successfully.')
      await loadData()
    } catch (err) {
      setError(
        `Attendance upload failed. ${getErrorMessage(err)}`,
      )
    } finally {
      setUploading(false)
    }
  }

  const handleReopen = async () => {
    if (!batchId) {
      setError('No attendance batch ID is available to reopen.')
      return
    }

    if (!reopenReason.trim()) {
      setError('Enter a reason before reopening this batch.')
      return
    }

    setReopening(true)
    setError('')
    setSuccess('')

    try {
      await apiRequest<unknown>(
        `/attendance/batches/${batchId}/reopen`,
        {
          method: 'POST',
          body: { reason: reopenReason.trim() },
        },
      )

      setShowReopenDialog(false)
      setReopenReason('')
      setSuccess('Reopen request completed successfully.')
      await loadData()
    } catch (err) {
      setError(`Unable to reopen attendance. ${getErrorMessage(err)}`)
    } finally {
      setReopening(false)
    }
  }

  const exportCsv = () => {
    const header = ['Employee ID', 'Employee Name', 'Department', 'Status']

    const rows = filteredEmployees.map((employee) => [
      employee.id,
      employee.name,
      employee.department ?? '',
      draftStatuses[employee.id]
        ? statusLabels[draftStatuses[employee.id]]
        : 'Not marked',
    ])

    const csv = [header, ...rows]
      .map((row) =>
        row
          .map((value) => `"${String(value).replace(/"/g, '""')}"`)
          .join(','),
      )
      .join('\r\n')

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')

    link.href = url
    link.download = `company-attendance-${selectedDate}.csv`
    link.click()

    URL.revokeObjectURL(url)
  }

  return (
    <div className="admin-attendance">
      <section className="admin-attendance-hero">
        <div>
          <div className="admin-attendance-eyebrow">
            <ShieldCheck size={15} />
            COMPANY-WIDE CONTROL
          </div>
          <h2>Attendance management</h2>
          <p>
            Monitor attendance across your company, review daily records,
            and manage authorized attendance batches.
          </p>
        </div>

        <div className="admin-attendance-hero-icon">
          <CalendarDays size={32} />
        </div>
      </section>

      {error && (
        <div className="admin-attendance-alert error" role="alert">
          <AlertCircle size={18} />
          <span>{error}</span>
          <button
            type="button"
            aria-label="Dismiss error"
            onClick={() => setError('')}
          >
            <X size={16} />
          </button>
        </div>
      )}

      {success && (
        <div className="admin-attendance-alert success" role="status">
          <CheckCircle2 size={18} />
          <span>{success}</span>
          <button
            type="button"
            aria-label="Dismiss message"
            onClick={() => setSuccess('')}
          >
            <X size={16} />
          </button>
        </div>
      )}

      <section className="admin-attendance-stats">
        <article className="admin-attendance-stat">
          <div className="admin-attendance-stat-top">
            <span>Total employees</span>
            <span className="admin-attendance-stat-icon green">
              <Users size={19} />
            </span>
          </div>
          <strong>{loading ? '—' : employees.length}</strong>
          <small>Company directory</small>
        </article>

        <article className="admin-attendance-stat">
          <div className="admin-attendance-stat-top">
            <span>Present</span>
            <span className="admin-attendance-stat-icon green">
              <CheckCircle2 size={19} />
            </span>
          </div>
          <strong>{loading ? '—' : summary.PRESENT}</strong>
          <small>Uploaded records</small>
        </article>

        <article className="admin-attendance-stat">
          <div className="admin-attendance-stat-top">
            <span>Absent</span>
            <span className="admin-attendance-stat-icon red">
              <Users size={19} />
            </span>
          </div>
          <strong>{loading ? '—' : summary.ABSENT}</strong>
          <small>Uploaded records</small>
        </article>

        <article className="admin-attendance-stat">
          <div className="admin-attendance-stat-top">
            <span>Late arrivals</span>
            <span className="admin-attendance-stat-icon amber">
              <Clock3 size={19} />
            </span>
          </div>
          <strong>{loading ? '—' : summary.LATE}</strong>
          <small>Uploaded records</small>
        </article>
      </section>

      <section className="admin-attendance-panel">
        <div className="admin-attendance-panel-heading">
          <div>
            <h3>Daily attendance register</h3>
            <p>Review employee attendance for a selected date.</p>
          </div>

          <div className="admin-attendance-actions">
            <button
              type="button"
              className="admin-attendance-secondary-button"
              onClick={exportCsv}
              disabled={filteredEmployees.length === 0}
            >
              <Download size={16} />
              Export CSV
            </button>

            <button
              type="button"
              className="admin-attendance-secondary-button"
              onClick={() => void loadData()}
              disabled={loading}
            >
              <RefreshCw size={16} className={loading ? 'spinning' : ''} />
              Refresh
            </button>
          </div>
        </div>

        <div className="admin-attendance-filters">
          <label className="admin-attendance-date">
            <span>Attendance date</span>
            <div>
              <CalendarDays size={17} />
              <input
                type="date"
                value={selectedDate}
                onChange={(event) => setSelectedDate(event.target.value)}
              />
            </div>
          </label>

          <label className="admin-attendance-department">
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

          <label className="admin-attendance-search">
            <span>Search employees</span>
            <div>
              <Search size={17} />
              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Name, ID, or email"
              />
            </div>
          </label>
        </div>

        <div className="admin-attendance-table-meta">
          <span>
            Showing <strong>{filteredEmployees.length}</strong> employees
          </span>
          <span>
            {records.length > 0
              ? `${records.length} saved attendance records`
              : `${markedCount} of ${filteredEmployees.length} currently marked`}
          </span>
        </div>

        <div className="admin-attendance-table-wrap">
          <table className="admin-attendance-table">
            <thead>
              <tr>
                <th>Employee</th>
                <th>Department</th>
                <th>Saved status</th>
                <th>Attendance status</th>
              </tr>
            </thead>

            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={4} className="admin-attendance-empty">
                    Loading company attendance…
                  </td>
                </tr>
              ) : filteredEmployees.length === 0 ? (
                <tr>
                  <td colSpan={4} className="admin-attendance-empty">
                    No employees match these filters.
                  </td>
                </tr>
              ) : (
                filteredEmployees.map((employee) => {
                  const saved = recordByEmployee.get(employee.id)
                  const currentStatus = draftStatuses[employee.id]

                  return (
                    <tr key={employee.id}>
                      <td>
                        <div className="admin-attendance-employee">
                          <span className="admin-attendance-avatar">
                            {employee.name
                              .split(/\s+/)
                              .slice(0, 2)
                              .map((part) => part.charAt(0).toUpperCase())
                              .join('')}
                          </span>
                          <span>
                            <strong>{employee.name}</strong>
                            <small>
                              {employee.email || `Employee #${employee.id}`}
                            </small>
                          </span>
                        </div>
                      </td>

                      <td>{employee.department || 'Unassigned'}</td>

                      <td>
                        {saved ? (
                          <span
                            className={`admin-attendance-status ${saved.status.toLowerCase()}`}
                          >
                            {statusLabels[saved.status] ?? saved.status}
                          </span>
                        ) : (
                          <span className="admin-attendance-not-marked">
                            Not uploaded
                          </span>
                        )}
                      </td>

                      <td>
                        <select
                          className="admin-attendance-status-select"
                          value={currentStatus || ''}
                          onChange={(event) =>
                            handleStatusChange(
                              employee.id,
                              event.target.value as AttendanceStatus,
                            )
                          }
                          disabled={Boolean(saved)}
                          aria-label={`Attendance status for ${employee.name}`}
                        >
                          <option value="" disabled>
                            Select status
                          </option>
                          {statuses.map((status) => (
                            <option key={status} value={status}>
                              {statusLabels[status]}
                            </option>
                          ))}
                        </select>
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>

        <div className="admin-attendance-upload-bar">
          <div className="admin-attendance-upload-copy">
            <span className="admin-attendance-upload-icon">
              <Upload size={18} />
            </span>
            <span>
              <strong>Daily attendance upload</strong>
              <small>
                {records.length > 0
                  ? 'A batch already exists for this date. Use the authorized correction workflow.'
                  : `${employees.length > 0 && isComplete ? 'All employees are marked.' : 'Mark every company employee before uploading.'}`}
              </small>
            </span>
          </div>

          <button
            type="button"
            className="admin-attendance-primary-button"
            onClick={() => void handleUpload()}
            disabled={
              loading ||
              uploading ||
              records.length > 0 ||
              !isComplete ||
              employees.length === 0
            }
          >
            {uploading ? (
              <RefreshCw size={16} className="spinning" />
            ) : (
              <Upload size={16} />
            )}
            {uploading ? 'Uploading…' : 'Upload attendance'}
          </button>
        </div>
      </section>

      <section className="admin-attendance-panel admin-attendance-batch">
        <div className="admin-attendance-panel-heading">
          <div>
            <h3>Attendance batch control</h3>
            <p>
              Batch details and reopening availability depend on the backend
              response and your account permissions.
            </p>
          </div>
          <span className="admin-attendance-batch-icon">
            <ShieldCheck size={21} />
          </span>
        </div>

        <div className="admin-attendance-batch-details">
          <div>
            <span>Selected date</span>
            <strong>{formatDate(selectedDate)}</strong>
          </div>
          <div>
            <span>Batch ID</span>
            <strong>{batchId ?? 'Not available'}</strong>
          </div>
          <div>
            <span>Uploaded at</span>
            <strong>{formatDateTime(uploadInfo?.uploaded_at)}</strong>
          </div>
          <div>
            <span>Correction window closes</span>
            <strong>{formatDateTime(uploadInfo?.closes_at)}</strong>
          </div>
        </div>

        <div className="admin-attendance-reopen-bar">
          <div>
            <strong>Need to reopen a locked batch?</strong>
            <p>
              A reason is required. The server must verify Company Admin
              permission and record the audit event.
            </p>
          </div>
          <button
            type="button"
            className="admin-attendance-secondary-button"
            onClick={() => setShowReopenDialog(true)}
            disabled={!batchId || reopening}
          >
            <RefreshCw size={16} />
            Request reopening
          </button>
        </div>
      </section>

      {showReopenDialog && (
        <div
          className="admin-attendance-modal-backdrop"
          role="presentation"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) {
              setShowReopenDialog(false)
            }
          }}
        >
          <section
            className="admin-attendance-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="admin-reopen-title"
          >
            <div className="admin-attendance-modal-icon">
              <ShieldCheck size={23} />
            </div>
            <button
              type="button"
              className="admin-attendance-modal-close"
              aria-label="Close dialog"
              onClick={() => setShowReopenDialog(false)}
            >
              <X size={18} />
            </button>

            <h3 id="admin-reopen-title">Reopen attendance batch</h3>
            <p>
              Batch #{batchId}. Explain why this batch needs to be reopened.
              The backend must validate your permission and retain an audit
              trail.
            </p>

            <label className="admin-attendance-reason">
              <span>Reason for reopening</span>
              <textarea
                value={reopenReason}
                onChange={(event) => setReopenReason(event.target.value)}
                placeholder="Explain the required correction…"
                rows={4}
                maxLength={1000}
              />
            </label>

            <div className="admin-attendance-modal-actions">
              <button
                type="button"
                className="admin-attendance-secondary-button"
                onClick={() => setShowReopenDialog(false)}
                disabled={reopening}
              >
                Cancel
              </button>
              <button
                type="button"
                className="admin-attendance-primary-button"
                onClick={() => void handleReopen()}
                disabled={reopening || !reopenReason.trim()}
              >
                {reopening ? (
                  <RefreshCw size={16} className="spinning" />
                ) : (
                  <Check size={16} />
                )}
                {reopening ? 'Submitting…' : 'Submit request'}
              </button>
            </div>
          </section>
        </div>
      )}
    </div>
  )
}
