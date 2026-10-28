
import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  RefreshCw,
  Search,
  Users,
  UserRound,
  Mail,
  Building2,
  BriefcaseBusiness,
  LoaderCircle,
  AlertCircle,
} from 'lucide-react'
import { apiRequest } from './lib/api'
import { getAccessToken } from './lib/auth'
import './EmployeesPage.css'

type Employee = {
  id: number
  name: string
  email: string
  department: string
  designation: string | null
  employment_status: string
  joining_date: string | null
  manager_id: number | null
}

type StatusFilter = 'ALL' | 'ACTIVE' | 'INACTIVE'

export default function EmployeesPage() {
  const [employees, setEmployees] = useState<Employee[]>([])
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('ALL')
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState('')

  const loadEmployees = useCallback(async (manualRefresh = false) => {
    const token = getAccessToken()

    if (!token) {
      setError('Your session is missing. Please sign in again.')
      setLoading(false)
      setRefreshing(false)
      return
    }

    if (manualRefresh) {
      setRefreshing(true)
    } else {
      setLoading(true)
    }

    setError('')

    try {
      const data = await apiRequest<Employee[]>('/employees/', { token })

      if (!Array.isArray(data)) {
        throw new Error('The server returned an unexpected employee list.')
      }

      setEmployees(data)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Could not load employees. Please try again.',
      )
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [])

  useEffect(() => {
    void loadEmployees()
  }, [loadEmployees])

  const filteredEmployees = useMemo(() => {
    const query = search.trim().toLowerCase()

    return employees.filter((employee) => {
      const matchesSearch =
        !query ||
        employee.name.toLowerCase().includes(query) ||
        employee.email.toLowerCase().includes(query) ||
        employee.department.toLowerCase().includes(query) ||
        (employee.designation ?? '').toLowerCase().includes(query)

      const status = (employee.employment_status || 'ACTIVE').toUpperCase()
      const matchesStatus =
        statusFilter === 'ALL' || status === statusFilter

      return matchesSearch && matchesStatus
    })
  }, [employees, search, statusFilter])

  const activeCount = employees.filter(
    (employee) =>
      (employee.employment_status || 'ACTIVE').toUpperCase() === 'ACTIVE',
  ).length

  const inactiveCount = employees.filter(
    (employee) =>
      (employee.employment_status || '').toUpperCase() === 'INACTIVE',
  ).length

  return (
    <main className="employees-page">
      <section className="employees-heading">
        <div>
          <p className="employees-eyebrow">PEOPLE MANAGEMENT</p>
          <h1>Employee directory</h1>
          <p className="employees-subtitle">
            View and find the employees and managers in your company.
            Records are loaded from your company database.
          </p>
        </div>

        <button
          className="employees-refresh-button"
          type="button"
          onClick={() => void loadEmployees(true)}
          disabled={loading || refreshing}
        >
          {refreshing ? (
            <LoaderCircle className="employees-spinner" size={17} />
          ) : (
            <RefreshCw size={17} />
          )}
          {refreshing ? 'Refreshing...' : 'Refresh'}
        </button>
      </section>

      <section className="employees-summary" aria-label="Employee totals">
        <article className="employees-summary-card">
          <div className="employees-summary-icon total">
            <Users size={21} />
          </div>
          <div>
            <p>Total records</p>
            <strong>{loading ? '—' : employees.length}</strong>
          </div>
        </article>

        <article className="employees-summary-card">
          <div className="employees-summary-icon active">
            <UserRound size={21} />
          </div>
          <div>
            <p>Active</p>
            <strong>{loading ? '—' : activeCount}</strong>
          </div>
        </article>

        <article className="employees-summary-card">
          <div className="employees-summary-icon inactive">
            <Users size={21} />
          </div>
          <div>
            <p>Inactive</p>
            <strong>{loading ? '—' : inactiveCount}</strong>
          </div>
        </article>
      </section>

      <section className="employees-directory-panel">
        <div className="employees-panel-heading">
          <div>
            <h2>Company people</h2>
            <p>
              {loading
                ? 'Loading company records...'
                : `${filteredEmployees.length} of ${employees.length} records`}
            </p>
          </div>
        </div>

        <div className="employees-toolbar">
          <label className="employees-search">
            <Search size={18} />
            <input
              type="search"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search name, email, department..."
              aria-label="Search employees"
            />
          </label>

          <select
            className="employees-status-filter"
            value={statusFilter}
            onChange={(event) =>
              setStatusFilter(event.target.value as StatusFilter)
            }
            aria-label="Filter by employment status"
          >
            <option value="ALL">All statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="INACTIVE">Inactive</option>
          </select>
        </div>

        {error && (
          <div className="employees-message error" role="alert">
            <AlertCircle size={19} />
            <span>{error}</span>
            <button type="button" onClick={() => void loadEmployees(true)}>
              Try again
            </button>
          </div>
        )}

        {loading ? (
          <div className="employees-state">
            <LoaderCircle className="employees-spinner" size={28} />
            <p>Loading employee records...</p>
          </div>
        ) : !error && employees.length === 0 ? (
          <div className="employees-state">
            <Users size={32} />
            <h3>No employee records yet</h3>
            <p>
              When an employee or manager completes registration through an
              invitation, their employee record will appear here.
            </p>
          </div>
        ) : !error && filteredEmployees.length === 0 ? (
          <div className="employees-state">
            <Search size={30} />
            <h3>No matching records</h3>
            <p>Try a different search or change the status filter.</p>
            <button
              type="button"
              onClick={() => {
                setSearch('')
                setStatusFilter('ALL')
              }}
            >
              Clear filters
            </button>
          </div>
        ) : !error ? (
          <div className="employees-table-wrap">
            <table className="employees-table">
              <thead>
                <tr>
                  <th>Employee</th>
                  <th>Department</th>
                  <th>Designation</th>
                  <th>Joining date</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {filteredEmployees.map((employee) => {
                  const status = (
                    employee.employment_status || 'ACTIVE'
                  ).toUpperCase()

                  return (
                    <tr key={employee.id}>
                      <td>
                        <div className="employees-person">
                          <div className="employees-avatar">
                            {employee.name.trim().charAt(0).toUpperCase() || '?'}
                          </div>
                          <div className="employees-person-details">
                            <strong>{employee.name}</strong>
                            <span>
                              <Mail size={13} />
                              {employee.email}
                            </span>
                            <small>Employee ID: {employee.id}</small>
                          </div>
                        </div>
                      </td>
                      <td>
                        <span className="employees-detail">
                          <Building2 size={15} />
                          {employee.department || 'Not assigned'}
                        </span>
                      </td>
                      <td>
                        <span className="employees-detail">
                          <BriefcaseBusiness size={15} />
                          {employee.designation || 'Not assigned'}
                        </span>
                      </td>
                      <td>
                        {employee.joining_date
                          ? new Date(
                              `${employee.joining_date.slice(0, 10)}T00:00:00`,
                            ).toLocaleDateString()
                          : '—'}
                      </td>
                      <td>
                        <span
                          className={`employees-status ${status.toLowerCase()}`}
                        >
                          <span className="employees-status-dot" />
                          {status}
                        </span>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        ) : null}
      </section>
    </main>
  )
}
