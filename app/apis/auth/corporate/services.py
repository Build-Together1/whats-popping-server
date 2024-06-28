from datetime import timedelta, datetime

from fastapi import HTTPException, status

from . import crud
from .. import utils
from ..models import PasswordReset
from ..utils import generate_otp, Password


class CorporateUserAccount:
    @staticmethod
    async def verify_email(req, db):
        account = crud.get_account_by_email(req, db)
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        otp = crud.get_otp_code(req, db)
        if not otp:
            raise HTTPException(status_code=404, detail="invalid OTP")

        if account and otp:
            current_time = datetime.utcnow()
            if otp.expires_in < current_time:
                raise HTTPException(status_code=404, detail="expired OTP")

        await crud.save_account_to_db(account, db)

        return {"msg": "Email verified"}

    @staticmethod
    async def otp_for_email_verification(req, db):
        account = crud.get_account_by_email(req, db)
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        generated_otp = generate_otp()
        created_at = datetime.utcnow()
        expires_in = created_at + timedelta(minutes=2)

        await crud.save_otp_to_db(generated_otp, expires_in, db)

        return {
            "message": f"Your otp has been generated successfully. "
                       f"Verify your account by inputting {generated_otp}"
        }

    @staticmethod
    async def change_account_password(req, db, current_user):
        if not current_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")

        account = crud.get_account_by_email(req, db)
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        check_password = Password.verify_password(req.old_password, current_user.password)
        if not check_password:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail="Invalid password. Check old password")

        await utils.password_checker(req.new_password, req.confirm_password)

        password = Password.hash_password(req.new_password)
        confirm_password = Password.hash_password(req.confirm_password)

        await crud.save_password_to_db(account, password, confirm_password, db)

        return {"msg": "Password changed successfully"}

    @staticmethod
    async def account_reset_otp(req, db):
        account = crud.get_account_by_email(req, db)
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        generated_otp = generate_otp()
        created_at = datetime.utcnow()
        expires_in = created_at + timedelta(minutes=2)

        reset_code = PasswordReset()
        reset_code.reset_code = generated_otp
        reset_code.expires_in = expires_in

        await crud.save_reset_code_to_db(reset_code, db)

        return {
            "message": f"Your otp has been generated successfully. "
                       f"reset your password by inputting {generated_otp}"
        }

    @staticmethod
    async def account_password_reset(req, db):
        account = crud.get_account_by_email(req, db)
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        reset_code = crud.get_reset_code(req, db)
        if not reset_code:
            raise HTTPException(status_code=404, detail="invalid OTP")

        if account and reset_code:
            current_time = datetime.utcnow()
            if reset_code.expires_in < current_time:
                raise HTTPException(status_code=404, detail="expired OTP")

        await utils.password_checker(req.password, req.confirm_password)

        password = Password.hash_password(req.password)
        confirm_password = Password.hash_password(req.confirm_password)

        await crud.save_password_to_db(account, password, confirm_password, db)

        return {"msg": "Password reset successful"}

    @staticmethod
    async def disable_account(req, db, current_user):
        if not current_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")
        account = crud.get_account_by_email(req, db)
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        await crud.save_disabled_account_to_db(account, db)

        return {"message": "User disabled successfully"}

    @staticmethod
    async def enable_account(req, db):
        account = crud.get_account_by_email(req, db)
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        await crud.save_enabled_account_to_db(account, db)
        return {"message": "User enabled successfully"}
