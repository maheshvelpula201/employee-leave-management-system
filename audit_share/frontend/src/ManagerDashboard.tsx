import { useState } from "react";
import {
  Activity,
  ArrowDownRight,
  ArrowRight,
  ArrowUpRight,
  Bell,
  BriefcaseBusiness,
  CalendarDays,
  Check,
  ChevronDown,
  CircleAlert,
  Clock3,
  Command,
  Download,
  Ellipsis,
  Flag,
  Gauge,
  LayoutDashboard,
  LogOut,
  Menu,
  MessageSquare,
  MoreHorizontal,
  Plus,
  Search,
  Settings2,
  ShieldCheck,
  Sparkles,
  Target,
  TrendingUp,
  Users,
  X,
  Zap,
  CheckCircle2,
  CircleDashed,
  FolderKanban,
  ClipboardList,
  BarChart3,
} from "lucide-react";
import "./ManagerDashboard.css";

type ManagerDashboardProps = {
  onLogout: () => void;
};

type ModuleName =
  | "Overview"
  | "My Team"
  | "Team Attendance"
  | "Team Leaves"
  | "Projects"
  | "Tasks & Work"
  | "Goals"
  | "Performance"
  | "Team Analytics";

const navigation: {
  label: ModuleName;
  icon: typeof LayoutDashboard;
  section: string;
}[] = [
  { label: "Overview", icon: LayoutDashboard, section: "WORKSPACE" },
  { label: "My Team", icon: Users, section: "PEOPLE" },
  { label: "Team Attendance", icon: CalendarDays, section: "PEOPLE" },
  { label: "Team Leaves", icon: Clock3, section: "PEOPLE" },
  { label: "Projects", icon: FolderKanban, section: "DELIVERY" },
  { label: "Tasks & Work", icon: ClipboardList, section: "DELIVERY" },
  { label: "Goals", icon: Target, section: "GROWTH" },
  { label: "Performance", icon: TrendingUp, section: "GROWTH" },
  { label: "Team Analytics", icon: BarChart3, section: "INSIGHTS" },
];

const team = [
  { name: "Aarav Sharma", role: "Frontend Engineer", initials: "AS", color: "lavender", status: "Available", project: "Atlas Redesign", score: 94 },
  { name: "Priya Nair", role: "Backend Engineer", initials: "PN", color: "mint", status: "Available", project: "Core Platform", score: 91 },
  { name: "Rahul Verma", role: "UI/UX Designer", initials: "RV", color: "peach", status: "In a meeting", project: "Atlas Redesign", score: 88 },
  { name: "Ananya Rao", role: "QA Engineer", initials: "AR", color: "blue", status: "On leave", project: "Mobile Release", score: 86 },
  { name: "Karthik Iyer", role: "Full Stack Developer", initials: "KI", color: "pink", status: "Available", project: "Core Platform", score: 92 },
];

const projects = [
  { name: "Atlas Redesign", category: "Product experience", progress: 78, color: "violet", due: "Oct 24", tasks: "18 / 24", status: "On track" },
  { name: "Core Platform", category: "Infrastructure", progress: 62, color: "blue", due: "Oct 29", tasks: "15 / 24", status: "In progress" },
  { name: "Mobile Release", category: "Mobile application", progress: 41, color: "orange", due: "Nov 04", tasks: "9 / 22", status: "Needs attention" },
];

const tasks = [
  { title: "Review authentication flow", project: "Core Platform", owner: "PN", priority: "High", due: "Today", done: false },
  { title: "Approve dashboard components", project: "Atlas Redesign", owner: "AS", priority: "Medium", due: "Today", done: false },
  { title: "Validate release checklist", project: "Mobile Release", owner: "AR", priority: "High", due: "Oct 14", done: false },
  { title: "Update API documentation", project: "Core Platform", owner: "KI", priority: "Low", due: "Oct 15", done: true },
];

const leaveRequests = [
  { id: 1, name: "Ananya Rao", initials: "AR", type: "Casual leave", dates: "Oct 13 – Oct 14", days: "2 days", color: "blue" },
  { id: 2, name: "Rahul Verma", initials: "RV", type: "Personal leave", dates: "Oct 16", days: "1 day", color: "peach" },
];

