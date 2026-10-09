import { useState } from 'react'
import {
  Activity,
  ArrowUpRight,
  Bell,
  BriefcaseBusiness,
  CalendarDays,
  ChevronDown,
  CircleHelp,
  Command,
  FileText,
  LayoutDashboard,
  LogOut,
  Menu,
  Search,
  Settings,
  ShieldCheck,
  Users,
  X,
} from 'lucide-react'
import {
  NavLink,
  Navigate,
  Route,
  Routes,
  useLocation,
} from 'react-router-dom'
import LoginPage from './LoginPage'
import CompanyRegistrationPage from './CompanyRegistrationPage'
import {
  getAccessToken,
  getCurrentUser,
  logoutLocal,
} from './lib/auth'
import { apiRequest } from './lib/api'
import './App.css'

const navigation = [
  {
    title: 'WORKSPACE',
    items: [
      { label: 'Overview', path: '/', icon: LayoutDashboard },
      { label: 'Employees', path: '/employees', icon: Users },
      { label: 'Leave management', path: '/leaves', icon: CalendarDays },
      { label: 'Invitations', path: '/invitations', icon: FileText },
    ],
  },
  {
    title: 'ADMINISTRATION',
    items: [
      { label: 'Company settings', path: '/settings', icon: Settings },
    ],
  },
]

const pageDetails: Record<
  string,
  { eyebrow: string; title: string; description: string }
> = {
  '/': {
    eyebrow: 'YOUR WORKSPACE',
    title: 'Good to have you here.',
    description:
      'A clear view of your workplace starts here. Your live company information will appear once the backend is connected.',
  },
  '/employees': {
    eyebrow: 'PEOPLE',
    title: 'Employees',
    description:
      'Manage your company directory, employee details, and employment status.',
  },
  '/leaves': {
    eyebrow: 'TIME OFF',
    title: 'Leave management',
    description:
      'Review leave requests and manage time-off workflows using your company policies.',
  },
  '/invitations': {
    eyebrow: 'TEAM ACCESS',
    title: 'Invitations',
    description:
      'Invite colleagues to your workspace and track their invitation status.',
  },
  '/settings': {
    eyebrow: 'CONFIGURATION',
    title: 'Company settings',
    description:
      'Manage your workspace configuration and company information.',
  },
}


function App() {
  const [authenticated, setAuthenticated] = useState(
    () => Boolean(getAccessToken() && getCurrentUser()),
  )
  const [showRegistration, setShowRegistration] = useState(false)

  if (!authenticated) {
    if (showRegistration) {
      return (
        <CompanyRegistrationPage
          onBack={() => setShowRegistration(false)}
        />
      )
    }

    return (
      <LoginPage
        onLoginSuccess={() => setAuthenticated(true)}
        onCreateCompany={() => setShowRegistration(true)}
      />
    )
  }

  return (
    <DashboardApp
      onLogout={() => {
        logoutLocal()
        setAuthenticated(false)
      }}
    />
  )
}

