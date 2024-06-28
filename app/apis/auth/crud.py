from app.apis.auth.models import BlacklistedTokens
from app.apis.users.corporate.models import CorporateAccount
from app.apis.users.individual.models import IndividualAccount


def get_individual_account_by_email(db, email: str):
    return db.query(IndividualAccount).filter(IndividualAccount.email_address == email).first()


def get_corporate_account_by_email(db, email: str):
    return db.query(CorporateAccount).filter(CorporateAccount.email_address == email).first()


def get_individual_account_by_id(db, account_id: str):
    return db.query(IndividualAccount).filter(IndividualAccount.id == account_id).first()


def get_corporate_account_by_id(db, account_id: str):
    return db.query(CorporateAccount).filter(CorporateAccount.id == account_id).first()


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
