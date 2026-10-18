
import { useEffect, useState } from 'react'
import { CalendarDays, RefreshCw, Save } from 'lucide-react'
import { apiRequest } from './lib/api'

type Employee = {
  id: number
  name: string
  department?: string
}

type Status = 'PRESENT' | 'ABSENT' | 'HALF_DAY' | 'ON_LEAVE'

type Attendance = {
  id: number
  employee_id: number
  attendance_date: string
  status: Status
  notes?: string | null
}

const statuses: Status[] = [
  'PRESENT',
  'ABSENT',
  'HALF_DAY',
  'ON_LEAVE',
]

function todayLocal() {
  const now = new Date()
  const offset = now.getTimezoneOffset()
  return new Date(now.getTime() - offset * 60000)
    .toISOString()
    .slice(0, 10)
}

export default function AttendancePage() {
  const [selectedDate, setSelectedDate] = useState(todayLocal())
  const [employees, setEmployees] = useState<Employee[]>([])
  const [records, setRecords] = useState<Record<number, Status>>({})
  const [loading, setLoading] = useState(false)
  const [savingId, setSavingId] = useState<number | null>(null)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  async function loadAttendance() {
    setLoading(true)
    setError('')
    setMessage('')

    try {
      const [employeeData, attendanceData] = await Promise.all([
        apiRequest('/employees/'),
        apiRequest(`/attendance/?attendance_date=${selectedDate}`),
      ])

      const employeeList = Array.isArray(employeeData)
        ? employeeData
        : (employeeData as { items?: Employee[] }).items ?? []

      const attendanceList = Array.isArray(attendanceData)
        ? attendanceData as Attendance[]
        : []

      setEmployees(employeeList)

      const saved: Record<number, Status> = {}

      for (const record of attendanceList) {
        saved[record.employee_id] = record.status
      }

      // Keep saved records. New employees start unmarked.
      setRecords(saved)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Could not load attendance data.',
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadAttendance()
  }, [selectedDate])

  async function saveAttendance(employeeId: number) {
    const status = records[employeeId]

    if (!status) {
      setError('Choose an attendance status first.')
      return
    }

    setSavingId(employeeId)
    setError('')
    setMessage('')

    try {
      await apiRequest('/attendance/mark', {
        method: 'POST',
        body: {
          employee_id: employeeId,
          attendance_date: selectedDate,
          status,
        },
      })

      setMessage('Attendance saved successfully.')
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Could not save attendance.',
      )
    } finally {
      setSavingId(null)
    }
  }

  const counts = statuses.reduce(
    (result, status) => {
      result[status] = Object.values(records).filter(
        value => value === status,
      ).length
      return result
    },
    {} as Record<Status, number>,
  )

  return (
    <section className="attendance-page">
      <div className="attendance-toolbar">
        <div>
          <h2>Daily attendance</h2>
          <p>Review and update attendance for your employees.</p>
        </div>

        <button
          type="button"
          onClick={() => void loadAttendance()}
          disabled={loading}
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      <div className="attendance-date">
        <CalendarDays size={19} />
        <label htmlFor="attendance-date">Attendance date</label>
        <input
          id="attendance-date"
          type="date"
          value={selectedDate}
          onChange={event => setSelectedDate(event.target.value)}
        />
      </div>

      <div className="attendance-summary">
        <div><strong>{employees.length}</strong><span>Employees</span></div>
        <div><strong>{counts.PRESENT}</strong><span>Present</span></div>
        <div><strong>{counts.ABSENT}</strong><span>Absent</span></div>
        <div><strong>{counts.HALF_DAY}</strong><span>Half day</span></div>
        <div><strong>{counts.ON_LEAVE}</strong><span>On leave</span></div>
      </div>

      {error && <p role="alert" className="attendance-error">{error}</p>}
      {message && <p role="status" className="attendance-success">{message}</p>}

      {loading ? (
        <p>Loading live attendance data…</p>
      ) : employees.length === 0 ? (
        <p>No employees were returned by the employee API.</p>
      ) : (
        <div className="attendance-table-wrap">
          <table className="attendance-table">
            <thead>
              <tr>
                <th>Employee</th>
                <th>Department</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {employees.map(employee => (
                <tr key={employee.id}>
                  <td>
                    <strong>{employee.name}</strong>
                    <small>Employee #{employee.id}</small>
                  </td>
                  <td>{employee.department || '—'}</td>
                  <td>
                    <select
                      aria-label={`Attendance status for ${employee.name}`}
                      value={records[employee.id] ?? ''}
                      onChange={event => {
                        const value = event.target.value as Status | ''
                        setRecords(previous => {
                          const next = { ...previous }
                          if (value) next[employee.id] = value
                          else delete next[employee.id]
                          return next
                        })
                        setMessage('')
                      }}
                    >
                      <option value="">Select status</option>
                      {statuses.map(status => (
                        <option key={status} value={status}>
                          {status.replace('_', ' ')}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td>
                    <button
                      type="button"
                      onClick={() => void saveAttendance(employee.id)}
                      disabled={
                        !records[employee.id] ||
                        savingId === employee.id
                      }
                    >
                      <Save size={15} />
                      {savingId === employee.id ? 'Saving…' : 'Save'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
