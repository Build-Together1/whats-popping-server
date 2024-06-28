import uuid

from sqlalchemy import Boolean, TIMESTAMP, text
from sqlalchemy import Column, UUID, String
from sqlalchemy.orm import relationship

from app.database.session import Base


class IndividualAccount(Base):
    __tablename__ = "individual_account"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email_address = Column(String, nullable=False, index=True)
    phone_number = Column(String, default="Not specified")
    state = Column(String, nullable=False)
    country = Column(String, nullable=False)
    password = Column(String, nullable=False)
    confirm_password = Column(String, nullable=False)
    is_active = Column(Boolean, index=True, default=False)
    is_verified = Column(Boolean, index=True, default=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'), onupdate=text('now()'))

    otp_codes = relationship("OTPCodes", back_populates="individual_account", cascade="all, delete-orphan")


# DELETE FROM user_otp WHERE user_id = '4570785c-61c9-44f3-bf44-47f8a9ff7e72';
# DELETE FROM users WHERE id = '4570785c-61c9-44f3-bf44-47f8a9ff7e72';

# SELECT * FROM users;
# SELECT * FROM user_otp;
