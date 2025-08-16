## API Endpoints

**Base URL:**  
`http://localhost:8000`

---

### 1. `GET /v1/reco/homefeed`
_Get personalized home feed recommendations._
- **Full URL:** `http://localhost:8000/v1/reco/homefeed?user_id=1`
- **Query params:** `user_id` (int, required)

### 2. `POST /v1/reco/feedback`
_Log user feedback events._
- **Full URL:** `http://localhost:8000/v1/reco/feedback`
- **Body:**








# FlatZ Recommendation Service

> A production-ready personalized recommendation system for residential community content discovery. Built with FastAPI, PostgreSQL, and advanced ML techniques.

## Overview

FlatZ Recommendation Service is a sophisticated recommendation engine designed for residential communities. It helps residents discover relevant local content, events, and services by analyzing their preferences and behavior patterns.

The system uses multiple recommendation algorithms including:
- **Content-based filtering** (semantic similarity using embeddings)
- **Collaborative filtering** (user behavior patterns)
- **Popularity-based recommendations** (trending content)
- **Hybrid ranking** with business rules and safety filters

### Key Benefits

- **Personalized Experience**: Each user gets recommendations tailored to their interests
- **Community Focus**: Prioritizes local, relevant content for each residential block
- **Real-time Learning**: Adapts recommendations based on user feedback
- **Safety & Quality**: Filters inappropriate or low-quality content
- **Scalable Architecture**: Designed to handle thousands of users and millions of interactions


### Core Functionality
- ✅ **Multi-Signal Recommendations**: Combines content, collaborative, and popularity signals
- ✅ **Real-time Personalization**: Updates recommendations based on user interactions
- ✅ **Community Isolation**: Prioritizes content from user's residential community
- ✅ **Cold-start Handling**: Provides sensible recommendations for new users
- ✅ **Feedback Integration**: Learns from user likes, views, bookings, and dismissals

### Technical Features
- ✅ **RESTful API**: Clean, documented endpoints for integration
- ✅ **Semantic Search**: Uses state-of-the-art text embeddings (FAISS + sentence-transformers)
- ✅ **Policy & Safety Layer**: Enforces business rules and content quality standards
- ✅ **Performance Optimized**: In-memory caching for sub-second response times
- ✅ **Database-backed**: PostgreSQL for reliable data persistence
- ✅ **Comprehensive Testing**: Unit and integration tests included

### Business Logic
- ✅ **Creator Frequency Caps**: Prevents any single creator from dominating feeds
- ✅ **Quality Filtering**: Removes low-engagement or negatively-rated content
- ✅ **Temporal Decay**: Recent content gets higher priority
- ✅ **Diversity Enforcement**: Ensures varied content types in recommendations



### Data Flow

1. **User Request** → API receives recommendation request
2. **Candidate Generation** → Multiple algorithms generate potential items
3. **Policy Filtering** → Business rules filter candidates
4. **Feature Extraction** → Calculate ranking features for each candidate
5. **Ranking** → Score and sort candidates
6. **Response** → Return top recommendations with explanations

---

## Technology Stack

### Backend
- **Python 3.8+**: Core programming language
- **FastAPI**: High-performance web framework
- **SQLAlchemy**: Database ORM
- **Alembic**: Database migrations
- **Pydantic**: Data validation and serialization

### Database
- **PostgreSQL**: Primary database for users, items, interactions
- **FAISS**: Vector similarity search for content-based recommendations

### Machine Learning
- **sentence-transformers**: Text embeddings for semantic similarity
- **NumPy**: Numerical computations
- **scikit-learn**: Additional ML utilities (if needed)

### Development & Testing
- **pytest**: Testing framework
- **uvicorn**: ASGI server for development
- **python-dotenv**: Environment variable management

---

## Prerequisites

Before setting up the project, ensure you have:

1. **Python 3.8 or higher**

2. **PostgreSQL 12 or higher**

3. **Git** (for cloning the repository)

4. **Virtual environment** (recommended)

---

## Installation & Setup

### Step 1: Clone the Repository

 git clone https://github.com/Chandan72/Flatz-content-based-reco-system
 cd flatz-reco-service

