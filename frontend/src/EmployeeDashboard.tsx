
import { useState } from 'react'
import {
  CalendarDays,
  Clock,
  FileText,
  LogOut,
  ShieldCheck,
  UserRound,
} from 'lucide-react'
import { getCurrentUser, logoutLocal } from './lib/auth'
import { apiRequest } from './lib/api'
import './EmployeeDashboard.css'

type EmployeeDashboardProps = {
  onLogout: () => void
}

export default function EmployeeDashboard({
  onLogout,
}: EmployeeDashboardProps) {
  const user = getCurrentUser()
  const [loggingOut, setLoggingOut] = useState(false)
  const [logoutError, setLogoutError] = useState('')

  async function handleLogout() {
    if (loggingOut) return

    setLoggingOut(true)
    setLogoutError('')

    const refreshToken = sessionStorage.getItem('hr_refresh_token')

    try {
      if (refreshToken) {
        await apiRequest('/auth/logout', {
          method: 'POST',
          body: { refresh_token: refreshToken },
        })
      }
    } catch (error) {
      setLogoutError(
        error instanceof Error
          ? `Server logout failed: ${error.message}`
          : 'Server logout failed.',
      )
    } finally {
      logoutLocal()
      onLogout()
    }
  }

  return (
    <div className="employee-shell">
      <header className="employee-topbar">
        <div className="employee-brand">
          <div className="employee-brand-icon">
            <ShieldCheck size={22} />
          </div>
          <div>
            <h2>Northstar</h2>
            <span>EMPLOYEE WORKSPACE</span>
          </div>
        </div>

        <button
          className="employee-logout"
          type="button"
          onClick={handleLogout}
          disabled={loggingOut}
        >
          <LogOut size={17} />
          {loggingOut ? 'Signing out...' : 'Sign out'}
        </button>
      </header>

      <main className="employee-content">
        <section className="employee-welcome">
          <p className="employee-eyebrow">YOUR WORKSPACE</p>
          <h1>
            Welcome, {user?.name || 'Employee'}!
          </h1>
          <p>
            Your personal workspace for leave requests and work-related
            information.
          </p>
        </section>

        <section className="employee-profile-card">
          <div className="employee-profile-icon">
            <UserRound size={25} />
          </div>
          <div className="employee-profile-info">
            <h2>{user?.name || 'Employee'}</h2>
            <p>{user?.email || 'Email unavailable'}</p>
            <span className="employee-role-badge">
              {user?.role || 'EMPLOYEE'}
            </span>
          </div>
        </section>

        <section className="employee-section">
          <div className="employee-section-heading">
            <h2>Your workspace</h2>
            <p>Everything you need to get started.</p>
          </div>

          <div className="employee-feature-grid">
            <article className="employee-feature-card">
              <div className="employee-feature-icon">
                <CalendarDays size={22} />
              </div>
              <h3>Apply for leave</h3>
              <p>
                Submit a leave request when you need time off.
              </p>
              <span className="employee-feature-status">
                Coming next
              </span>
            </article>

            <article className="employee-feature-card">
              <div className="employee-feature-icon">
                <Clock size={22} />
              </div>
              <h3>Leave status</h3>
              <p>
                View your submitted requests and approval decisions.
              </p>
              <span className="employee-feature-status">
                Coming next
              </span>
            </article>

            <article className="employee-feature-card">
              <div className="employee-feature-icon">
                <FileText size={22} />
              </div>
              <h3>Leave balance</h3>
              <p>
                Check your available leave allowance and usage.
              </p>
              <span className="employee-feature-status">
                Coming next
              </span>
            </article>
          </div>
        </section>

        <footer className="employee-footer">
          Northstar · Employee workspace
        </footer>

        {logoutError && (
          <p className="employee-logout-error" role="status">
            {logoutError}
          </p>
        )}
      </main>
    </div>
  )
}
