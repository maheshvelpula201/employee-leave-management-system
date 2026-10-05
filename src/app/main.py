from fastapi import FastAPI

from src.app.api.employees.routes import router as employee_router
from src.app.api.leave import router as leave_router
from src.app.api.leave_balance import router as leave_balance_router
from src.app.api.leave_policy import router as leave_policy_router
from src.app.api.hr import router as hr_router
from src.app.api.registration import router as registration_router
from src.app.api.company import router as company_router
from src.app.api.admin import router as admin_router
from src.app.api.auth import router as auth_router
from src.app.api.test_auth import router as test_auth_router


app = FastAPI(
    title="Employee Leave Management System",
    version="1.0.0"
)


app.include_router(employee_router)
app.include_router(leave_router)
app.include_router(leave_balance_router)
app.include_router(leave_policy_router)
app.include_router(hr_router)
app.include_router(registration_router)
app.include_router(company_router)
app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(test_auth_router)


@app.get("/")
def root():
    return {
        "message": "Employee Leave Management System is running"
    }