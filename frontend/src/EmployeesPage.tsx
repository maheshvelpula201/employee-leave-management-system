// frontend/src/EmployeesPage.tsx

import { useCallback, useEffect, useState } from 'react'
import { LoaderCircle, RefreshCw, Search, Users, Shield, Briefcase } from 'lucide-react'
import { apiRequest } from './lib/api'
import { getAccessToken } from './lib/auth'
import './EmployeesPage.css'

type StaffMember = {
  id: number
  user_id: number | null
  name: string
  email: string
  employee_id: string | null
  department: string | null
  designation: string | null
  phone: string | null
  category: 'Employee' | 'Manager' | 'HR'
  employment_status: string | null
  joining_date: string | null
}

export default function EmployeesPage() {
  const [staff, setStaff] = useState<StaffMember[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [categoryFilter, setCategoryFilter] = useState<string>('')
  const [departmentFilter, setDepartmentFilter] = useState('')

  const token = getAccessToken()

  const loadStaff = useCallback(async () => {
    if (!token) {
      setError('Session missing. Please sign in again.')
      setLoading(false)
      return
    }

    setLoading(true)
    setError('')

    try {
      const queryParams = new URLSearchParams()
      if (categoryFilter) queryParams.set('category', categoryFilter)
      if (search.trim()) queryParams.set('search', search.trim())
      if (departmentFilter.trim()) queryParams.set('department', departmentFilter.trim())

      const endpoint = `/staff/${queryParams.toString() ? `?${queryParams.toString()}` : ''}`
      const data = await apiRequest<StaffMember[]>(endpoint, { token })
      setStaff(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load staff directory.')
    } finally {
      setLoading(false)
    }
  }, [token, categoryFilter, search, departmentFilter])

  useEffect(() => {
    void loadStaff()
  }, [loadStaff])

  return (
    <div className="employees-page">
      <section className="employees-header">
        <div className="employees-header-icon">
          <Users size={24} />
        </div>
        <div>
          <h2>Company Staff Directory</h2>
          <p>View, search, and manage all real employee, manager, and HR profiles in your workspace.</p>
        </div>
      </section>

      {error && <p className="employees-message error" role="alert">{error}</p>}

      <section className="employees-controls">
        <div className="search-box">
          <Search size={18} />
          <input
            type="text"
            placeholder="Search by name, email, ID, or phone..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div className="filter-group">
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            aria-label="Filter by category"
          >
            <option value="">All Categories</option>
            <option value="Employee">Employees</option>
            <option value="Manager">Managers</option>
            <option value="HR">HR Personnel</option>
          </select>

          <input
            type="text"
            placeholder="Filter by department..."
            value={departmentFilter}
            onChange={(e) => setDepartmentFilter(e.target.value)}
          />

          <button
            className="refresh-btn"
            type="button"
            onClick={() => void loadStaff()}
            disabled={loading}
            aria-label="Refresh staff list"
          >
            <RefreshCw size={17} />
          </button>
        </div>
      </section>

      <section className="employees-content">
        {loading ? (
          <div className="employees-empty">
            <LoaderCircle className="spinner" size={26} />
            <p>Loading staff directory...</p>
          </div>
        ) : staff.length === 0 ? (
          <div className="employees-empty">
            <Users size={32} />
            <h3>No staff members found</h3>
            <p>Try adjusting your search filters or invite team members to join.</p>
          </div>
        ) : (
          <div className="table-wrap">
            <table className="employees-table">
              <thead>
                <tr>
                  <th>Name & Email</th>
                  <th>ID</th>
                  <th>Category</th>
                  <th>Department</th>
                  <th>Designation</th>
                  <th>Phone</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {staff.map((member) => (
                  <tr key={`${member.category}-${member.id}`}>
                    <td>
                      <div className="staff-name-cell">
                        <strong>{member.name}</strong>
                        <span>{member.email}</span>
                      </div>
                    </td>
                    <td><code>{member.employee_id ?? 'N/A'}</code></td>
                    <td>
                      <span className={`badge category-${member.category.toLowerCase()}`}>
                        {member.category === 'HR' && <Shield size={13} />}
                        {member.category === 'Manager' && <Briefcase size={13} />}
                        {member.category}
                      </span>
                    </td>
                    <td>{member.department || 'Unassigned'}</td>
                    <td>{member.designation || '—'}</td>
                    <td>{member.phone || '—'}</td>
                    <td>
                      <span className="badge status-active">
                        {member.employment_status || 'ACTIVE'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  )
}