### Step 2: Create Virtual Environment

python -m venv .venv

### activate vitual environment

source .venv/bin/activate


### Step 3: Install Dependencies

pip install --upgrade pip

pip install -r requirements.txt


### Step 4: Set Up PostgreSQL Database

1. **Create Database and User**:
 -- Connect to PostgreSQL as superuser 
    psql -U postgres
 -- Create database
    CREATE DATABASE flatzdb;
 
2. **Set Environment Variables**:
 Create .env file 

 echo "DATABASE_URL=postgresql://flatzuser:your_password@localhost:5432/flatzdb" > .env


### Step 5: Run Database Migrations

  alembic upgrade head


---

## Data Loading

The system comes with sample data generators for testing and development.

### Generate Sample Data

python scripts/generate_sample_data.py

    
This creates:
- `users.csv` (500 users across 10 communities)
- `items.csv` (1,000 community items/events)
- `interactions.csv` (10,000 user interactions)

### Load Data into Database

  python -m scripts.load_data

  rom app.core.db import SessionLocal
from app.core.models import User, Item, Interaction



### Verify Data Loading
db = SessionLocal()
print(f'Users: {db.query(User).count()}')
print(f'Items: {db.query(Item).count()}')
print(f'Interactions: {db.query(Interaction).count()}')
db.close()


---

## Running the Application

### Development Server

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000


The application will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Production Server

 pip install gunicorn  ## for production ready


---

## API Documentation

### Health Check

**GET** `/health`

Check if the service is running.

curl http://localhost:8000/health


**Response:**

{
"status": "ok"
}


### Get Recommendations

**GET** `/v1/reco/homefeed`

Get personalized recommendations for a user.

**Parameters:**
- `user_id` (required): Integer ID of the user

**Example:**
 curl "http://localhost:8000/v1/reco/homefeed?user_id=1"


**Response:**

{
"user_id": 1,
"recommendations": [
{
"item_id": 42,
"title": "Community Yoga Class",
"reason": "Similar to your recent interests",
"tags": ["content", "pop-comm"],
"timestamp": "2025-08-16T18:30:00Z"
},
{
"item_id": 123,
"title": "Block-A Monthly Meeting",
"reason": "Trending in your community",
"tags": ["pop-comm"],
"timestamp": "2025-08-16T18:30:00Z"
}
]
}


### Log User Feedback

**POST** `/v1/reco/feedback`

Record user interactions with recommended items.

**Request Body:**

{
"user_id": 1,
"item_id": 42,
"feedback_type": "like",
"timestamp": "2025-08-16T18:30:00Z"
}


**Feedback Types:**
- `view`: User viewed the item
- `click`: User clicked on the item
- `like`: User liked/favorited the item
- `book`: User booked/registered for the item
- `attend`: User attended the event
- `dismiss`: User dismissed the recommendation

**Example:**

curl -X POST "http://localhost:8000/v1/reco/feedback"
-H "Content-Type: application/json"
-d '{
"user_id": 1,
"item_id": 42,
"feedback_type": "like"
}'


**Response:**
{
"status": "success",
"message": "Logged like for user 1"
}


---

## Testing

### Run All Tests

python -m pytest tests/ -v


### Run Specific Tests

python -m pytest tests/test_endpoints.py -v

python -m pytest tests/test_policy.py -v


### Test Coverage

pip install pytest-cov

python -m pytest tests/ --cov=app --cov-report=html


### Manual Testing via Swagger UI

1. Start the server: `uvicorn app.main:app --reload`
2. Open http://localhost:8000/docs
3. Try the `/v1/reco/homefeed` endpoint with different user IDs
4. Test the `/v1/reco/feedback` endpoint with various feedback types

---


---

## How It Works

### 1. Candidate Generation

The system uses multiple algorithms to generate potential recommendations:

#### Content-Based Filtering
- Converts item titles and descriptions into semantic embeddings
- Uses FAISS for fast similarity search
- Finds items similar to user's recent interactions

#### Collaborative Filtering
- Analyzes user interaction patterns
- Finds items liked by users with similar tastes
- Uses item-item similarity based on user behavior

