from sqlalchemy import text
from sqlalchemy.orm import Session


def set_current_company(
    db: Session,
    company_id: int
):
    db.execute(
        text(
            "SELECT set_config("
            "'app.current_company_id', "
            ":company_id, "
            "false"
            ")"
        ),
        {
            "company_id": str(company_id)
        }
    )


def clear_current_company(
    db: Session
):
    db.execute(
        text(
            "SELECT set_config("
            "'app.current_company_id', "
            "'', "
            "false"
            ")"
        )
    )