const weeklyWork = [
  { day: "Mon", value: 66 },
  { day: "Tue", value: 82 },
  { day: "Wed", value: 57 },
  { day: "Thu", value: 91 },
  { day: "Fri", value: 74 },
  { day: "Sat", value: 30 },
  { day: "Sun", value: 18 },
];

export default function ManagerDashboard({ onLogout }: ManagerDashboardProps) {
  const [activeModule, setActiveModule] = useState<ModuleName>("Overview");
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [completedTasks, setCompletedTasks] = useState<number[]>([3]);
  const [decisions, setDecisions] = useState<Record<number, "Approved" | "Declined">>({});
  const [notice, setNotice] = useState("");
  const [showProfile, setShowProfile] = useState(false);

  const pendingLeaves = leaveRequests.filter(
    (leave) => !decisions[leave.id]
  ).length;

  const filteredTeam = team.filter((member) =>
    `${member.name} ${member.role} ${member.project}`
      .toLowerCase()
      .includes(search.toLowerCase())
  );

  const handleModule = (module: ModuleName) => {
    setActiveModule(module);
    setMobileNavOpen(false);
    setNotice("");
  };

  const handleDecision = (id: number, decision: "Approved" | "Declined") => {
    setDecisions((current) => ({ ...current, [id]: decision }));
    setNotice(`Leave request ${decision.toLowerCase()} in this demo view.`);
  };

  const renderOverview = () => (
    <>
      <section className="md-welcome">
        <div className="md-welcome-copy">
          <div className="md-eyebrow"><Sparkles size={14} /> YOUR TEAM, IN FOCUS</div>
          <h1>Make good work<br /><span>happen together.</span></h1>
          <p>Your team's workspace for people, priorities, and progress.</p>
          <div className="md-welcome-actions">
            <button className="md-primary-button" onClick={() => handleModule("My Team")}>
              Explore my team <ArrowRight size={16} />
            </button>
            <button className="md-ghost-button" onClick={() => handleModule("Tasks & Work")}>
              View tasks
            </button>
          </div>
        </div>
        <div className="md-welcome-art" aria-hidden="true">
          <div className="md-orbit md-orbit-one" />
          <div className="md-orbit md-orbit-two" />
          <div className="md-art-core"><Command size={39} /></div>
          <div className="md-art-float md-art-float-top"><Zap size={17} /><span>In sync</span></div>
          <div className="md-art-float md-art-float-bottom"><Activity size={17} /><span>Moving forward</span></div>
          <div className="md-art-dot md-dot-one" />
          <div className="md-art-dot md-dot-two" />
        </div>
        <div className="md-welcome-index"><span>MANAGER WORKSPACE</span><span>01 / 09</span></div>
      </section>

      <section className="md-metric-grid">
        <article className="md-metric md-metric-primary">
          <div className="md-metric-top"><span>TEAM MEMBERS</span><Users size={17} /></div>
          <div className="md-metric-value">12 <span className="md-metric-change"><ArrowUpRight size={13} /> 2</span></div>
          <div className="md-metric-bottom">Across 3 active projects</div>
          <div className="md-avatar-stack">
            {team.slice(0, 4).map((member) => <span key={member.initials} className={`md-avatar md-avatar-${member.color}`}>{member.initials}</span>)}
            <span className="md-avatar md-avatar-more">+7</span>
          </div>
        </article>
        <article className="md-metric">
          <div className="md-metric-top"><span>AVAILABLE TODAY</span><span className="md-status-dot" /></div>
          <div className="md-metric-value">09 <span className="md-metric-unit">/ 12</span></div>
          <div className="md-metric-bottom">3 members unavailable</div>
          <div className="md-mini-track"><span style={{ width: "75%" }} /></div>
        </article>
        <article className="md-metric">
          <div className="md-metric-top"><span>OPEN TASKS</span><ClipboardList size={17} /></div>
          <div className="md-metric-value">24 <span className="md-metric-change md-change-neutral">8 due soon</span></div>
          <div className="md-metric-bottom">Across all team projects</div>
          <div className="md-mini-track md-track-blue"><span style={{ width: "58%" }} /></div>
        </article>
        <article className="md-metric">
          <div className="md-metric-top"><span>GOAL PROGRESS</span><Target size={17} /></div>
          <div className="md-metric-value">76<span className="md-metric-unit">%</span></div>
          <div className="md-metric-bottom">Quarterly team objectives</div>
          <div className="md-mini-track md-track-green"><span style={{ width: "76%" }} /></div>
        </article>
      </section>

      <section className="md-main-grid">
        <article className="md-panel md-project-panel">
          <div className="md-panel-heading">
            <div><span className="md-section-kicker">DELIVERY PULSE</span><h2>Projects in motion</h2></div>
            <button className="md-text-button" onClick={() => handleModule("Projects")}>All projects <ArrowRight size={14} /></button>
          </div>
          <div className="md-project-list">
            {projects.map((project, index) => (
              <div className="md-project-row" key={project.name}>
                <div className={`md-project-symbol md-symbol-${project.color}`}>
                  {index === 0 ? <Command size={19} /> : index === 1 ? <ShieldCheck size={19} /> : <Zap size={19} />}
                </div>
                <div className="md-project-main">
                  <div className="md-project-name-row"><strong>{project.name}</strong><span className={`md-project-state md-state-${project.color}`}>{project.status}</span></div>
                  <span className="md-project-category">{project.category}</span>
                  <div className="md-project-progress"><span className={`md-fill-${project.color}`} style={{ width: `${project.progress}%` }} /></div>
                  <div className="md-project-foot"><span>{project.tasks} tasks</span><span>{project.progress}% complete</span><span>Due {project.due}</span></div>
                </div>
                <button className="md-icon-button md-project-more" aria-label={`View ${project.name}`} onClick={() => handleModule("Projects")}><ArrowUpRight size={17} /></button>
              </div>
            ))}
          </div>
        </article>

        <article className="md-panel md-attendance-panel">
          <div className="md-panel-heading">
            <div><span className="md-section-kicker">PEOPLE PULSE</span><h2>Today's presence</h2></div>
            <button className="md-icon-button" aria-label="View attendance" onClick={() => handleModule("Team Attendance")}><ArrowUpRight size={17} /></button>
          </div>
          <div className="md-presence-summary">
            <div className="md-presence-ring"><div><strong>75%</strong><span>present</span></div></div>
            <div className="md-presence-legend">
              <span><i className="md-legend-green" />Present <b>9</b></span>
              <span><i className="md-legend-violet" />On leave <b>2</b></span>
              <span><i className="md-legend-amber" />Away <b>1</b></span>
            </div>
          </div>
          <div className="md-panel-divider" />
          <button className="md-inline-link" onClick={() => handleModule("Team Attendance")}>Open attendance report <ArrowRight size={15} /></button>
        </article>
      </section>

      <section className="md-main-grid md-lower-grid">
        <article className="md-panel md-task-panel">
          <div className="md-panel-heading">
            <div><span className="md-section-kicker">NEXT UP</span><h2>Work that needs you</h2></div>
            <button className="md-text-button" onClick={() => handleModule("Tasks & Work")}>View all <ArrowRight size={14} /></button>
          </div>
          <div className="md-task-list">
            {tasks.slice(0, 3).map((task, index) => (
              <label className={`md-task-row ${completedTasks.includes(index) ? "md-task-done" : ""}`} key={task.title}>
                <input type="checkbox" checked={completedTasks.includes(index)} onChange={() => setCompletedTasks((current) => current.includes(index) ? current.filter((n) => n !== index) : [...current, index])} />
                <span className="md-custom-check"><Check size={13} /></span>
                <span className="md-task-content"><strong>{task.title}</strong><small>{task.project} · Due {task.due}</small></span>
                <span className={`md-priority md-priority-${task.priority.toLowerCase()}`}>{task.priority}</span>
              </label>
            ))}
          </div>
        </article>

        <article className="md-panel md-leave-panel">
          <div className="md-panel-heading">
            <div><span className="md-section-kicker">ACTION REQUIRED</span><h2>Leave requests <span className="md-count-badge">{pendingLeaves}</span></h2></div>
            <button className="md-icon-button" aria-label="View all leave requests" onClick={() => handleModule("Team Leaves")}><ArrowUpRight size={17} /></button>
          </div>
          {leaveRequests.filter((leave) => !decisions[leave.id]).length === 0 ? (
            <div className="md-empty-state"><CheckCircle2 size={24} /><strong>All caught up</strong><span>No pending demo requests.</span></div>
          ) : leaveRequests.filter((leave) => !decisions[leave.id]).map((leave) => (
            <div className="md-leave-row" key={leave.id}>
              <span className={`md-avatar md-avatar-${leave.color}`}>{leave.initials}</span>
              <div className="md-leave-info"><strong>{leave.name}</strong><span>{leave.type} · {leave.days}</span><small>{leave.dates}</small></div>
              <div className="md-leave-actions">
                <button className="md-approve-button" aria-label={`Approve ${leave.name}`} onClick={() => handleDecision(leave.id, "Approved")}><Check size={15} /></button>
                <button className="md-decline-button" aria-label={`Decline ${leave.name}`} onClick={() => handleDecision(leave.id, "Declined")}><X size={15} /></button>
              </div>
            </div>
          ))}
          <button className="md-inline-link" onClick={() => handleModule("Team Leaves")}>Manage leave requests <ArrowRight size={15} /></button>
        </article>
      </section>

      <section className="md-panel md-analytics-panel">
        <div className="md-panel-heading">
          <div><span className="md-section-kicker">TEAM ANALYTICS</span><h2>Momentum through the week</h2><p className="md-panel-subtitle">Illustrative work activity index · not live system data</p></div>
          <button className="md-text-button" onClick={() => handleModule("Team Analytics")}>Deep dive <ArrowRight size={14} /></button>
        </div>
        <div className="md-chart">
          {weeklyWork.map((item) => (
            <div className="md-chart-column" key={item.day}>
              <span className="md-chart-value">{item.value}</span>
              <div className="md-chart-track"><span style={{ height: `${item.value}%` }} /></div>
              <span className="md-chart-day">{item.day}</span>
            </div>
          ))}
        </div>
      </section>

      <div className="md-bottom-note"><Sparkles size={15} /><span>Great teams don't just deliver. They make room for each other to do their best work.</span></div>
    </>
  );

  const renderTeam = () => (
    <section className="md-panel md-module-panel">
      <div className="md-panel-heading"><div><span className="md-section-kicker">PEOPLE DIRECTORY</span><h2>Meet your team</h2><p className="md-panel-subtitle">Find team members and see their current focus.</p></div><span className="md-module-total">{filteredTeam.length} people</span></div>
      <div className="md-module-search"><Search size={17} /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search people, roles or projects..." /></div>
      <div className="md-table-wrap"><table className="md-table"><thead><tr><th>TEAM MEMBER</th><th>CURRENT PROJECT</th><th>AVAILABILITY</th><th>PERFORMANCE</th><th /></tr></thead><tbody>
        {filteredTeam.map((member) => <tr key={member.initials}><td><div className="md-table-person"><span className={`md-avatar md-avatar-${member.color}`}>{member.initials}</span><span><strong>{member.name}</strong><small>{member.role}</small></span></div></td><td>{member.project}</td><td><span className={`md-member-status md-member-${member.status.toLowerCase().replace(" ", "-")}`}><i />{member.status}</span></td><td><div className="md-score"><span>{member.score}</span><div><i style={{ width: `${member.score}%` }} /></div></div></td><td><button className="md-icon-button" aria-label={`View ${member.name}`} onClick={() => setNotice(`${member.name}: ${member.role}.`)}><ArrowUpRight size={16} /></button></td></tr>)}
      </tbody></table></div>
      {filteredTeam.length === 0 && <div className="md-empty-state">No team members match that search.</div>}
    </section>
  );

  const renderModule = () => {
    if (activeModule === "Overview") return renderOverview();
    if (activeModule === "My Team") return renderTeam();

    if (activeModule === "Team Attendance") return (
      <section className="md-panel md-module-panel"><div className="md-panel-heading"><div><span className="md-section-kicker">PEOPLE / PRESENCE</span><h2>Team attendance</h2><p className="md-panel-subtitle">A quick view of today's team availability.</p></div><CalendarDays size={22} /></div><div className="md-attendance-cards"><div><span>Present</span><strong>9</strong><small>75% of team</small></div><div><span>On leave</span><strong>2</strong><small>Approved absence</small></div><div><span>Other / away</span><strong>1</strong><small>Check availability</small></div></div><div className="md-panel-divider" /><div className="md-empty-state"><CalendarDays size={25} /><strong>Attendance detail</strong><span>Connect your attendance API to display actual check-in and check-out records here.</span></div></section>
    );

    if (activeModule === "Team Leaves") return (
      <section className="md-panel md-module-panel"><div className="md-panel-heading"><div><span className="md-section-kicker">PEOPLE / TIME OFF</span><h2>Team leave requests</h2><p className="md-panel-subtitle">Review requests in this local demo view.</p></div><span className="md-module-total">{pendingLeaves} pending</span></div>
        {leaveRequests.map((leave) => <div className="md-leave-row md-leave-module-row" key={leave.id}><span className={`md-avatar md-avatar-${leave.color}`}>{leave.initials}</span><div className="md-leave-info"><strong>{leave.name}</strong><span>{leave.type} · {leave.days}</span><small>{leave.dates}</small></div>{decisions[leave.id] ? <span className={`md-decision md-decision-${decisions[leave.id].toLowerCase()}`}>{decisions[leave.id]}</span> : <div className="md-leave-actions"><button className="md-approve-button" onClick={() => handleDecision(leave.id, "Approved")}><Check size={15} /> Approve</button><button className="md-decline-button" onClick={() => handleDecision(leave.id, "Declined")}><X size={15} /> Decline</button></div>}</div>)}
        <p className="md-demo-notice"><CircleAlert size={15} /> Demo interactions only. Decisions here are not saved to the backend.</p>
      </section>
    );

    if (activeModule === "Projects") return (
      <section className="md-module-project-grid">{projects.map((project, index) => <article className="md-panel md-project-card" key={project.name}><div className={`md-project-symbol md-symbol-${project.color}`}>{index === 0 ? <Command size={21} /> : index === 1 ? <ShieldCheck size={21} /> : <Zap size={21} />}</div><span className={`md-project-state md-state-${project.color}`}>{project.status}</span><h2>{project.name}</h2><p>{project.category}</p><div className="md-project-progress md-card-progress"><span className={`md-fill-${project.color}`} style={{ width: `${project.progress}%` }} /></div><div className="md-project-foot"><span>{project.tasks} tasks</span><strong>{project.progress}%</strong></div><div className="md-panel-divider" /><div className="md-project-card-bottom"><span><CalendarDays size={14} /> Due {project.due}</span><button className="md-icon-button" onClick={() => setNotice(`${project.name} selected. Connect project APIs for details.`)}><ArrowUpRight size={17} /></button></div></article>)}</section>
    );

    if (activeModule === "Tasks & Work") return (
      <section className="md-panel md-module-panel"><div className="md-panel-heading"><div><span className="md-section-kicker">DELIVERY / EXECUTION</span><h2>Tasks & work</h2><p className="md-panel-subtitle">Track priorities and mark demo tasks complete.</p></div><span className="md-module-total">{tasks.length} tasks</span></div><div className="md-task-list md-full-task-list">{tasks.map((task, index) => <label className={`md-task-row ${completedTasks.includes(index) ? "md-task-done" : ""}`} key={task.title}><input type="checkbox" checked={completedTasks.includes(index)} onChange={() => setCompletedTasks((current) => current.includes(index) ? current.filter((n) => n !== index) : [...current, index])} /><span className="md-custom-check"><Check size={13} /></span><span className="md-task-content"><strong>{task.title}</strong><small>{task.project} · Owner {task.owner} · Due {task.due}</small></span><span className={`md-priority md-priority-${task.priority.toLowerCase()}`}>{task.priority}</span></label>)}</div><p className="md-demo-notice"><CircleAlert size={15} /> Task completion is local to this page until connected to your API.</p></section>
    );

    if (activeModule === "Goals") return (
      <section className="md-panel md-module-panel"><div className="md-panel-heading"><div><span className="md-section-kicker">GROWTH / OBJECTIVES</span><h2>Quarterly goals</h2><p className="md-panel-subtitle">Example objectives for a team planning review.</p></div><Target size={22} /></div>{[{ name: "Improve release reliability", owner: "Engineering", progress: 82 }, { name: "Reduce review turnaround", owner: "Entire team", progress: 68 }, { name: "Ship the new product experience", owner: "Product & Design", progress: 76 }, { name: "Strengthen automated test coverage", owner: "Quality engineering", progress: 54 }].map((goal) => <div className="md-goal-row" key={goal.name}><div className="md-goal-info"><div><strong>{goal.name}</strong><span>{goal.owner}</span></div><b>{goal.progress}%</b></div><div className="md-project-progress"><span style={{ width: `${goal.progress}%` }} /></div></div>)}<p className="md-demo-notice"><CircleAlert size={15} /> Illustrative goals. Connect the goals API to show company records.</p></section>
    );

    if (activeModule === "Performance") return (
      <section className="md-panel md-module-panel"><div className="md-panel-heading"><div><span className="md-section-kicker">GROWTH / RECOGNITION</span><h2>Team performance</h2><p className="md-panel-subtitle">Illustrative indicators to support constructive check-ins.</p></div><TrendingUp size={22} /></div>{team.map((member) => <div className="md-performance-row" key={member.initials}><span className={`md-avatar md-avatar-${member.color}`}>{member.initials}</span><div className="md-performance-info"><strong>{member.name}</strong><span>{member.role}</span></div><div className="md-score"><span>{member.score}/100</span><div><i style={{ width: `${member.score}%` }} /></div></div><span className="md-performance-trend"><ArrowUpRight size={15} /> Positive</span></div>)}<p className="md-demo-notice"><CircleAlert size={15} /> Sample indicators, not official employee performance ratings.</p></section>
    );

    return (
      <section className="md-panel md-module-panel"><div className="md-panel-heading"><div><span className="md-section-kicker">INSIGHTS / TRENDS</span><h2>Team analytics</h2><p className="md-panel-subtitle">Illustrative activity index across the week.</p></div><BarChart3 size={22} /></div><div className="md-analytics-summary"><div><span>Weekly activity</span><strong>68.3</strong><small><ArrowUpRight size={14} /> Illustrative index</small></div><div><span>Goal progress</span><strong>76%</strong><small>Quarterly objectives</small></div><div><span>Active projects</span><strong>03</strong><small>Example project set</small></div></div><div className="md-chart md-module-chart">{weeklyWork.map((item) => <div className="md-chart-column" key={item.day}><span className="md-chart-value">{item.value}</span><div className="md-chart-track"><span style={{ height: `${item.value}%` }} /></div><span className="md-chart-day">{item.day}</span></div>)}</div><p className="md-demo-notice"><CircleAlert size={15} /> Sample analytics only. No real attendance or productivity data is being calculated.</p></section>
    );
  };

  return (
    <div className="md-shell">
      {mobileNavOpen && <button className="md-mobile-scrim" aria-label="Close navigation" onClick={() => setMobileNavOpen(false)} />}
      <aside className={`md-sidebar ${mobileNavOpen ? "md-sidebar-open" : ""}`}>
        <div className="md-brand">
          <div className="md-brand-mark"><Command size={22} /></div>
          <div className="md-brand-name"><strong>nexora</strong><span>PEOPLE OPERATIONS</span></div>
          <button className="md-mobile-close" aria-label="Close navigation" onClick={() => setMobileNavOpen(false)}><X size={19} /></button>
        </div>

        <button className="md-workspace-switch" onClick={() => setShowProfile((value) => !value)}>
          <span className="md-workspace-icon">W</span><span className="md-workspace-text"><strong>Workspace</strong><small>Team operations</small></span><ChevronDown size={15} />
        </button>
        {showProfile && <div className="md-workspace-menu"><strong>Manager workspace</strong><span>People · Projects · Goals</span></div>}

        <div className="md-nav-scroll">
          {["WORKSPACE", "PEOPLE", "DELIVERY", "GROWTH", "INSIGHTS"].map((section) => (
            <div className="md-nav-section" key={section}>
              <span className="md-nav-label">{section}</span>
              {navigation.filter((item) => item.section === section).map((item) => {
                const Icon = item.icon;
                return <button key={item.label} className={`md-nav-item ${activeModule === item.label ? "md-nav-active" : ""}`} onClick={() => handleModule(item.label)}><Icon size={18} strokeWidth={1.8} /><span>{item.label}</span>{item.label === "Team Leaves" && pendingLeaves > 0 && <span className="md-nav-count">{pendingLeaves}</span>}{activeModule === item.label && <span className="md-nav-indicator" />}</button>;
              })}
            </div>
          ))}
        </div>

        <div className="md-sidebar-bottom">
          <div className="md-help-card"><div className="md-help-icon"><MessageSquare size={17} /></div><strong>Need a hand?</strong><span>Your people ops toolkit, all in one place.</span><button onClick={() => setNotice("Help center can be connected to your support resources.")}>Explore help <ArrowRight size={14} /></button></div>
          <button className="md-nav-item md-settings-link" onClick={() => setNotice("Settings are not connected yet.")}><Settings2 size={18} /><span>Settings</span></button>
          <button className="md-user-profile" onClick={() => setShowProfile((value) => !value)}><span className="md-user-avatar">M</span><span><strong>Team Manager</strong><small>Manager workspace</small></span><MoreHorizontal size={18} /></button>
          {showProfile && <button className="md-logout-button" onClick={onLogout}><LogOut size={16} /> Sign out</button>}
        </div>
      </aside>

      <main className="md-main">
        <header className="md-topbar">
          <div className="md-topbar-left"><button className="md-mobile-menu" aria-label="Open navigation" onClick={() => setMobileNavOpen(true)}><Menu size={21} /></button><div className="md-breadcrumb"><span>Workspace</span><span className="md-breadcrumb-slash">/</span><strong>{activeModule}</strong></div></div>
          <div className="md-topbar-right">
            <label className="md-search-box"><Search size={16} /><input value={search} onChange={(event) => { setSearch(event.target.value); if (event.target.value) setActiveModule("My Team"); }} placeholder="Search team..." /><kbd>⌘ K</kbd></label>
            <span className="md-topbar-divider" />
            <button className="md-top-icon" aria-label="Notifications" onClick={() => setNotice("You are viewing the manager workspace. Notification integration can be added next.")}><Bell size={19} /><i /></button>
            <button className="md-top-profile" onClick={() => setShowProfile((value) => !value)}>M<ChevronDown size={13} /></button>
          </div>
        </header>

        <div className="md-page-content">
          <div className="md-page-heading"><div><div className="md-date-line"><span className="md-date-dot" /> MANAGER CONSOLE <span>/</span> {new Date().toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }).toUpperCase()}</div><h1>{activeModule === "Overview" ? "Your team's big picture." : activeModule}<span className="md-heading-period">.</span></h1><p>{activeModule === "Overview" ? "A clearer view of the people and work behind every win." : `Your ${activeModule.toLowerCase()} workspace, organized around what matters.`}</p></div><button className="md-export-button" onClick={() => setNotice("Export is not connected yet. Connect the relevant API to export real data.")}><Download size={16} /> Export view</button></div>
          {notice && <div className="md-notice"><span><CircleAlert size={16} />{notice}</span><button aria-label="Dismiss notice" onClick={() => setNotice("")}><X size={16} /></button></div>}
          {renderModule()}
          <footer className="md-footer"><span>nexora <i>·</i> Manager workspace</span><span>Designed for people who move work forward <Sparkles size={13} /></span></footer>
        </div>
      </main>
    </div>
  );
}
