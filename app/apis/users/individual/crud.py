from datetime import datetime, timedelta

from .models import IndividualAccount
from ...auth.models import OTPCodes
from ...auth.utils import generate_otp


async def get_account_by_email(req, db):
    return db.query(IndividualAccount).filter(IndividualAccount.email_address == req.email_address).first()


def save_account_to_db(user_dict, db):
    account = IndividualAccount(
        **user_dict,
        is_active=False,
        is_verified=False
    )

    db.add(account)
    db.commit()
    db.refresh(account)


def save_otp_to_db(req, account, db):
    generated_otp = generate_otp()
    created_at = datetime.utcnow()
    expires_in = created_at + timedelta(minutes=3)

    otp_code = OTPCodes()
    otp_code.individual_id = account.id
    otp_code.otp_code = generated_otp
    otp_code.expires_in = expires_in

    db.add(otp_code)
    db.commit()
    db.refresh(otp_code)
