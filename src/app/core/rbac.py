from enum import Enum


class Permission(str, Enum):

    # Company
    VIEW_COMPANY = "view_company"
    EDIT_COMPANY = "edit_company"
    MANAGE_DEPARTMENTS = "manage_departments"
    MANAGE_COMPANY_SETTINGS = "manage_company_settings"
    MANAGE_HOLIDAYS = "manage_holidays"

    # Employees
    VIEW_EMPLOYEES = "view_employees"
    CREATE_EMPLOYEE = "create_employee"
    UPDATE_EMPLOYEE = "update_employee"
    MANAGE_EMPLOYEE_STATUS = "manage_employee_status"
    MANAGE_EMPLOYEE_EXIT = "manage_employee_exit"
    ASSIGN_EMPLOYEE_HR = "assign_employee_hr"
    ASSIGN_EMPLOYEE_MANAGER = "assign_employee_manager"

    # HR
    VIEW_HRS = "view_hrs"
    INVITE_HR = "invite_hr"
    MANAGE_HR = "manage_hr"
    VIEW_HR_PERFORMANCE = "view_hr_performance"

    # Managers
    VIEW_MANAGERS = "view_managers"
    INVITE_MANAGER = "invite_manager"
    MANAGE_MANAGER = "manage_manager"
    VIEW_MANAGER_PERFORMANCE = "view_manager_performance"

    # Owners
    VIEW_OWNER = "view_owner"
    INVITE_OWNER = "invite_owner"

    # Admins
    VIEW_ADMINS = "view_admins"
    INVITE_ADMIN = "invite_admin"
    MANAGE_ADMIN = "manage_admin"

    # Analytics
    VIEW_ANALYTICS = "view_analytics"
    VIEW_COMPANY_PERFORMANCE = "view_company_performance"
    VIEW_ATTENDANCE_ANALYTICS = "view_attendance_analytics"
    VIEW_LEAVE_ANALYTICS = "view_leave_analytics"

    # Goals
    CREATE_GOALS = "create_goals"
    VIEW_GOALS = "view_goals"
    MANAGE_GOALS = "manage_goals"

    # Attendance
    VIEW_ATTENDANCE = "view_attendance"
    MANAGE_ATTENDANCE = "manage_attENDANCE"

    # Leave
    VIEW_LEAVES = "view_leaves"
    MANAGE_LEAVES = "manage_leaves"
    MANAGE_LEAVE_POLICIES = "manage_leave_policies"

    # Notifications
    SEND_NOTIFICATIONS = "send_notifications"

    # Announcements
    MANAGE_ANNOUNCEMENTS = "manage_announcements"

    # Search
    SEARCH_COMPANY_DATA = "search_company_data"

    # Audit
    VIEW_AUDIT_LOGS = "view_audit_logs"

    # Documents
    MANAGE_COMPANY_DOCUMENTS = "manage_company_documents"

    # Payroll
    VIEW_PAYROLL = "view_payroll"
    MANAGE_PAYROLL = "manage_payroll"


ROLE_PERMISSIONS = {
    "COMPANY_ADMIN": {
        Permission.VIEW_COMPANY,
        Permission.EDIT_COMPANY,
        Permission.MANAGE_DEPARTMENTS,
        Permission.MANAGE_COMPANY_SETTINGS,
        Permission.MANAGE_HOLIDAYS,

        Permission.VIEW_EMPLOYEES,
        Permission.CREATE_EMPLOYEE,
        Permission.UPDATE_EMPLOYEE,
        Permission.MANAGE_EMPLOYEE_STATUS,
        Permission.MANAGE_EMPLOYEE_EXIT,
        Permission.ASSIGN_EMPLOYEE_HR,
        Permission.ASSIGN_EMPLOYEE_MANAGER,

        Permission.VIEW_HRS,
        Permission.INVITE_HR,
        Permission.MANAGE_HR,
        Permission.VIEW_HR_PERFORMANCE,

        Permission.VIEW_MANAGERS,
        Permission.INVITE_MANAGER,
        Permission.MANAGE_MANAGER,
        Permission.VIEW_MANAGER_PERFORMANCE,

        Permission.VIEW_OWNER,
        Permission.INVITE_OWNER,

        Permission.VIEW_ADMINS,
        Permission.INVITE_ADMIN,
        Permission.MANAGE_ADMIN,

        Permission.VIEW_ANALYTICS,
        Permission.VIEW_COMPANY_PERFORMANCE,
        Permission.VIEW_ATTENDANCE_ANALYTICS,
        Permission.VIEW_LEAVE_ANALYTICS,

        Permission.CREATE_GOALS,
        Permission.VIEW_GOALS,
        Permission.MANAGE_GOALS,

        Permission.VIEW_ATTENDANCE,
        Permission.MANAGE_ATTENDANCE,

        Permission.VIEW_LEAVES,
        Permission.MANAGE_LEAVES,
        Permission.MANAGE_LEAVE_POLICIES,

        Permission.SEND_NOTIFICATIONS,

        Permission.MANAGE_ANNOUNCEMENTS,

        Permission.SEARCH_COMPANY_DATA,

        Permission.VIEW_AUDIT_LOGS,

        Permission.MANAGE_COMPANY_DOCUMENTS,

        Permission.VIEW_PAYROLL,
        Permission.MANAGE_PAYROLL,
    }
}