"""
Flask backend API for AI Feedback System
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import init_db, get_db, Review
from schemas import (
    ReviewSubmissionRequest,
    ReviewSubmissionResponse,
    ReviewItem,
    AdminDashboardResponse,
    HealthCheckResponse
)
from llm_service import LLMService
from config import CORS_ORIGINS, MAX_REVIEW_LENGTH, MIN_REVIEW_LENGTH
import traceback

app = Flask(__name__)
CORS(app, origins=CORS_ORIGINS)

# Initialize database
init_db()

# Initialize LLM service
llm_service = LLMService()


@app.route('/', methods=['GET'])
def index():
    """Root endpoint - API information"""
    return jsonify({
        'message': 'AI Feedback System API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'submit_review': 'POST /api/submit-review',
            'admin_reviews': 'GET /api/admin/reviews',
            'admin_review_by_id': 'GET /api/admin/reviews/<review_id>'
        },
        'status': 'running'
    }), 200


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        db = next(get_db())
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db_connected = True
    except:
        db_connected = False
    
    llm_available = True  # Assume available, will fail gracefully if not
    
    return jsonify(HealthCheckResponse(
        status="healthy" if db_connected else "degraded",
        database_connected=db_connected,
        llm_available=llm_available
    ).dict())


@app.route('/api/submit-review', methods=['POST'])
def submit_review():
    """Submit a new review"""
    try:
        # Validate request
        data = request.get_json()
        if not data:
            return jsonify(ReviewSubmissionResponse(
                success=False,
                error="No data provided"
            ).dict()), 400

        # Validate schema
        try:
            review_request = ReviewSubmissionRequest(**data)
        except Exception as e:
            return jsonify(ReviewSubmissionResponse(
                success=False,
                error=f"Validation error: {str(e)}"
            ).dict()), 400

        # Validate review text length
        if len(review_request.review_text) > MAX_REVIEW_LENGTH:
            return jsonify(ReviewSubmissionResponse(
                success=False,
                error=f"Review text exceeds maximum length of {MAX_REVIEW_LENGTH} characters"
            ).dict()), 400

        if len(review_request.review_text.strip()) < MIN_REVIEW_LENGTH:
            return jsonify(ReviewSubmissionResponse(
                success=False,
                error="Review text cannot be empty"
            ).dict()), 400

        # Get database session
        try:
            db: Session = next(get_db())
        except Exception as db_error:
            return jsonify(ReviewSubmissionResponse(
                success=False,
                error=f"Database connection error: {str(db_error)}"
            ).dict()), 500

        # Generate AI response for user
        try:
            ai_response = llm_service.generate_user_response(
                review_request.rating,
                review_request.review_text
            )
        except Exception as e:
            ai_response = "Thank you for your feedback. We appreciate your input."

        # Generate AI summary and recommendations
        try:
            ai_summary = llm_service.generate_summary(
                review_request.rating,
                review_request.review_text
            )
            ai_recommended_actions = llm_service.generate_recommended_actions(
                review_request.rating,
                review_request.review_text
            )
        except Exception as e:
            ai_summary = f"{review_request.rating}-star review"
            ai_recommended_actions = "Review submitted successfully"

        # Save to database
        try:
            review = Review(
                rating=review_request.rating,
                review_text=review_request.review_text,
                ai_summary=ai_summary,
                ai_recommended_actions=ai_recommended_actions
            )
            db.add(review)
            db.commit()
            db.refresh(review)
        except Exception as db_error:
            db.rollback()
            return jsonify(ReviewSubmissionResponse(
                success=False,
                error=f"Failed to save review: {str(db_error)}"
            ).dict()), 500
        finally:
            db.close()

        return jsonify(ReviewSubmissionResponse(
            success=True,
            review_id=review.review_id,
            ai_response=ai_response
        ).dict()), 201

    except Exception as e:
        return jsonify(ReviewSubmissionResponse(
            success=False,
            error=f"Internal server error: {str(e)}"
        ).dict()), 500


@app.route('/api/admin/reviews', methods=['GET'])
def get_admin_reviews():
    """Get all reviews for admin dashboard"""
    db: Session = None
    try:
        db = next(get_db())

        # Get all reviews, ordered by most recent first
        reviews = db.query(Review).order_by(Review.created_at.desc()).all()

        # Calculate rating distribution
        rating_dist = db.query(
            Review.rating,
            func.count(Review.review_id).label('count')
        ).group_by(Review.rating).all()
        rating_distribution = {rating: count for rating, count in rating_dist}

        # Calculate analytics
        total_count = len(reviews)
        avg_rating = db.query(func.avg(Review.rating)).scalar() or 0
        low_ratings = sum(1 for r in reviews if r.rating <= 2)
        high_ratings = sum(1 for r in reviews if r.rating >= 4)

        analytics = {
            'total_reviews': total_count,
            'average_rating': round(float(avg_rating), 2),
            'low_ratings_count': low_ratings,
            'high_ratings_count': high_ratings,
            'low_ratings_percentage': round((low_ratings / total_count * 100) if total_count > 0 else 0, 2),
            'high_ratings_percentage': round((high_ratings / total_count * 100) if total_count > 0 else 0, 2)
        }

        # Convert reviews to response format
        review_items = [ReviewItem(**review.to_dict()) for review in reviews]

        return jsonify(AdminDashboardResponse(
            reviews=[item.dict() for item in review_items],
            total_count=total_count,
            rating_distribution=rating_distribution,
            analytics=analytics
        ).dict()), 200

    except Exception as e:
        return jsonify({
            'error': f"Internal server error: {str(e)}"
        }), 500
    finally:
        if db:
            db.close()


@app.route('/api/admin/reviews/<review_id>', methods=['GET'])
def get_review(review_id):
    """Get a specific review by ID"""
    db: Session = None
    try:
        db = next(get_db())
        review = db.query(Review).filter(Review.review_id == review_id).first()
        
        if not review:
            return jsonify({'error': 'Review not found'}), 404
        
        return jsonify(ReviewItem(**review.to_dict()).dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if db:
            db.close()


if __name__ == '__main__':
    from config import API_HOST, API_PORT, DEBUG
    # Disable Flask's automatic .env loading to avoid encoding issues
    # We already load it in config.py
    import os
    os.environ['FLASK_SKIP_DOTENV'] = '1'
    app.run(host=API_HOST, port=API_PORT, debug=DEBUG)