#### Popularity-Based Recommendations
- Tracks trending content in each community
- Applies time decay to prioritize recent activity
- Provides fallback recommendations for cold-start users

### 2. Policy & Safety Layer

Before ranking, all candidates pass through safety filters:

#### Community Isolation
- Prioritizes content from user's residential community
- Allows controlled spillover from other communities
- Maintains 60% local / 40% global content ratio

#### Creator Frequency Caps
- Limits items from any single creator/source
- Prevents spam or over-representation
- Ensures diverse content in recommendations

#### Quality Filtering
- Removes items with very low engagement
- Filters out negatively-rated content
- Maintains minimum interaction thresholds

### 3. Ranking & Scoring

Candidates are scored using multiple features:

score = (
0.4 * content_similarity +
0.25 * recency_score +
0.15 * popularity_score +
0.2 * community_match
)


### 4. Explanation Generation

Each recommendation includes a human-readable reason:
- "Similar to your recent interests" (content-based)
- "People with similar tastes liked this" (collaborative)
- "Trending in your community" (local popularity)
- "Popular right now" (global popularity)

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

DATABASE_URL=postgresql://username:password@localhost:5432/flatzdb

Application 

DEBUG=true
LOG_LEVEL=INFO

Recommendation Parameters

CONTENT_WEIGHT=0.4
RECENCY_WEIGHT=0.25
POPULARITY_WEIGHT=0.15
COMMUNITY_WEIGHT=0.2

policiy settings

CREATOR_FREQUENCY_CAP=3
MIN_INTERACTION_THRESHOLD=2
COMMUNITY_PREFERENCE_RATIO=0.6


### Recommendation Tuning

You can adjust recommendation behavior by modifying parameters in the service classes:



---

## Troubleshooting

### Common Issues

#### Import Errors in Tests
ModuleNotFoundError: No module named 'app'


**Solution:** Add to `tests/__init__.py`:

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(file), '..')))



#### Database Connection Issues


**Solutions:**
1. Ensure PostgreSQL is running
2. Check DATABASE_URL in your environment
3. Verify database exists and user has permissions

#### FAISS Installation Issues

ImportError: No module named 'faiss'


**Solution:**
pip install faiss-cpu


#### Port Already in Use
OSError: [Errno 48] Address already in use

**Solution:**

uvicorn app.main:app --port 8001 --reload


### Performance Issues

#### Slow Startup Time
- The FAISS index is built at startup (10-30 seconds)
- This is normal for the first run
- Consider pre-building indexes for production

#### High Memory Usage
- FAISS keeps embeddings in memory for speed
- Monitor memory usage with many items
- Consider using disk-based indexes for large datasets

### Debugging

#### Enable Debug Logging

import logging
logging.basicConfig(level=logging.DEBUG)


#### Check Recommendation Pipeline

from app.services.reco.generators.content import content_gen
from app.core.db import SessionLocal

db = SessionLocal()
content_gen.build_index(db)
print('Content generator working')
db.close()


---


#### Monitoring & Observability
- Implement health checks for all components
- Add metrics for recommendation quality
- Monitor API response times and error rates
- Track recommendation click-through rates

### Security Considerations

1. **Input Validation**: All inputs are validated using Pydantic
2. **SQL Injection Prevention**: Using SQLAlchemy ORM
3. **Rate Limiting**: Consider implementing rate limiting for API endpoints
4. **Authentication**: Add authentication for production use

---

## Contributing

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**
3. **Make changes and add tests**
4. **Run the test suite**
5. **Submit a pull request**

### Code Style

- Follow PEP 8 for Python code style
- Use type hints where possible
- Add docstrings for all public functions
- Keep functions small and focused

### Adding New Recommendation Algorithms

1. Create a new generator in `app/services/reco/generators/`
2. Implement the required interface
3. Add it to the candidate service
4. Write tests for the new algorithm

Example:
class MyRecommendationAlgorithm:
def get_candidates(self, user_id: int, top_k: int = 10) -> List[int]:
# Your algorithm implementation
return candidate_item_ids

