function DashboardApp({ onLogout }: { onLogout: () => void }) {
  const [mobileNavOpen, setMobileNavOpen] = useState(false)
  const [logoutError, setLogoutError] = useState('')
  const [loggingOut, setLoggingOut] = useState(false)

  const location = useLocation()
  const currentPage = pageDetails[location.pathname] ?? pageDetails['/']
  const user = getCurrentUser()

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
      // Clear local credentials even if the server request fails.
      onLogout()
    }
  }

  return (
    <div className="app-shell">
      {mobileNavOpen && (
        <button
          className="mobile-overlay"
          aria-label="Close navigation"
          onClick={() => setMobileNavOpen(false)}
        />
      )}

      <aside className={`sidebar ${mobileNavOpen ? 'sidebar-open' : ''}`}>
        <div className="brand">
          <div className="brand-mark">
            <Command size={21} strokeWidth={2.2} />
          </div>
          <div className="brand-copy">
            <span className="brand-name">Northstar</span>
            <span className="brand-caption">PEOPLE OPERATIONS</span>
          </div>
          <button
            className="icon-button sidebar-close"
            onClick={() => setMobileNavOpen(false)}
            aria-label="Close sidebar"
          >
            <X size={19} />
          </button>
        </div>

        <button className="company-switcher" type="button">
          <div className="company-avatar">
            {user?.name?.charAt(0).toUpperCase() || 'A'}
          </div>
          <div className="company-copy">
            <span className="company-name">Your company</span>
            <span className="company-plan">Company workspace</span>
          </div>
          <ChevronDown size={16} className="company-chevron" />
        </button>

        <nav className="sidebar-navigation" aria-label="Main navigation">
          {navigation.map((group) => (
            <div className="nav-group" key={group.title}>
              <p className="nav-group-title">{group.title}</p>
              {group.items.map((item) => {
                const Icon = item.icon

                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    end={item.path === '/'}
                    onClick={() => setMobileNavOpen(false)}
                    className={({ isActive }) =>
                      `nav-link ${isActive ? 'nav-link-active' : ''}`
                    }
                  >
                    <Icon size={18} strokeWidth={1.8} />
                    <span>{item.label}</span>
                    {item.path === '/invitations' && (
                      <span
                        className="nav-link-indicator"
                        aria-hidden="true"
                      />
                    )}
                  </NavLink>
                )
              })}
            </div>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="help-card">
            <div className="help-icon">
              <CircleHelp size={18} />
            </div>
            <div>
              <p className="help-title">Need a hand?</p>
              <p className="help-description">Help with your workspace</p>
            </div>
          </div>

          <div className="sidebar-footer">
            <div className="profile-avatar">
              {user?.name
                ? user.name
                    .split(/\s+/)
                    .slice(0, 2)
                    .map((part) => part.charAt(0).toUpperCase())
                    .join('')
                : 'CA'}
            </div>
            <div className="profile-copy">
              <span className="profile-name">
                {user?.name || 'Company Admin'}
              </span>
              <span className="profile-role">
                {user?.role || 'Administrator'}
              </span>
            </div>
            <button
              className="icon-button profile-menu"
              type="button"
              aria-label="Sign out"
              title="Sign out"
              onClick={handleLogout}
              disabled={loggingOut}
            >
              <LogOut size={17} />
            </button>
          </div>

          {logoutError && (
            <p role="status" className="logout-error">
              {logoutError}
            </p>
          )}
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="topbar-left">
            <button
              className="icon-button mobile-menu"
              onClick={() => setMobileNavOpen(true)}
              aria-label="Open navigation"
            >
              <Menu size={21} />
            </button>
            <div className="breadcrumb">
              <span>Workspace</span>
              <span className="breadcrumb-divider">/</span>
              <strong>{currentPage.title}</strong>
            </div>
          </div>

          <div className="topbar-actions">
            <div className="environment-label">
              <span className="environment-dot" />
              Frontend preview
            </div>
            <button
              className="icon-button search-button"
              aria-label="Search"
              title="Search will be enabled when connected to backend data"
              type="button"
            >
              <Search size={19} />
            </button>
            <button
              className="icon-button notification-button"
              aria-label="Notifications"
              title="Notifications are not connected yet"
              type="button"
            >
              <Bell size={19} />
            </button>
            <div className="topbar-avatar">
              {user?.name?.charAt(0).toUpperCase() || 'A'}
            </div>
          </div>
        </header>

        <div className="page-container">
          <div className="page-heading">
            <div>
              <p className="eyebrow">{currentPage.eyebrow}</p>
              <h1>{currentPage.title}</h1>
              <p className="page-description">
                {currentPage.description}
              </p>
            </div>
            <div className="page-heading-meta">
              <ShieldCheck size={16} />
              <span>Designed for clarity</span>
            </div>
          </div>

          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route
              path="/employees"
              element={
                <FeaturePage
                  icon={Users}
                  title="Your employee directory"
                  description="Employee records will be loaded from the FastAPI employee endpoints."
                  endpoint="GET /employees/"
                />
              }
            />
            <Route
              path="/leaves"
              element={
                <FeaturePage
                  icon={CalendarDays}
                  title="Time-off workspace"
                  description="Leave requests and their current statuses will come from the leave API."
                  endpoint="GET /leaves/"
                />
              }
            />
            <Route
              path="/invitations"
              element={
                <FeaturePage
                  icon={FileText}
                  title="Bring your team together"
                  description="Your real invitations will appear here. We'll connect invitation creation and listing next."
                  endpoint="GET /invitations/"
                />
              }
            />
            <Route
              path="/settings"
              element={
                <FeaturePage
                  icon={Settings}
                  title="Your company, your workspace"
                  description="Company settings will use the capabilities currently available in your backend."
                  endpoint="Backend integration pending"
                />
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>

          <footer className="page-footer">
            <span>Northstar · People operations</span>
            <span className="footer-right">
              <Activity size={14} />
              Frontend foundation
            </span>
          </footer>
        </div>
      </main>
    </div>
  )
}

function DashboardPage() {
  return (
    <>
      <section className="welcome-panel">
        <div className="welcome-content">
          <div className="welcome-icon">
            <BriefcaseBusiness size={21} />
          </div>
          <div>
            <p className="welcome-kicker">A better way to work</p>
            <h2>Your people, in one place.</h2>
            <p>
              Keep employee information, leave workflows, and team access
              organized in a single workspace.
            </p>
          </div>
        </div>
        <div className="welcome-decoration" aria-hidden="true">
          <div className="decoration-ring ring-one" />
          <div className="decoration-ring ring-two" />
          <div className="decoration-dot" />
        </div>
      </section>

      <div className="section-heading">
        <div>
          <h2>Workspace at a glance</h2>
          <p>Your company metrics will appear here after connecting the API.</p>
        </div>
        <span className="data-state">
          <span className="data-state-dot" />
          Awaiting live data
        </span>
      </div>

      <section className="metric-grid" aria-label="Company metrics">
        <MetricCard
          label="Total employees"
          value="—"
          description="Awaiting employee records"
          icon={Users}
          trend="neutral"
        />
        <MetricCard
          label="Pending leave requests"
          value="—"
          description="Awaiting leave records"
          icon={CalendarDays}
          trend="neutral"
        />
        <MetricCard
          label="Open invitations"
          value="—"
          description="Awaiting invitation records"
          icon={FileText}
          trend="neutral"
        />
        <MetricCard
          label="Workspace status"
          value="—"
          description="Awaiting account verification"
          icon={ShieldCheck}
          trend="neutral"
        />
      </section>

      <section className="content-grid">
        <div className="panel activity-panel">
          <div className="panel-heading">
            <div>
              <h2>Recent activity</h2>
              <p>Changes across your company workspace</p>
            </div>
            <span className="panel-icon">
              <Activity size={18} />
            </span>
          </div>
          <div className="empty-state">
            <div className="empty-state-icon">
              <Activity size={22} />
            </div>
            <h3>Your activity will show up here</h3>
            <p>
              Once connected, this space can show real employee, invitation,
              and leave updates.
            </p>
          </div>
        </div>

        <div className="panel actions-panel">
          <div className="panel-heading">
            <div>
              <h2>Workspace essentials</h2>
              <p>Core areas of your people operations</p>
            </div>
          </div>
          <div className="essential-list">
            <EssentialRow
              icon={Users}
              title="Employee directory"
              description="People and employment details"
              to="/employees"
              tone="blue"
            />
            <EssentialRow
              icon={CalendarDays}
              title="Leave management"
              description="Requests and leave statuses"
              to="/leaves"
              tone="green"
            />
            <EssentialRow
              icon={FileText}
              title="Team invitations"
              description="Manage access to your workspace"
              to="/invitations"
              tone="violet"
            />
          </div>
        </div>
      </section>

      <section className="integration-notice">
        <div className="integration-icon">
          <ShieldCheck size={19} />
        </div>
        <div>
          <h3>Built around your real company data</h3>
          <p>
            This dashboard deliberately shows placeholders until the API
            supplies actual values. No sample metrics are presented as real.
          </p>
        </div>
      </section>
    </>
  )
}

function MetricCard({
  label,
  value,
  description,
  icon: Icon,
  trend,
}: {
  label: string
  value: string
  description: string
  icon: typeof Users
  trend: 'neutral'
}) {
  return (
    <article className="metric-card">
      <div className="metric-card-top">
        <span className="metric-label">{label}</span>
        <span className="metric-icon">
          <Icon size={18} strokeWidth={1.8} />
        </span>
      </div>
      <div className="metric-value">{value}</div>
      <div className={`metric-description ${trend}`}>
        <span className="metric-description-icon">
          <ArrowUpRight size={14} />
        </span>
        {description}
      </div>
    </article>
  )
}

function FeaturePage({
  icon: Icon,
  title,
  description,
  endpoint,
}: {
  icon: typeof Users
  title: string
  description: string
  endpoint: string
}) {
  return (
    <section className="feature-page-panel">
      <div className="feature-page-icon">
        <Icon size={25} strokeWidth={1.7} />
      </div>
      <h2>{title}</h2>
      <p>{description}</p>
      <div className="feature-endpoint">
        <span className="endpoint-dot" />
        <span>{endpoint}</span>
      </div>
      <div className="feature-divider" />
      <p className="feature-footnote">
        This page is part of the frontend foundation. Data loading, forms, and
        actions will be added after we verify the API contract and permissions.
      </p>
    </section>
  )
}

function EssentialRow({
  icon: Icon,
  title,
  description,
  to,
  tone,
}: {
  icon: typeof Users
  title: string
  description: string
  to: string
  tone: 'blue' | 'green' | 'violet'
}) {
  return (
    <NavLink className="essential-row" to={to}>
      <span className={`essential-icon ${tone}`}>
        <Icon size={18} />
      </span>
      <span className="essential-copy">
        <span className="essential-title">{title}</span>
        <span className="essential-description">{description}</span>
      </span>
      <ArrowUpRight className="essential-arrow" size={17} />
    </NavLink>
  )
}

export default App
