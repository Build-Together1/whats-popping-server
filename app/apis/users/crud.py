from datetime import datetime, timedelta, timezone

from app.apis.auth.utils import generate_otp
from app.database.models import User, OTPCodes


async def get_user_by_email(req, db):
    return db.query(User).filter(User.email_address == req.email_address).first()

async def get_user_by_id(req, db):
    return db.query(User).filter(User.id == req.id).first()

async def get_user_by_username(req, db):
    return db.query(User).filter(User.username == req.username).first()


def save_user_to_db(user_dict, db):
    account = User(
        **user_dict,
        is_active=False,
        is_verified=False
    )

    db.add(account)
    db.commit()
    db.refresh(account)


def save_otp_to_db(req, account, db):
    generated_otp = generate_otp()
    created_at = datetime.now(timezone.utc)
    expires_in = created_at + timedelta(minutes=3)

    otp_code = OTPCodes()
    otp_code.individual_id = account.id
    otp_code.otp_code = generated_otp
    otp_code.expires_in = expires_in

    db.add(otp_code)
    db.commit()
    db.refresh(otp_code)
