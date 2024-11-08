# import uuid
# from datetime import datetime, timezone
#
# from sqlalchemy import Column, UUID, String, DateTime, ForeignKey
# from sqlalchemy.orm import relationship
#
# from app.database.session import Base
#
#
# class OTPCodes(Base):
#     __tablename__ = "otp_codes"
#
#     id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
#     otp_code = Column(String, nullable=False, index=True)
#     created_at = Column(DateTime, default=datetime.now(timezone.utc))
#     expires_in = Column(DateTime, index=True)
#
#     user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
#
#     user = relationship("User", back_populates="otp_codes")
#
#
#
# class PasswordReset(Base):
#     __tablename__ = "password_reset"
#
#     id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
#     reset_code = Column(String, nullable=False, index=True)
#     created_at = Column(DateTime, default=datetime.now(timezone.utc), index=True)
#     expires_in = Column(DateTime, index=True)
#
#
# class BlacklistedTokens(Base):
#     __tablename__ = "blacklisted_tokens"
#
#     token = Column(String, primary_key=True, index=True)
#
#
