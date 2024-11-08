# import uuid
# from random import randint
#
# from sqlalchemy import Boolean, TIMESTAMP, text
# from sqlalchemy import Column, UUID, String
# from sqlalchemy.orm import relationship
#
# from app.database.session import Base
#
#
# class User(Base):
#     __tablename__ = "users"
#
#     id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
#     name = Column(String, nullable=False)
#     email_address = Column(String, nullable=False, index=True)
#     date_of_birth = Column(TIMESTAMP, nullable=False)
#     password = Column(String, nullable=False)
#     confirm_password = Column(String, nullable=False)
#
#     username = Column(String, nullable=False, unique=True)
#
#     profile_header_path = Column(String, nullable=True)
#     profile_pic_path = Column(String, nullable=True)
#     location = Column(String, nullable=True)
#     website = Column(String, nullable=True)
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         # Set the default username if it's not provided
#         if not kwargs.get('username'):
#             self.username = f"{self.name}{randint(100, 999)}"
#
#     is_active = Column(Boolean, index=True, default=False)
#     is_verified = Column(Boolean, index=True, default=False)
#     created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
#     updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'), onupdate=text('now()'))
#
#     otp_codes = relationship("OTPCodes", back_populates="users", cascade="all, delete-orphan")



# DELETE FROM user_otp WHERE user_id = '4570785c-61c9-44f3-bf44-47f8a9ff7e72';
# DELETE FROM users WHERE id = '4570785c-61c9-44f3-bf44-47f8a9ff7e72';

# SELECT * FROM users;
# SELECT * FROM user_otp;
