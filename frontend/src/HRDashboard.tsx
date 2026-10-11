
import { useState } from "react";
import {
  Activity,
  ArrowUpRight,
  Bell,
  BriefcaseBusiness,
  CalendarDays,
  ChevronDown,
  ClipboardList,
  FileText,
  LayoutDashboard,
  LogOut,
  Menu,
  Plane,
  Search,
  Settings,
  Users,
  X,
  FolderKanban,
  MessageSquareText,
  ChartNoAxesCombined,
  Clock3,
  ShieldCheck,
} from "lucide-react";
import "./HRDashboard.css";

type HRModule =
  | "Dashboard"
  | "Employees"
  | "Attendance"
  | "Leaves"
  | "Employee Requests"
  | "Documents"
  | "Projects / Work"
  | "Trips"
  | "HR Posts"
  | "HR Analytics";

type HRDashboardProps = {
  onLogout?: () => void;
};

const navigation: {
  label: HRModule;
  icon: typeof LayoutDashboard;
}[] = [
  { label: "Dashboard", icon: LayoutDashboard },
  { label: "Employees", icon: Users },
  { label: "Attendance", icon: Clock3 },
  { label: "Leaves", icon: CalendarDays },
  { label: "Employee Requests", icon: ClipboardList },
  { label: "Documents", icon: FileText },
  { label: "Projects / Work", icon: FolderKanban },
  { label: "Trips", icon: Plane },
  { label: "HR Posts", icon: MessageSquareText },
  { label: "HR Analytics", icon: ChartNoAxesCombined },
];

const moduleDescriptions: Record<HRModule, string> = {
  Dashboard: "Your HR operations at a glance.",
  Employees: "Manage employee records and workforce information.",
  Attendance: "Review attendance records and daily work hours.",
  Leaves: "Review leave applications and their current status.",
  "Employee Requests":
    "Review employee requests and track their progress.",
  Documents: "Organize and manage employee documents.",
  "Projects / Work": "View projects, assignments, and work progress.",
  Trips: "Manage business trips and travel requests.",
  "HR Posts": "Publish company updates and employee announcements.",
  "HR Analytics": "Explore workforce metrics and HR trends.",
};

const overviewCards = [
  {
    label: "Total employees",
    value: "—",
    note: "Workforce overview",
    icon: Users,
    className: "hr-stat-green",
  },
  {
    label: "Present today",
    value: "—",
    note: "Attendance overview",
    icon: Clock3,
    className: "hr-stat-blue",
  },
  {
    label: "Pending leaves",
    value: "—",
    note: "Awaiting review",
    icon: CalendarDays,
    className: "hr-stat-amber",
  },
  {
    label: "Open requests",
    value: "—",
    note: "Requires attention",
    icon: ClipboardList,
    className: "hr-stat-purple",
  },
];

