# src/app/api/employees/routes.py

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from src.app.db.database import get_db
from src.app.models.user import User
from src.app.models.employes import Employee
from src.app.models.hr import HR
from src.app.core.rbac_dependencies import require_permission
from src.app.core.rbac import Permission
from src.app.schemas.employee import StaffMemberResponse, ProfileUpdate, UserProfileResponse


router = APIRouter(
    prefix="/staff",
    tags=["Staff Directory & Profiles"],
)


@router.get("/", response_model=list[StaffMemberResponse])
def get_staff_directory(
    category: str | None = Query(default=None, description="Filter by 'Employee', 'Manager', or 'HR'"),
    search: str | None = Query(default=None, description="Search by name, email, employee ID, or phone"),
    department: str | None = Query(default=None, description="Filter by department"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.VIEW_COMPANY)),
):
    """
    Retrieves real staff records (Employees, Managers, HR) for the company admin's tenant,
    excluding Owner accounts. Supports searching and category filtering.
    """
    company_id = current_user.company_id
    staff_members = []

    # 1. Fetch Employees and Managers
    if not category or category.upper() in {"EMPLOYEE", "MANAGER"}:
        emp_query = db.query(Employee).filter(Employee.company_id == company_id)
        
        if category:
            cat_upper = category.upper()
            if cat_upper == "MANAGER":
                emp_query = emp_query.filter(
                    or_(
                        Employee.designation.ilike("%manager%"),
                        Employee.role == "MANAGER" if hasattr(Employee, "role") else False
                    )
                )
            elif cat_upper == "EMPLOYEE":
                emp_query = emp_query.filter(
                    or_(
                        Employee.designation.is_(None),
                        ~Employee.designation.ilike("%manager%")
                    )
                )

        if department:
            emp_query = emp_query.filter(Employee.department.ilike(f"%{department}%"))

        employees = emp_query.all()
        for emp in employees:
            is_mgr = emp.designation and "manager" in emp.designation.lower()
            cat_label = "Manager" if is_mgr else "Employee"
            
            if category and category.capitalize() != cat_label:
                continue

            staff_members.append(StaffMemberResponse(
                id=emp.id,
                name=emp.name,
                email=emp.email,
                employee_id=str(emp.id),
                department=emp.department,
                designation=emp.designation,
                phone=getattr(emp, "phone", None),
                category=cat_label,
                employment_status=getattr(emp, "employment_status", "ACTIVE"),
                joining_date=getattr(emp, "joining_date", None),
                created_at=getattr(emp, "created_at", None),
            ))

    # 2. Fetch HR personnel
    if not category or category.upper() == "HR":
        hr_query = db.query(HR).filter(HR.company_id == company_id)
        hrs = hr_query.all()
        for h in hrs:
            staff_members.append(StaffMemberResponse(
                id=h.id,
                name=h.name,
                email=h.email,
                employee_id=f"HR-{h.id}",
                department="Human Resources",
                designation="HR Specialist",
                phone=getattr(h, "phone", None),
                category="HR",
                employment_status="ACTIVE",
                joining_date=getattr(h, "joining_date", None),
                created_at=getattr(h, "created_at", None),
            ))

    # 3. Apply search filter across name, email, employee ID, phone
    if search:
        term = search.strip().lower()
        filtered = []
        for sm in staff_members:
            match_name = sm.name and term in sm.name.lower()
            match_email = sm.email and term in sm.email.lower()
            match_empid = sm.employee_id and term in sm.employee_id.lower()
            match_phone = sm.phone and term in sm.phone.lower()
            if match_name or match_email or match_empid or match_phone:
                filtered.append(sm)
        staff_members = filtered

    return staff_members


@router.get("/profile", response_model=UserProfileResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.VIEW_COMPANY)),
):
    """
    Retrieves the authenticated user's professional profile details.
    """
    if current_user.role == "OWNER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owners do not use employee profile completion."
        )

    phone = None
    department = None
    designation = None
    employment_status = "ACTIVE"
    joining_date = None

    if current_user.role == "HR":
        hr_rec = db.query(HR).filter(HR.email == current_user.email, HR.company_id == current_user.company_id).first()
        if hr_rec:
            phone = getattr(hr_rec, "phone", None)
            department = "Human Resources"
            designation = "HR Specialist"
    else:
        emp_rec = db.query(Employee).filter(Employee.email == current_user.email, Employee.company_id == current_user.company_id).first()
        if emp_rec:
            phone = getattr(emp_rec, "phone", None)
            department = emp_rec.department
            designation = emp_rec.designation
            employment_status = getattr(emp_rec, "employment_status", "ACTIVE")
            joining_date = getattr(emp_rec, "joining_date", None)

    return UserProfileResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        company_id=current_user.company_id,
        phone=phone,
        department=department,
        designation=designation,
        employment_status=employment_status,
        joining_date=joining_date,
    )


@router.put("/profile", response_model=UserProfileResponse)
def update_my_profile(
    data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.VIEW_COMPANY)),
):
    """
    Updates the authenticated user's profile details and synchronizes them
    to the corresponding Employee or HR record so it appears in the Staff Directory.
    """
    if current_user.role == "OWNER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owners cannot modify employee profiles."
        )

    # Update user account name
    current_user.name = data.name
    db.add(current_user)

    phone = None
    department = None
    designation = None
    employment_status = "ACTIVE"
    joining_date = None

    if current_user.role == "HR":
        hr_rec = db.query(HR).filter(HR.email == current_user.email, HR.company_id == current_user.company_id).first()
        if hr_rec:
            hr_rec.name = data.name
            if hasattr(hr_rec, "phone"):
                hr_rec.phone = data.phone
                phone = data.phone
            db.add(hr_rec)
        department = "Human Resources"
        designation = "HR Specialist"
    else:
        emp_rec = db.query(Employee).filter(Employee.email == current_user.email, Employee.company_id == current_user.company_id).first()
        if emp_rec:
            emp_rec.name = data.name
            if data.department:
                emp_rec.department = data.department
                department = data.department
            if data.designation is not None:
                emp_rec.designation = data.designation
                designation = data.designation
            if hasattr(emp_rec, "phone"):
                emp_rec.phone = data.phone
                phone = data.phone
            db.add(emp_rec)
            employment_status = getattr(emp_rec, "employment_status", "ACTIVE")
            joining_date = getattr(emp_rec, "joining_date", None)

    try:
        db.commit()
        db.refresh(current_user)
    except Exception:
        db.rollback()
        raise

    return UserProfileResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        company_id=current_user.company_id,
        phone=phone,
        department=department,
        designation=designation,
        employment_status=employment_status,
        joining_date=joining_date,
    )