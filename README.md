# Prediction Market Application

A Django-based prediction market application where users can predict on various randomly-behaving entities (sports, financial, random events) and earn points for correct predictions.

## Features

- **Multiple Prediction Categories**: Sports, Financial, Random Events, and Custom categories
- **Random Entity Behavior**: Background tasks generate random outcomes for events
- **Flexible Authentication**: Password-based authentication with optional OAuth (Google, GitHub)
- **Point-based Scoring**: Users earn points for correct predictions
- **REST API**: Full REST API for programmatic access
- **User Dashboard**: Track predictions, scores, and win rates
- **Leaderboard**: See top performers
- **Admin Interface**: Manage events, categories, and users

## Tech Stack

- **Backend**: Django 4.2
- **API Framework**: Django REST Framework
- **Background Tasks**: Celery + Redis
- **Authentication**: django-allauth (Password + OAuth)
- **Database**: SQLite (development)
- **Frontend**: Django Templates

## Setup Instructions

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Unix:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` and add your OAuth credentials:
- `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` (optional, for Google OAuth)
- `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` (optional, for GitHub OAuth)
- `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` (default: redis://localhost:6379/0)

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Create Superuser

```bash
python manage.py createsuperuser
```

Or use the default admin user:
- Username: `admin`
- Password: `admin123`

### 5. Seed Sample Data

```bash
python manage.py seed_data
```

This creates sample categories, entities, and events.

### 6. Start Redis (for Celery)

```bash
# On Windows with Docker
docker run -d -p 6379:6379 redis

# Or install Redis locally
# Download from https://redis.io/download
```

### 7. Start Celery Worker

```bash
celery -A prediction_market worker -l info
```

### 8. Start Celery Beat (for scheduled tasks)

```bash
celery -A prediction_market beat -l info
```

### 9. Run Development Server

```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## API Endpoints

- `GET /api/categories/` - List all categories
- `GET /api/events/` - List events (filter by `?category=<id>` or `?status=<status>`)
- `GET /api/events/active/` - List active events
- `GET /api/events/<id>/` - Get event details
- `POST /api/predictions/` - Create a prediction (requires authentication)
- `GET /api/predictions/my_predictions/` - List user's predictions
- `GET /api/user-score/` - Get user's current score
- `GET /api/leaderboard/` - Get top 10 users by score

## Web Pages

- `/` - Home page with active events
- `/dashboard/` - User dashboard with prediction history
- `/leaderboard/` - Leaderboard
- `/event/<id>/` - Event detail page
- `/accounts/login/` - Login page (password or OAuth)
- `/accounts/signup/` - Sign up page (password or OAuth)
- `/accounts/logout/` - Logout
- `/admin/` - Django admin interface

## Event Types

1. **Sports Events (match)**: Predict match outcomes between teams
2. **Financial Events (price)**: Predict price movements (up/down/no change)
3. **Random Events (random)**: Coin flips, dice rolls, random numbers
4. **Custom Events**: Configurable custom predictions

## Background Tasks

The application uses Celery for background tasks:

- `resolve_event(event_id)`: Resolves a specific event and updates user scores
- `resolve_expired_events()`: Checks for and resolves all expired events
- `generate_random_entity_states()`: Updates entity states randomly

To run scheduled tasks, use Celery Beat or set up a cron job to call `resolve_expired_events` periodically.

## Admin Interface

Access the admin interface at `/admin/` to:
- Create and manage categories
- Create and manage entities
- Create and manage events
- View all predictions
- Manage users
- Manually resolve events if needed

## Authentication

The application supports two authentication methods:

### Password-Based Authentication (Default)

Users can sign up and login using:
- Username
- Email
- Password

Simply visit `/accounts/signup/` to create an account or `/accounts/login/` to log in.

**Password Reset**: Users can reset their password via the "Forgot Password?" link on the login page. Password reset emails will be displayed in the console (development mode).

### OAuth Authentication (Optional)

To enable OAuth authentication, configure the providers:

### Google OAuth
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable Google+ API
3. Create OAuth 2.0 credentials
4. Add callback URL: `http://localhost:8000/accounts/google/login/callback/`
5. Copy Client ID and Secret to `.env`

### GitHub OAuth
1. Go to GitHub Settings > Developer settings > OAuth Apps
2. Create a new OAuth App
3. Set callback URL: `http://localhost:8000/accounts/github/login/callback/`
4. Copy Client ID and Secret to `.env`

## Development Notes

- SQLite is used for development. For production, consider PostgreSQL
- Redis is required for Celery to work
- Password-based authentication is enabled by default
- OAuth setup is optional - users can still sign up/login with username/email and password
- The seed data command creates sample events that expire in 1-2 hours
- Event resolution happens automatically via background tasks when events expire
- Password reset emails are displayed in the console (development mode)

## Testing

Run the development server and:
1. Visit `http://localhost:8000` to see active events
2. Create an account or login
3. Make predictions on active events
4. Wait for events to expire (or manually resolve in admin)
5. Check your dashboard and leaderboard

## License

This is a sample project for educational purposes.