function HRDashboard({ onLogout }: HRDashboardProps) {
  const [activeModule, setActiveModule] =
    useState<HRModule>("Dashboard");
  const [searchTerm, setSearchTerm] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);

  const filteredNavigation = navigation.filter((item) =>
    item.label.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  function selectModule(module: HRModule) {
    setActiveModule(module);
    setSidebarOpen(false);
    setSearchTerm("");
  }

  return (
    <div className="hr-app">
      {sidebarOpen && (
        <button
          className="hr-mobile-overlay"
          aria-label="Close navigation"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside className={`hr-sidebar ${sidebarOpen ? "hr-sidebar-open" : ""}`}>
        <div className="hr-brand">
          <div className="hr-brand-mark">
            <ShieldCheck size={23} />
          </div>
          <div className="hr-brand-copy">
            <span className="hr-brand-name">Northstar</span>
            <span className="hr-brand-caption">PEOPLE OPERATIONS</span>
          </div>
          <button
            className="hr-icon-button hr-mobile-close"
            aria-label="Close navigation"
            onClick={() => setSidebarOpen(false)}
          >
            <X size={19} />
          </button>
        </div>

        <div className="hr-workspace">
          <span className="hr-workspace-dot" />
          <div>
            <p className="hr-workspace-name">Human Resources</p>
            <p className="hr-workspace-caption">HR workspace</p>
          </div>
          <ChevronDown size={15} />
        </div>

        <div className="hr-nav-heading">WORKSPACE</div>

        <nav className="hr-navigation" aria-label="HR navigation">
          {filteredNavigation.length > 0 ? (
            filteredNavigation.map((item) => {
              const Icon = item.icon;
              const isActive = activeModule === item.label;

              return (
                <button
                  key={item.label}
                  className={`hr-nav-item ${isActive ? "hr-nav-active" : ""}`}
                  onClick={() => selectModule(item.label)}
                  aria-current={isActive ? "page" : undefined}
                >
                  <Icon size={18} strokeWidth={1.8} />
                  <span>{item.label}</span>
                  {item.label === "Employee Requests" && (
                    <span className="hr-nav-indicator" />
                  )}
                </button>
              );
            })
          ) : (
            <p className="hr-empty-search">No matching modules found.</p>
          )}
        </nav>

        <div className="hr-sidebar-bottom">
          <div className="hr-help-card">
            <div className="hr-help-icon">
              <Activity size={18} />
            </div>
            <p className="hr-help-title">HR workspace</p>
            <p className="hr-help-text">
              Your tools for managing people and daily operations.
            </p>
          </div>

          <button
            className="hr-nav-item hr-settings-item"
            onClick={() => selectModule("HR Analytics")}
          >
            <Settings size={18} strokeWidth={1.8} />
            <span>Workspace insights</span>
          </button>

          {onLogout && (
            <button className="hr-nav-item hr-logout" onClick={onLogout}>
              <LogOut size={18} strokeWidth={1.8} />
              <span>Sign out</span>
            </button>
          )}
        </div>
      </aside>

      <main className="hr-main">
        <header className="hr-topbar">
          <div className="hr-topbar-left">
            <button
              className="hr-icon-button hr-menu-button"
              aria-label="Open navigation"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu size={21} />
            </button>
            <div className="hr-breadcrumb">
              <span>HR workspace</span>
              <span className="hr-breadcrumb-separator">/</span>
              <strong>{activeModule}</strong>
            </div>
          </div>

          <div className="hr-topbar-actions">
            <label className="hr-search">
              <Search size={17} />
              <input
                value={searchTerm}
                onChange={(event) => setSearchTerm(event.target.value)}
                onFocus={() => setSidebarOpen(false)}
                placeholder="Find a module..."
                aria-label="Search HR modules"
              />
              {searchTerm && (
                <button
                  type="button"
                  className="hr-search-clear"
                  aria-label="Clear search"
                  onClick={() => setSearchTerm("")}
                >
                  <X size={15} />
                </button>
              )}
            </label>

            <div className="hr-notification-wrap">
              <button
                className={`hr-icon-button ${notificationsOpen ? "hr-icon-selected" : ""}`}
                aria-label="Notifications"
                aria-expanded={notificationsOpen}
                onClick={() => setNotificationsOpen(!notificationsOpen)}
              >
                <Bell size={19} />
              </button>

              {notificationsOpen && (
                <div className="hr-notification-popover">
                  <div className="hr-popover-heading">
                    <strong>Notifications</strong>
                    <button
                      className="hr-icon-button"
                      aria-label="Close notifications"
                      onClick={() => setNotificationsOpen(false)}
                    >
                      <X size={16} />
                    </button>
                  </div>
                  <p>
                    Notifications will appear here when connected to the
                    backend.
                  </p>
                </div>
              )}
            </div>

            <div className="hr-profile">
              <div className="hr-avatar">HR</div>
              <div className="hr-profile-copy">
                <span className="hr-profile-name">HR Workspace</span>
                <span className="hr-profile-role">Human Resources</span>
              </div>
              <ChevronDown size={15} className="hr-profile-chevron" />
            </div>
          </div>
        </header>

        <div className="hr-content">
          <div className="hr-page-heading">
            <div>
              <div className="hr-eyebrow">
                <span className="hr-eyebrow-dot" />
                PEOPLE OPERATIONS
              </div>
              <h1>
                {activeModule === "Dashboard"
                  ? "HR overview"
                  : activeModule}
              </h1>
              <p>{moduleDescriptions[activeModule]}</p>
            </div>

            <div className="hr-heading-date">
              <CalendarDays size={16} />
              <span>Company workspace</span>
            </div>
          </div>

          {activeModule === "Dashboard" ? (
            <>
              <section className="hr-welcome-banner">
                <div className="hr-welcome-copy">
                  <span className="hr-welcome-label">YOUR WORKSPACE</span>
                  <h2>Good work starts with great people.</h2>
                  <p>
                    Keep track of your HR operations, employee activity,
                    and requests in one place.
                  </p>
                </div>
                <div className="hr-welcome-art" aria-hidden="true">
                  <div className="hr-art-ring hr-art-ring-one" />
                  <div className="hr-art-ring hr-art-ring-two" />
                  <div className="hr-art-square">
                    <Users size={42} strokeWidth={1.4} />
                  </div>
                  <div className="hr-art-dot hr-art-dot-one" />
                  <div className="hr-art-dot hr-art-dot-two" />
                </div>
              </section>

              <div className="hr-section-heading">
                <div>
                  <h2>Workforce snapshot</h2>
                  <p>Key indicators from your HR operations</p>
                </div>
                <span className="hr-live-label">
                  <span /> Data pending connection
                </span>
              </div>

              <section className="hr-stats-grid">
                {overviewCards.map((card) => {
                  const Icon = card.icon;

                  return (
                    <article className="hr-stat-card" key={card.label}>
                      <div className="hr-stat-top">
                        <span className="hr-stat-label">{card.label}</span>
                        <span className={`hr-stat-icon ${card.className}`}>
                          <Icon size={19} />
                        </span>
                      </div>
                      <div className="hr-stat-value">{card.value}</div>
                      <div className="hr-stat-bottom">
                        <span className="hr-stat-note">{card.note}</span>
                        <span className="hr-stat-neutral">
                          <Activity size={13} />
                          <span>—</span>
                        </span>
                      </div>
                    </article>
                  );
                })}
              </section>

              <section className="hr-lower-grid">
                <article className="hr-panel hr-operations-panel">
                  <div className="hr-panel-heading">
                    <div>
                      <h2>HR operations</h2>
                      <p>Quick access to your daily work</p>
                    </div>
                    <BriefcaseBusiness size={19} />
                  </div>

                  <div className="hr-quick-links">
                    {[
                      {
                        title: "Employee directory",
                        description: "Employee records and profiles",
                        icon: Users,
                        module: "Employees" as HRModule,
                      },
                      {
                        title: "Attendance",
                        description: "Daily presence and work hours",
                        icon: Clock3,
                        module: "Attendance" as HRModule,
                      },
                      {
                        title: "Leave management",
                        description: "Applications awaiting review",
                        icon: CalendarDays,
                        module: "Leaves" as HRModule,
                      },
                      {
                        title: "Employee requests",
                        description: "Review and track submissions",
                        icon: ClipboardList,
                        module: "Employee Requests" as HRModule,
                      },
                    ].map((item) => {
                      const Icon = item.icon;

                      return (
                        <button
                          className="hr-quick-link"
                          key={item.title}
                          onClick={() => selectModule(item.module)}
                        >
                          <span className="hr-quick-icon">
                            <Icon size={19} />
                          </span>
                          <span className="hr-quick-copy">
                            <strong>{item.title}</strong>
                            <span>{item.description}</span>
                          </span>
                          <ArrowUpRight size={17} className="hr-quick-arrow" />
                        </button>
                      );
                    })}
                  </div>
                </article>

                <article className="hr-panel hr-activity-panel">
                  <div className="hr-panel-heading">
                    <div>
                      <h2>Activity & updates</h2>
                      <p>Keep up with your HR workspace</p>
                    </div>
                    <Activity size={19} />
                  </div>

                  <div className="hr-empty-activity">
                    <div className="hr-empty-activity-icon">
                      <CalendarDays size={23} />
                    </div>
                    <h3>Nothing to show yet</h3>
                    <p>
                      Recent HR activity will appear here when your data
                      source is connected.
                    </p>
                  </div>
                </article>
              </section>

              <section className="hr-module-section">
                <div className="hr-section-heading">
                  <div>
                    <h2>Your HR modules</h2>
                    <p>Choose an area to continue working</p>
                  </div>
                </div>

                <div className="hr-module-grid">
                  {navigation
                    .filter((item) => item.label !== "Dashboard")
                    .map((item, index) => {
                      const Icon = item.icon;

                      return (
                        <button
                          className="hr-module-card"
                          key={item.label}
                          onClick={() => selectModule(item.label)}
                        >
                          <span className={`hr-module-icon hr-module-icon-${index % 4}`}>
                            <Icon size={20} />
                          </span>
                          <span className="hr-module-copy">
                            <strong>{item.label}</strong>
                            <span>{moduleDescriptions[item.label]}</span>
                          </span>
                          <ArrowUpRight size={17} className="hr-module-arrow" />
                        </button>
                      );
                    })}
                </div>
              </section>
            </>
          ) : (
            <section className="hr-module-placeholder">
              <div className="hr-placeholder-icon">
                {(() => {
                  const Icon =
                    navigation.find((item) => item.label === activeModule)?.icon ??
                    LayoutDashboard;
                  return <Icon size={30} strokeWidth={1.5} />;
                })()}
              </div>
              <span className="hr-placeholder-eyebrow">HR MODULE</span>
              <h2>{activeModule}</h2>
              <p>{moduleDescriptions[activeModule]}</p>
              <div className="hr-placeholder-divider" />
              <div className="hr-placeholder-status">
                <span className="hr-status-dot" />
                Module layout ready for implementation
              </div>
              <p className="hr-placeholder-footnote">
                This is the starting layout. We'll build this module's
                tables, forms, actions, and backend connection in the next
                steps.
              </p>
              <button
                className="hr-secondary-button"
                onClick={() => selectModule("Dashboard")}
              >
                <LayoutDashboard size={16} />
                Back to overview
              </button>
            </section>
          )}

          <footer className="hr-footer">
            <span>Northstar HR workspace</span>
            <span>People operations · Internal workspace</span>
          </footer>
        </div>
      </main>
    </div>
  );
}

export default HRDashboard;
