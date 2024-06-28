from app.apis.auth.models import OTPCodes, PasswordReset
from app.apis.users.corporate.models import CorporateAccount


def get_account_by_email(req, db):
    return db.query(CorporateAccount).filter(CorporateAccount.email_address == req.email_address).first()


def get_account_by_id(req, db):
    return db.query(CorporateAccount).filter(CorporateAccount.id == req.id).first()


def get_otp_code(req, db):
    return db.query(OTPCodes).filter(OTPCodes.otp_code == req.otp).first()


async def save_account_to_db(account, db):
    account.is_verified = True
    account.is_active = True
    db.commit()
    db.refresh(account)


async def save_otp_to_db(generated_otp, expires_in, db):
    otp_code = OTPCodes()
    otp_code.otp_code = generated_otp
    otp_code.expires_in = expires_in

    db.add(otp_code)
    db.commit()
    db.refresh(otp_code)


async def save_password_to_db(account, password, confirm_password, db):
    account.password = password
    account.confirm_password = confirm_password
    db.commit()
    db.refresh(account)


async def save_reset_code_to_db(reset_code, db):
    db.add(reset_code)
    db.commit()
    db.refresh(reset_code)


def get_reset_code(req, db):
    return db.query(PasswordReset).filter(PasswordReset.reset_code == req.reset_code).first()


async def save_disabled_account_to_db(account, db):
    account.is_active = False
    db.commit()
    db.refresh(account)


async def save_enabled_account_to_db(account, db):
    account.is_active = True
    db.commit()
    db.refresh(account)
