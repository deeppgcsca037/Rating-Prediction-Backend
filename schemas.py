"""
JSON schemas for API request and response payloads
"""
from typing import Optional
from pydantic import BaseModel, Field, validator


class ReviewSubmissionRequest(BaseModel):
    """Schema for review submission from user dashboard"""
    rating: int = Field(..., ge=1, le=5, description="Star rating from 1 to 5")
    review_text: str = Field(..., min_length=1, max_length=5000, description="Review text content")

    @validator('review_text')
    def validate_review_text(cls, v):
        if not v or not v.strip():
            raise ValueError('Review text cannot be empty')
        return v.strip()


class ReviewSubmissionResponse(BaseModel):
    """Schema for review submission response"""
    success: bool
    review_id: Optional[str] = None
    ai_response: Optional[str] = None
    error: Optional[str] = None


class ReviewItem(BaseModel):
    """Schema for individual review item"""
    review_id: str
    rating: int
    review_text: str
    ai_summary: str
    ai_recommended_actions: str
    created_at: str


class AdminDashboardResponse(BaseModel):
    """Schema for admin dashboard data"""
    reviews: list[ReviewItem]
    total_count: int
    rating_distribution: dict[int, int]
    analytics: dict


class HealthCheckResponse(BaseModel):
    """Schema for health check endpoint"""
    status: str
    database_connected: bool
    llm_available: bool


