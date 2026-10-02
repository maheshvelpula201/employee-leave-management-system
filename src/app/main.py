from src.app.api.employees.routes import router as employee_router
from src.app.api.leave import router as leave_router
from fastapi import FastAPI
from src.app.api.leave_balance import router as leave_balance_router
from src.app.api.leave_policy import router as leave_policy_router
from src.app.api.hr import router as hr_router

app = FastAPI(
    title="Employee Leave Management System",
    version="1.0.0"
)

app.include_router(employee_router)
app.include_router(leave_router)
app.include_router(leave_balance_router)
app.include_router(leave_policy_router)
app.include_router(hr_router)

@app.get("/")
def root():
    return {"message": "Employee Leave Management System is running"}