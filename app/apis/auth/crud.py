from app.database.models import User, PasswordReset, OTPCodes, BlacklistedTokens


def get_user_by_email(db, email: str):
    return db.query(User).filter(User.email_address == email).first()


def get_user_by_id(db, user_id: str):
    return db.query(User).filter(User.id == user_id).first()


def get_otp_code(req, db):
    return db.query(OTPCodes).filter(OTPCodes.otp_code == req.otp).first()


async def save_user_to_db(user, db):
    user.is_verified = True
    user.is_active = True
    db.commit()
    db.refresh(user)


async def save_otp_to_db(generated_otp, expires_in, db):
    otp_code = OTPCodes()
    otp_code.otp_code = generated_otp
    otp_code.expires_in = expires_in

    db.add(otp_code)
    db.commit()
    db.refresh(otp_code)


async def save_password_to_db(user, password, confirm_password, db):
    user.password = password
    user.confirm_password = confirm_password
    db.commit()
    db.refresh(user)


async def save_reset_code_to_db(reset_code, db):
    db.add(reset_code)
    db.commit()
    db.refresh(reset_code)


def get_reset_code(req, db):
    return db.query(PasswordReset).filter(PasswordReset.reset_code == req.reset_code).first()


async def save_disabled_user_to_db(user, db):
    user.is_active = False
    db.commit()
    db.refresh(user)


async def save_enabled_user_to_db(user, db):
    user.is_active = True
    db.commit()
    db.refresh(user)


def get_blacklisted_token(db, token):
    return db.query(BlacklistedTokens).filter(BlacklistedTokens.token == token).first()


def save_blacklisted_access_token_to_db(db, access_token):
    blacklisted_token_access = BlacklistedTokens(token=access_token)
    db.add(blacklisted_token_access)
    db.commit()


def save_blacklisted_refresh_token_to_db(db, refresh_token):
    blacklisted_token_refresh = BlacklistedTokens(token=refresh_token)
    db.add(blacklisted_token_refresh)
    db.commit()
