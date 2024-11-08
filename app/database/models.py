import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, TIMESTAMP, text, Date, Time, UniqueConstraint
from sqlalchemy import Column, UUID, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .session import Base


# metadata = Base.metadata


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email_address = Column(String, nullable=False, index=True)
    date_of_birth = Column(Date, nullable=False)
    password = Column(String, nullable=False)
    confirm_password = Column(String, nullable=False)

    username = Column(String, nullable=False)

    profile_header_path = Column(String, nullable=True)
    profile_pic_path = Column(String, nullable=True)
    location = Column(String, nullable=True)
    website = Column(String, nullable=True)

    is_active = Column(Boolean, index=True, default=False)
    is_verified = Column(Boolean, index=True, default=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'), onupdate=text('now()'))

    otp_codes = relationship("OTPCodes", back_populates="user", cascade="all, delete-orphan")

    events = relationship("Events", back_populates="user", cascade="all, delete-orphan")


class OTPCodes(Base):
    __tablename__ = "otp_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    otp_code = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    expires_in = Column(DateTime(timezone=True), index=True)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    user = relationship("User", back_populates="otp_codes")


class PasswordReset(Base):
    __tablename__ = "password_reset"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    reset_code = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), index=True)
    expires_in = Column(DateTime(timezone=True), index=True)


class BlacklistedTokens(Base):
    __tablename__ = "blacklisted_tokens"

    token = Column(String, primary_key=True, index=True)


class Events(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    event_name = Column(String, nullable=False, index=True)
    event_description = Column(String, nullable=False)
    event_category = Column(String, nullable=False, index=True)
    event_image = Column(String, nullable=False)
    event_date = Column(Date, nullable=False)
    event_time = Column(Time, nullable=False)
    event_location= Column(String, nullable=False, index=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'), onupdate=text('now()'))

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    user = relationship("User", back_populates="events")
    comments = relationship("Comments", back_populates="event", cascade="all, delete-orphan")
    likes = relationship("Likes", back_populates="event", cascade="all, delete-orphan")

    def like_count(self):
        return len(self.likes)


class Comments(Base):
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    content = Column(String, nullable=True)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=True)

    event = relationship("Events", back_populates="comments")


class Likes(Base):
    __tablename__ = "likes"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    __table_args__ = (UniqueConstraint('user_id', 'event_id', name='_user_event_uc'),)

    # Relationships
    user = relationship("User")
    event = relationship("Events", back_populates="likes")



# DELETE FROM user_otp WHERE user_id = '4570785c-61c9-44f3-bf44-47f8a9ff7e72';
# DELETE FROM users WHERE id = '4570785c-61c9-44f3-bf44-47f8a9ff7e72';

# SELECT * FROM users;
# SELECT * FROM user_otp;
