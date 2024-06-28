from fastapi import HTTPException, status

from app.apis.auth.utils import password_checker, Password
from app.apis.users.individual import crud
from app.apis.users.individual.crud import save_account_to_db


class IndividualUserAccount:
    @staticmethod
    async def create_individual_account(req, user_dict, db):

        existing_account = await crud.get_account_by_email(req, db)
        if existing_account:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This account already exists")

        await password_checker(req.password, req.confirm_password)

        req.password = Password.hash_password(req.password)
        req.confirm_password = Password.hash_password(req.confirm_password)

        user_dict = req.model_dump()

        account = save_account_to_db(user_dict, db)
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
