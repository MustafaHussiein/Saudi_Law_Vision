"""
Lawyer Model
Extended profile for lawyer users
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, Date, JSON
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Lawyer(BaseModel):
    """Lawyer profile (extends User)"""
    
    __tablename__ = "lawyers"
    
    # User reference (one-to-one)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    user = relationship("User", back_populates="lawyer_profile")
    
    # Professional details
    license_number = Column(String(50), unique=True)
    bar_association = Column(String(100))
    license_issue_date = Column(Date)
    license_expiry_date = Column(Date)
    
    # Specializations
    specialization = Column(String(200))
    specialization_ar = Column(String(200))
    areas_of_practice = Column(JSON)  # List of practice areas
    
    # Experience
    years_of_experience = Column(Integer)
    education = Column(Text)
    education_ar = Column(Text)
    certifications = Column(JSON)  # List of certifications
    
    # Profile
    bio = Column(Text)
    bio_ar = Column(Text)
    languages = Column(JSON)  # List of languages spoken
    
    # Availability
    is_available = Column(Boolean, default=True)
    max_cases = Column(Integer, default=20)
    hourly_rate = Column(Integer)  # In local currency
    
    # Stats
    cases_won = Column(Integer, default=0)
    cases_lost = Column(Integer, default=0)
    total_cases = Column(Integer, default=0)
    success_rate = Column(Integer, default=0)  # Percentage
    
    # Assignments
    cases = relationship("Case", back_populates="lawyer")
    
    def calculate_success_rate(self):
        """Calculate success rate"""
        if self.total_cases > 0:
            self.success_rate = int((self.cases_won / self.total_cases) * 100)
        return self.success_rate
    
    def __repr__(self):
        return f"<Lawyer(id={self.id}, license={self.license_number})>"
