
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
  Phone,
  CalendarDays,
  MapPin,
  ShieldCheck,
  ArrowLeft,
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
  leaving_date?: string | null
  termination_reason?: string | null
  manager_id: number | null
  floor?: string | null
  phone?: string | null
  emergency_contact_name?: string | null
  emergency_contact_phone?: string | null
  hr_id?: number | null
}

type HRMember = {
  id: number
  name: string
  email: string
}

type StaffCategory = 'EMPLOYEES' | 'HR' | 'MANAGERS'
type StatusFilter = 'ALL' | 'ACTIVE' | 'INACTIVE'
type StaffMember = Employee | HRMember

function isEmployeeRecord(person: StaffMember): person is Employee {
  return 'department' in person
}

function isManager(employee: Employee) {
  return (employee.designation ?? '').trim().toLowerCase() === 'manager'
}

function formatDate(value: string | null | undefined) {
  if (!value) return 'Not provided'

  const date = new Date(`${value.slice(0, 10)}T00:00:00`)

  return Number.isNaN(date.getTime())
    ? 'Not provided'
    : date.toLocaleDateString()
}

function getInitial(name: string) {
  return name.trim().charAt(0).toUpperCase() || '?'
}

export default function EmployeesPage() {
  const [employees, setEmployees] = useState<Employee[]>([])
  const [hrMembers, setHrMembers] = useState<HRMember[]>([])
  const [category, setCategory] = useState<StaffCategory>('EMPLOYEES')
  const [selectedPerson, setSelectedPerson] = useState<StaffMember | null>(null)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('ALL')
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState('')

  const loadStaff = useCallback(async (manualRefresh = false) => {
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
      const [employeeResult, hrResult] = await Promise.allSettled([
        apiRequest<Employee[]>('/employees/', { token }),
        apiRequest<HRMember[]>('/hr/', { token }),
      ])

      let employeeError = ''
      let hrError = ''

      if (employeeResult.status === 'fulfilled') {
        if (Array.isArray(employeeResult.value)) {
          setEmployees(employeeResult.value)
        } else {
          employeeError = 'The server returned an unexpected employee list.'
        }
      } else {
        employeeError =
          employeeResult.reason instanceof Error
            ? employeeResult.reason.message
            : 'Could not load employee records.'
      }

      if (hrResult.status === 'fulfilled') {
        if (Array.isArray(hrResult.value)) {
          setHrMembers(hrResult.value)
        } else {
          hrError = 'The server returned an unexpected HR list.'
        }
      } else {
        hrError =
          hrResult.reason instanceof Error
            ? hrResult.reason.message
            : 'Could not load HR records.'
      }

      if (employeeError && hrError) {
        setError(
          `Could not load staff records. Employees: ${employeeError} HR: ${hrError}`,
        )
      } else if (category === 'HR' && hrError) {
        setError(hrError)
      } else if (category !== 'HR' && employeeError) {
        setError(employeeError)
      } else if (employeeError || hrError) {
        setError(
          'Some staff records could not be loaded. Switch categories or refresh to try again.',
        )
      }
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [category])

  useEffect(() => {
    void loadStaff()
  }, [loadStaff])

  const employeeRecords = useMemo(
    () => employees.filter((employee) => !isManager(employee)),
    [employees],
  )

  const managerRecords = useMemo(
    () => employees.filter(isManager),
    [employees],
  )

  const visiblePeople: StaffMember[] = useMemo(() => {
    if (category === 'HR') return hrMembers
    if (category === 'MANAGERS') return managerRecords
    return employeeRecords
  }, [category, employeeRecords, hrMembers, managerRecords])

  const filteredPeople = useMemo(() => {
    const query = search.trim().toLowerCase()

    return visiblePeople.filter((person) => {
      const matchesSearch =
        !query ||
        person.name.toLowerCase().includes(query) ||
        person.email.toLowerCase().includes(query) ||
        (isEmployeeRecord(person) &&
          ((person.department ?? '').toLowerCase().includes(query) ||
            (person.designation ?? '').toLowerCase().includes(query)))

      if (!isEmployeeRecord(person)) return matchesSearch

      const status = (person.employment_status || 'ACTIVE').toUpperCase()
      const matchesStatus =
        statusFilter === 'ALL' || status === statusFilter

      return matchesSearch && matchesStatus
    })
  }, [visiblePeople, search, statusFilter])

  const categoryCount =
    category === 'HR'
      ? hrMembers.length
      : category === 'MANAGERS'
        ? managerRecords.length
        : employeeRecords.length

  const categoryLabel =
    category === 'HR'
      ? 'HR'
      : category === 'MANAGERS'
        ? 'Managers'
        : 'Employees'

  return (
    <main className="employees-page">
      <section className="employees-heading">
        <div>
          <p className="employees-eyebrow">PEOPLE MANAGEMENT</p>
          <h1>Staff directory</h1>
          <p className="employees-subtitle">
            Find employees, HR members, and managers in your company.
            Staff records are loaded from your company database.
          </p>
        </div>

        <button
          className="employees-refresh-button"
          type="button"
          onClick={() => void loadStaff(true)}
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

      <section className="employees-summary" aria-label="Staff totals">
        <article className="employees-summary-card">
          <div className="employees-summary-icon total">
            <Users size={21} />
          </div>
          <div>
            <p>Employees</p>
            <strong>{loading ? '—' : employeeRecords.length}</strong>
          </div>
        </article>

        <article className="employees-summary-card">
          <div className="employees-summary-icon active">
            <ShieldCheck size={21} />
          </div>
          <div>
            <p>HR members</p>
            <strong>{loading ? '—' : hrMembers.length}</strong>
          </div>
        </article>

        <article className="employees-summary-card">
          <div className="employees-summary-icon inactive">
            <UserRound size={21} />
          </div>
          <div>
            <p>Managers</p>
            <strong>{loading ? '—' : managerRecords.length}</strong>
          </div>
        </article>
      </section>

      <section className="employees-directory-panel">
        <div className="employees-panel-heading">
          <div>
            <h2>Company staff</h2>
            <p>
              {loading
                ? 'Loading company records...'
                : `${filteredPeople.length} ${categoryLabel.toLowerCase()} shown`}
            </p>
          </div>
        </div>

        <div
          className="staff-category-tabs"
          role="tablist"
          aria-label="Staff category"
        >
          <button
            type="button"
            role="tab"
            aria-selected={category === 'EMPLOYEES'}
            className={category === 'EMPLOYEES' ? 'active' : ''}
            onClick={() => {
              setCategory('EMPLOYEES')
              setSelectedPerson(null)
              setStatusFilter('ALL')
              setError('')
            }}
          >
            <Users size={16} />
            Employees
            <span>{loading ? '—' : employeeRecords.length}</span>
          </button>

          <button
            type="button"
            role="tab"
            aria-selected={category === 'HR'}
            className={category === 'HR' ? 'active' : ''}
            onClick={() => {
              setCategory('HR')
              setSelectedPerson(null)
              setStatusFilter('ALL')
              setError('')
            }}
          >
            <ShieldCheck size={16} />
            HR
            <span>{loading ? '—' : hrMembers.length}</span>
          </button>

          <button
            type="button"
            role="tab"
            aria-selected={category === 'MANAGERS'}
            className={category === 'MANAGERS' ? 'active' : ''}
            onClick={() => {
              setCategory('MANAGERS')
              setSelectedPerson(null)
              setStatusFilter('ALL')
              setError('')
            }}
          >
            <UserRound size={16} />
            Managers
            <span>{loading ? '—' : managerRecords.length}</span>
          </button>
        </div>

        {selectedPerson ? (
          <section className="staff-detail-view" aria-label="Staff member details">
            <button
              type="button"
              className="staff-back-button"
              onClick={() => setSelectedPerson(null)}
            >
              <ArrowLeft size={17} />
              Back to {categoryLabel}
            </button>

            <div className="staff-detail-header">
              <div className="staff-detail-avatar">
                {getInitial(selectedPerson.name)}
              </div>
              <div className="staff-detail-heading">
                <p className="employees-eyebrow">
                  {isEmployeeRecord(selectedPerson)
                    ? isManager(selectedPerson)
                      ? 'MANAGER PROFILE'
                      : 'EMPLOYEE PROFILE'
                    : 'HR PROFILE'}
                </p>
                <h2>{selectedPerson.name}</h2>
                <p>{selectedPerson.email}</p>
              </div>

              <div className="staff-id-card">
                <span>
                  {isEmployeeRecord(selectedPerson) ? 'EMPLOYEE ID' : 'HR ID'}
                </span>
                <strong>{selectedPerson.id}</strong>
              </div>
            </div>

            <div className="staff-detail-grid">
              <article className="staff-detail-item">
                <span><Mail size={16} /> Email</span>
                <strong>{selectedPerson.email || 'Not provided'}</strong>
              </article>

              {isEmployeeRecord(selectedPerson) ? (
                <>
                  <article className="staff-detail-item">
                    <span><Building2 size={16} /> Department</span>
                    <strong>{selectedPerson.department || 'Not assigned'}</strong>
                  </article>

                  <article className="staff-detail-item">
                    <span><BriefcaseBusiness size={16} /> Designation</span>
                    <strong>{selectedPerson.designation || 'Not assigned'}</strong>
                  </article>

                  <article className="staff-detail-item">
                    <span><MapPin size={16} /> Floor</span>
                    <strong>{selectedPerson.floor || 'Not provided'}</strong>
                  </article>

                  <article className="staff-detail-item">
                    <span><CalendarDays size={16} /> Joining date</span>
                    <strong>{formatDate(selectedPerson.joining_date)}</strong>
                  </article>

                  <article className="staff-detail-item">
                    <span><Phone size={16} /> Phone</span>
                    <strong>{selectedPerson.phone || 'Not provided'}</strong>
                  </article>

                  <article className="staff-detail-item">
                    <span><ShieldCheck size={16} /> Employment status</span>
                    <strong>
                      {(selectedPerson.employment_status || 'ACTIVE').toUpperCase()}
                    </strong>
                  </article>

                  <article className="staff-detail-item">
                    <span><UserRound size={16} /> Manager record ID</span>
                    <strong>{selectedPerson.manager_id ?? 'Not assigned'}</strong>
                  </article>

                  <article className="staff-detail-item">
                    <span><UserRound size={16} /> Emergency contact</span>
                    <strong>
                      {selectedPerson.emergency_contact_name || 'Not provided'}
                    </strong>
                  </article>

                  <article className="staff-detail-item">
                    <span><Phone size={16} /> Emergency contact phone</span>
                    <strong>
                      {selectedPerson.emergency_contact_phone || 'Not provided'}
                    </strong>
                  </article>
                </>
              ) : (
                <article className="staff-detail-item">
                  <span><ShieldCheck size={16} /> Staff category</span>
                  <strong>Human Resources</strong>
                </article>
              )}
            </div>

            <p className="staff-detail-note">
              Details not yet provided in the profile are shown as “Not provided”
              or “Not assigned”.
            </p>
          </section>
        ) : (
          <>
            <div className="employees-toolbar">
              <label className="employees-search">
                <Search size={18} />
                <input
                  type="search"
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                  placeholder="Search name, email, department..."
                  aria-label="Search staff"
                />
              </label>

              {category !== 'HR' && (
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
              )}
            </div>

            {error && (
              <div className="employees-message error" role="alert">
                <AlertCircle size={19} />
                <span>{error}</span>
                <button type="button" onClick={() => void loadStaff(true)}>
                  Try again
                </button>
              </div>
            )}

            {loading ? (
              <div className="employees-state">
                <LoaderCircle className="employees-spinner" size={28} />
                <p>Loading staff records...</p>
              </div>
            ) : error ? (
              <div className="employees-state">
                <AlertCircle size={30} />
                <h3>Could not load {categoryLabel.toLowerCase()}</h3>
                <p>Check the API response and your account permissions, then try again.</p>
                <button type="button" onClick={() => void loadStaff(true)}>
                  Try again
                </button>
              </div>
            ) : categoryCount === 0 ? (
              <div className="employees-state">
                <Users size={32} />
                <h3>No {categoryLabel.toLowerCase()} records yet</h3>
                <p>
                  Records created for your company will appear here when they
                  are available in the database.
                </p>
              </div>
            ) : filteredPeople.length === 0 ? (
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
            ) : (
              <div className="employees-table-wrap">
                <table className="employees-table">
                  <thead>
                    <tr>
                      <th>{category === 'HR' ? 'HR member' : 'Staff member'}</th>
                      {category !== 'HR' && (
                        <>
                          <th>Department</th>
                          <th>Designation</th>
                          <th>Joining date</th>
                          <th>Status</th>
                        </>
                      )}
                      <th>Details</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredPeople.map((person) => (
                      <tr
                        key={`${category}-${person.id}`}
                        className="staff-clickable-row"
                        onClick={() => setSelectedPerson(person)}
                      >
                        <td>
                          <div className="employees-person">
                            <div className="employees-avatar">
                              {getInitial(person.name)}
                            </div>
                            <div className="employees-person-details">
                              <strong>{person.name}</strong>
                              <span>
                                <Mail size={13} />
                                {person.email}
                              </span>
                              {isEmployeeRecord(person) && (
                                <small>Employee ID: {person.id}</small>
                              )}
                            </div>
                          </div>
                        </td>

                        {category !== 'HR' && isEmployeeRecord(person) && (
                          <>
                            <td>
                              <span className="employees-detail">
                                <Building2 size={15} />
                                {person.department || 'Not assigned'}
                              </span>
                            </td>
                            <td>
                              <span className="employees-detail">
                                <BriefcaseBusiness size={15} />
                                {person.designation || 'Not assigned'}
                              </span>
                            </td>
                            <td>{formatDate(person.joining_date)}</td>
                            <td>
                              <span
                                className={`employees-status ${
                                  (person.employment_status || 'ACTIVE').toLowerCase()
                                }`}
                              >
                                <span className="employees-status-dot" />
                                {(person.employment_status || 'ACTIVE').toUpperCase()}
                              </span>
                            </td>
                          </>
                        )}

                        <td>
                          <button
                            className="staff-view-button"
                            type="button"
                            onClick={(event) => {
                              event.stopPropagation()
                              setSelectedPerson(person)
                            }}
                          >
                            View details
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </section>
    </main>
  )
}
