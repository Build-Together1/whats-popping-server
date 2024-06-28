from app.apis.users.individual.models import IndividualAccount
from app.apis.users.corporate.models import CorporateAccount
from app.apis.auth.models import (
    OTPCodes,
    PasswordReset,
    BlacklistedTokens
)

from .session import Base

metadata = Base.metadata
