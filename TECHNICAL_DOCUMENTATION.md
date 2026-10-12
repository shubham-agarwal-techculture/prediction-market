# Prediction Market System - Technical Documentation

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Technology Stack & Rationale](#technology-stack--rationale)
3. [Design Patterns](#design-patterns)
4. [Database Design](#database-design)
5. [API Design](#api-design)
6. [Authentication & Authorization](#authentication--authorization)
7. [Background Task Architecture](#background-task-architecture)
8. [Random Entity Behavior System](#random-entity-behavior-system)
9. [Frontend Architecture](#frontend-architecture)
10. [Security Considerations](#security-considerations)
11. [Scalability Considerations](#scalability-considerations)
12. [Error Handling Strategy](#error-handling-strategy)
13. [Testing Strategy](#testing-strategy)
14. [Deployment Considerations](#deployment-considerations)

---

## System Architecture

### High-Level Architecture

The system follows a **monolithic web application architecture** with asynchronous background processing:

```
┌─────────────────────────────────────────────────────────────┐
│                     Web Client (Browser)                    │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/HTTPS
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Django Application Server                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Views      │  │   Models     │  │   Serializers│      │
│  │   (MVC)      │  │   (ORM)      │  │   (DRF)      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Templates  │  │   URLs       │  │   Middleware │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   SQLite     │  │    Redis     │  │  OAuth APIs  │
│  (Database)  │  │  (Celery)    │  │ (External)   │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Architectural Decisions

#### 1. Monolithic Architecture
**Decision**: Use a monolithic Django application instead of microservices.

**Rationale**:
- **Simplicity**: Single codebase is easier to develop, test, and deploy
- **Lower Complexity**: No need for inter-service communication, service discovery, or distributed transactions
- **Sufficient Scale**: For a prediction market application, a monolith can handle significant load
- **Development Speed**: Faster iteration with a single deployment pipeline
- **Cost**: Lower infrastructure and operational costs

**Trade-offs**:
- Scaling: Must scale entire application instead of individual components
- Technology lock-in: Harder to adopt different technologies for different components
- Deployment: All changes require full deployment

#### 2. Synchronous Web + Asynchronous Background Tasks
**Decision**: Django for synchronous web requests, Celery for background tasks.

**Rationale**:
- **Separation of Concerns**: Web layer handles user interactions, background layer handles time-consuming operations
- **User Experience**: Web requests remain fast, heavy processing happens asynchronously
- **Reliability**: Background tasks can retry failed operations
- **Scalability**: Can scale web workers and task workers independently

**Trade-offs**:
- Complexity: Requires additional infrastructure (Redis)
- Eventual Consistency: Some operations aren't immediately visible
- Debugging: Background task errors are harder to trace

---

## Technology Stack & Rationale

### Backend Framework: Django 4.2

**Decision**: Use Django over Flask, FastAPI, or other frameworks.

**Rationale**:
- **Batteries-included**: Built-in ORM, admin, authentication, forms reduce development time
- **Maturity**: Proven, stable, well-documented framework
- **Ecosystem**: Large package ecosystem (django-allauth, DRF, etc.)
- **Admin Interface**: Automatic admin panel for data management
- **Security**: Built-in CSRF protection, SQL injection prevention, authentication
- **ORM**: Powerful ORM with migrations, query optimization

**Trade-offs**:
- Performance: Slower than lightweight frameworks like Flask
- Flexibility: Opinionated structure limits architectural freedom
- Learning Curve: Steeper learning curve than simpler frameworks

### API Framework: Django REST Framework (DRF)

**Decision**: Use DRF instead of building custom API or using other frameworks.

**Rationale**:
- **Integration**: Seamless integration with Django models and authentication
- **Serializers**: Automatic serialization/deserialization with validation
- **ViewSets**: CRUD operations with minimal code
- **Documentation**: Built-in API documentation (browsable API)
- **Authentication**: Support for multiple authentication methods (session, token, OAuth)
- **Throttling**: Built-in rate limiting capabilities

**Trade-offs**:
- Coupling: Tightly coupled to Django
- Overhead: Additional layer of abstraction

### Background Tasks: Celery + Redis

**Decision**: Use Celery with Redis broker instead of Django background tasks or other solutions.

**Rationale**:
- **Maturity**: Celery is the industry standard for Python background tasks
- **Features**: Task scheduling, retries, rate limiting, monitoring
- **Scalability**: Can distribute tasks across multiple workers
- **Redis**: Fast in-memory broker with persistence options
- **Scheduling**: Celery Beat for scheduled tasks

**Alternatives Considered**:
- **Django Background Tasks**: Simpler but less feature-rich, no distributed execution
- **RQ (Redis Queue)**: Simpler but fewer features than Celery
- **APScheduler**: Good for scheduling but lacks distributed execution

**Trade-offs**:
- Complexity: Requires Redis infrastructure
- Resource Usage: Additional processes (worker, beat)
- Monitoring: Need to monitor task queue health

### Authentication: django-allauth

**Decision**: Use django-allauth for authentication instead of custom implementation.

**Rationale**:
- **OAuth Support**: Built-in support for Google, GitHub, and other OAuth providers
- **Email Verification**: Built-in email verification workflows
- **Security**: Battle-tested authentication implementation
- **Integration**: Seamless integration with Django user model
- **Flexibility**: Highly customizable while providing sensible defaults

**Trade-offs**:
- Complexity: Additional dependency and configuration
- Customization Limits: Some customizations require deep knowledge of allauth

### Database: SQLite

**Decision**: Use SQLite for development.

**Rationale**:
- **Zero Configuration**: No database server setup required
- **Portability**: Single file database, easy to move/copy
- **Sufficient for Development**: Handles development traffic well
- **Built-in**: No additional dependencies

**Production Consideration**:
- For production, recommend PostgreSQL due to:
  - Better concurrency handling
  - Full-text search capabilities
  - JSONB support for complex queries
  - Better performance under load
  - Advanced features (stored procedures, triggers)

### Frontend: Django Templates

**Decision**: Use Django templates instead of SPA frameworks (React, Vue).

**Rationale**:
- **Simplicity**: Server-side rendering, no build step required
- **Integration**: Seamless integration with Django context and authentication
- **Learning Curve**: Familiar to Django developers
- **Performance**: No client-side JavaScript overhead
- **SEO**: Better SEO out of the box

**Trade-offs**:
- User Experience: No real-time updates without additional setup
- Interactivity: Limited compared to modern SPAs
- Code Splitting: All frontend code in Django project

---

## Design Patterns

### 1. Model-View-Controller (MVC) / Model-View-Template (MVT)

**Implementation**: Django's MVT pattern is the core architectural pattern.

**Components**:
- **Models**: `predictions/models.py` - Data access layer
- **Views**: `predictions/views.py` - Business logic and request handling
- **Templates**: `predictions/templates/` - Presentation layer

**Rationale**:
- **Separation of Concerns**: Clear separation between data, logic, and presentation
- **Maintainability**: Changes to one layer don't affect others
- **Testability**: Each layer can be tested independently
- **Reusability**: Views and templates can be reused across different data

### 2. Repository Pattern (via Django ORM)

**Implementation**: Django ORM acts as a repository abstraction.

**Rationale**:
- **Data Access Abstraction**: Database operations abstracted behind ORM
- **Query Optimization**: ORM provides query optimization and lazy loading
- **Database Independence**: Easy to switch databases (SQLite → PostgreSQL)
- **Type Safety**: Model fields enforce data types

### 3. Serializer Pattern

**Implementation**: DRF serializers in `predictions/serializers.py`.

**Rationale**:
- **Data Transformation**: Clean separation between models and API representation
- **Validation**: Centralized validation logic
- **Flexibility**: Different serializers for different use cases (read vs write)
- **Reusability**: Serializers can be reused across multiple views

**Example**:
```python
# Read serializer with computed fields
class PredictionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    event = EventSerializer(read_only=True)

# Write serializer with validation
class CreatePredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = ["event", "predicted_outcome"]
```

### 4. Factory Pattern (Django Signals)

**Implementation**: User profile creation via signals in `predictions/signals.py`.

**Rationale**:
- **Automatic Creation**: UserProfile created automatically when User is created
- **Decoupling**: User creation logic doesn't need to know about profiles
- **Consistency**: Ensures every user has a profile
- **Single Responsibility**: User creation focuses on user, signal handles profile

### 5. Strategy Pattern (Random Generators)

**Implementation**: Different outcome generators in `predictions/random_generators.py`.

**Rationale**:
- **Algorithm Selection**: Different strategies for different event types
- **Extensibility**: Easy to add new event types with new strategies
- **Encapsulation**: Each generator encapsulates its own logic
- **Testability**: Each generator can be tested independently

**Example**:
```python
def generate_sports_outcome(event):
    # Sports-specific logic

def generate_financial_outcome(event):
    # Financial-specific logic

def generate_random_outcome(event):
    # Random-specific logic
```

### 6. ViewSet Pattern

**Implementation**: DRF ViewSets in `predictions/views.py`.

**Rationale**:
- **CRUD Operations**: Standard CRUD operations with minimal code
- **URL Routing**: Automatic URL generation
- **Consistency**: Uniform API structure across resources
- **DRY**: Don't repeat yourself - common patterns implemented once

### 7. Command Pattern (Management Commands)

**Implementation**: Django management commands like `seed_data.py`.

**Rationale**:
- **Encapsulated Operations**: Each command encapsulates a specific operation
- **Extensibility**: Easy to add new commands
- **Integration**: Seamlessly integrated with Django CLI
- **Testing**: Commands can be tested independently

### 8. Observer Pattern (Django Signals)

**Implementation**: Used for user profile creation.

**Rationale**:
- **Loose Coupling**: Observers (signal handlers) don't need to know about observed (user creation)
- **Event-Driven**: Actions triggered by events
- **Extensibility**: Multiple handlers can observe the same event
- **Maintainability**: New observers can be added without modifying observed code

---

## Database Design

### Schema Design

#### 1. User Extension Pattern

**Decision**: One-to-one relationship to extend Django User model.

**Rationale**:
- **Best Practice**: Django's recommended pattern for extending User
- **Separation**: Keeps User model clean, custom fields in UserProfile
- **Flexibility**: Can add/remove fields without affecting Django's built-in auth
- **Backward Compatibility**: Works with Django's built-in authentication

**Trade-offs**:
- **Query Performance**: Requires JOIN to access profile data
- **Complexity**: Two models instead of one

#### 2. Category Hierarchy

**Decision**: Flat category structure (no hierarchy).

**Rationale**:
- **Simplicity**: Flat structure is sufficient for current needs
- **Performance**: No recursive queries needed
- **Flexibility**: Can add hierarchy later if needed (self-referential FK)

**Extension Point**: If needed, can add `parent` field for hierarchical categories.

#### 3. Entity-Event Many-to-Many

**Decision**: Many-to-many relationship between Entity and Event.

**Rationale**:
- **Flexibility**: Events can involve multiple entities (e.g., sports match with 2 teams)
- **Normalization**: Avoid duplicating entity data for each event
- **Reusability**: Entities can participate in multiple events

**Trade-offs**:
- **Query Complexity**: Requires prefetch/select_related for optimization
- **Data Integrity**: Need to ensure entities are appropriate for event type

#### 4. JSONField for Flexible Data

**Decision**: Use JSONField for outcome, state, and prediction data.

**Rationale**:
- **Flexibility**: Different event types have different data structures
- **Schema Evolution**: Can add fields without migrations
- **Query Support**: Django supports JSON field queries
- **Storage**: Efficient storage of semi-structured data

**Trade-offs**:
- **Type Safety**: No compile-time type checking
- **Validation**: Requires custom validation
- **Query Complexity**: JSON queries can be complex

**Example Usage**:
```python
# Sports outcome
actual_outcome = {
    "result": "Team Alpha",
    "winner": "Team Alpha",
    "team1": "Team Alpha",
    "team2": "Team Beta",
    "team1_score": 3,
    "team2_score": 1
}

# Financial outcome
actual_outcome = {
    "result": "up",
    "previous_price": 100.0,
    "new_price": 105.5,
    "percentage": 5.5
}
```

#### 5. Status Field Pattern

**Decision**: Use CharField with choices for status fields.

**Rationale**:
- **Type Safety**: Restricted to valid choices
- **Readability**: Human-readable choices in code
- **Validation**: Automatic validation at model level
- **Documentation**: Self-documenting field

**Example**:
```python
STATUS_CHOICES = [
    ("pending", "Pending"),
    ("active", "Active"),
    ("resolved", "Resolved"),
    ("cancelled", "Cancelled"),
]
```

#### 6. Timestamp Pattern

**Decision**: Include created_at and updated_at on all models.

**Rationale**:
- **Audit Trail**: Track when records are created/modified
- **Debugging**: Useful for debugging data issues
- **Ordering**: Natural ordering by time
- **Optimistic Locking**: Can use updated_at for conflict detection

#### 7. Unique Constraint Pattern

**Decision**: Unique constraint on (user, event) for predictions.

**Rationale**:
- **Business Rule**: One prediction per user per event
- **Data Integrity**: Enforced at database level
- **Performance**: Efficient lookup of existing predictions
- **Validation**: Model-level validation catches duplicates

**Implementation**:
```python
class Meta:
    unique_together = ["user", "event"]
```

### Indexing Strategy

**Current State**: Uses default indexes (primary keys, foreign keys).

**Recommended Indexes for Production**:
```python
class Event(models.Model):
    # Add these indexes for production
    class Meta:
        indexes = [
            models.Index(fields=['status', 'end_time']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['start_time', 'end_time']),
        ]

class Prediction(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['event', 'status']),
            models.Index(fields=['created_at']),
        ]
```

**Rationale**:
- **Query Optimization**: Speed up common queries
- **Filter Performance**: Indexes on frequently filtered fields
- **Sorting**: Indexes support efficient sorting

---

## API Design

### RESTful API Principles

**Decision**: Follow REST principles for API design.

**Rationale**:
- **Standardization**: Industry-standard approach
- **Interoperability**: Easy to consume by various clients
- **Statelessness**: Each request contains all necessary information
- **Scalability**: Stateless design scales better

### Resource Naming

**Convention**: Use plural nouns for resource names.

**Examples**:
- `/api/categories/` - List of categories
- `/api/events/` - List of events
- `/api/predictions/` - List of predictions

**Rationale**:
- **Consistency**: Consistent naming across all endpoints
- **Intuitiveness**: Plural nouns represent collections
- **REST Best Practice**: Follows REST conventions

### HTTP Method Usage

**Decision**: Use appropriate HTTP methods for operations.

**Mapping**:
- `GET` - Retrieve resources (read-only, idempotent)
- `POST` - Create resources (non-idempotent)
- `PUT/PATCH` - Update resources (idempotent for PUT)
- `DELETE` - Delete resources (idempotent)

**Current Implementation**:
- `GET /api/categories/` - List categories
- `GET /api/events/` - List events
- `GET /api/events/<id>/` - Get specific event
- `POST /api/predictions/` - Create prediction
- `GET /api/predictions/my_predictions/` - Get user's predictions

**Rationale**:
- **Semantic**: HTTP methods have clear semantics
- **Caching**: GET requests can be cached
- **Idempotency**: PUT/DELETE are idempotent, easier to retry

### ViewSet vs APIView

**Decision**: Use ViewSets for standard CRUD, APIView for custom logic.

**Rationale**:
- **ViewSet**: Standard CRUD operations require minimal code
- **APIView**: Custom actions need full control
- **Consistency**: ViewSets provide consistent structure
- **DRY**: Don't repeat common patterns

**Example**:
```python
# ViewSet for standard CRUD
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# Custom actions with @action decorator
@action(detail=False, methods=["get"])
def active(self, request):
    active_events = self.get_queryset().filter(status="active")
    serializer = self.get_serializer(active_events, many=True)
    return Response(serializer.data)
```

### Serialization Strategy

**Decision**: Separate serializers for read vs write operations.

**Rationale**:
- **Security**: Write serializer with limited fields prevents overwriting
- **Validation**: Write serializer can include custom validation
- **Performance**: Read serializer can include computed fields
- **Flexibility**: Different representations for different contexts

**Example**:
```python
# Read serializer with nested data
class PredictionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    event = EventSerializer(read_only=True)

# Write serializer with validation
class CreatePredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = ["event", "predicted_outcome"]

    def validate(self, data):
        # Custom validation logic
        pass
```

### Permission Strategy

**Decision**: Use DRF permission classes for access control.

**Implementation**:
- `AllowAny` - Public endpoints (categories, events, leaderboard)
- `IsAuthenticated` - Protected endpoints (predictions, user score)

**Rationale**:
- **Declarative**: Clear permission declaration
- **Reusable**: Permission classes can be reused
- **Testability**: Easy to test permission logic
- **Flexibility**: Can create custom permission classes

**Extension**: For production, consider:
- `IsOwnerOrReadOnly` - Users can only edit their own predictions
- `IsAdminUser` - Admin-only endpoints

### Query Optimization

**Decision**: Use select_related and prefetch_related for optimization.

**Implementation**:
```python
queryset = Event.objects.select_related("category").prefetch_related("entities")
```

**Rationale**:
- **N+1 Problem**: Prevents N+1 query problem
- **Performance**: Reduces database queries
- **Select Related**: For ForeignKey (single object)
- **Prefetch Related**: For ManyToMany (multiple objects)

### Custom Actions

**Decision**: Use @action decorator for custom endpoints.

**Examples**:
- `/api/events/active/` - Get only active events
- `/api/predictions/my_predictions/` - Get current user's predictions

**Rationale**:
- **Organization**: Related actions grouped with resource
- **URL Generation**: Automatic URL generation
- **Consistency**: Consistent with REST principles
- **DRY**: Reuses ViewSet logic

---

## Authentication & Authorization

### Authentication Strategy

**Decision**: Multi-layer authentication approach.

**Layers**:
1. **Session Authentication** - For web interface
2. **Token Authentication** - For API access
3. **OAuth Authentication** - For social login

**Rationale**:
- **Flexibility**: Different methods for different use cases
- **Security**: Token-based for API, session-based for web
- **User Experience**: OAuth provides convenient social login
- **Best Practice**: Industry-standard approach

### OAuth Implementation

**Decision**: Use django-allauth for OAuth.

**Providers Supported**:
- Google OAuth
- GitHub OAuth

**Rationale**:
- **Security**: Don't store passwords, rely on OAuth providers
- **User Experience**: Users don't need to remember another password
- **Trust**: Users trust established OAuth providers
- **Verification**: OAuth providers verify user identity

**Implementation Details**:
- Callback URLs configured in Django settings
- OAuth credentials stored in environment variables
- Email verification optional (can be enabled for production)

### User Profile Extension

**Decision**: One-to-one relationship to extend User model.

**Rationale**:
- **Separation**: Keep Django User model clean
- **Custom Fields**: Add prediction-specific fields (score, stats)
- **Signals**: Automatic profile creation on user creation
- **Best Practice**: Django's recommended approach

### Authorization Model

**Current State**: Simple authenticated/unauthenticated model.

**Implementation**:
- Public: Categories, events, leaderboard
- Authenticated: Predictions, user score, dashboard

**Rationale**:
- **Simplicity**: Sufficient for current requirements
- **Security**: Protects user-specific data
- **Scalability**: Can add role-based access control later

**Extension for Production**:
```python
# Add roles
class UserRole(models.Model):
    USER = 'user'
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    ROLE_CHOICES = [
        (USER, 'User'),
        (ADMIN, 'Admin'),
        (MODERATOR, 'Moderator'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=USER)

# Custom permissions
class IsAdminOrModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.profile.role in ['admin', 'moderator']
```

### Session Management

**Decision**: Use Django's built-in session management.

**Rationale**:
- **Security**: Django handles session security (CSRF, secure cookies)
- **Simplicity**: No custom session implementation needed
- **Scalability**: Can use database-backed or cached sessions
- **Best Practice**: Battle-tested session management

**Configuration**:
```python
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_SECURE = True  # HTTPS only in production
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
```

---

## Background Task Architecture

### Task Queue Pattern

**Decision**: Use Celery with Redis broker for task queuing.

**Architecture**:
```
Django App → Redis Queue → Celery Worker → Task Execution
     ↓
Celery Beat → Scheduled Tasks → Redis Queue → Celery Worker
```

**Rationale**:
- **Asynchronous Processing**: Long-running tasks don't block web requests
- **Reliability**: Tasks persist in queue even if worker fails
- **Scalability**: Multiple workers can process tasks in parallel
- **Scheduling**: Celery Beat for scheduled tasks
- **Monitoring**: Task status and results can be monitored

### Task Types

**1. Event Resolution Task** (`resolve_event`)
- **Purpose**: Resolve a specific event and update scores
- **Trigger**: When event end time is reached
- **Logic**:
  1. Generate random outcome based on event type
  2. Update event status to "resolved"
  3. Compare predictions with actual outcome
  4. Update user scores

**2. Batch Resolution Task** (`resolve_expired_events`)
- **Purpose**: Resolve all expired events
- **Trigger**: Scheduled (e.g., every minute)
- **Logic**:
  1. Find all events with status="active" and end_time <= now
  2. Queue individual resolution tasks for each event

**3. Entity State Update Task** (`generate_random_entity_states`)
- **Purpose**: Update entity states randomly
- **Trigger**: Scheduled (e.g., every hour)
- **Logic**:
  1. Get all entities
  2. Update states based on entity type
  3. Save changes

### Task Design Principles

**1. Idempotency**
- Tasks should be safe to run multiple times
- Check conditions before performing actions
- Example: Check event status before resolving

**2. Error Handling**
- Tasks should handle errors gracefully
- Log errors for debugging
- Use Celery's retry mechanism for transient failures

**3. Atomicity**
- Database operations should be atomic
- Use Django transactions for data consistency
- Example: Score updates wrapped in transaction

**4. Monitoring**
- Tasks should return meaningful status
- Success/failure can be tracked
- Use Celery result backend for task results

### Scheduling Strategy

**Decision**: Use Celery Beat for scheduled tasks.

**Configuration** (for production):
```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    'resolve-expired-events': {
        'task': 'predictions.tasks.resolve_expired_events',
        'schedule': crontab(minute='*'),  # Every minute
    },
    'update-entity-states': {
        'task': 'predictions.tasks.generate_random_entity_states',
        'schedule': crontab(minute=0),  # Every hour
    },
}
```

**Rationale**:
- **Reliability**: Celery Beat handles scheduling reliably
- **Flexibility**: Cron-like syntax for complex schedules
- **Distributed**: Multiple beat workers can run (with locks)
- **Monitoring**: Scheduled tasks are visible in monitoring

### Error Handling Strategy

**Current Implementation**: Basic error handling in tasks.

**Recommended Enhancements**:
```python
@shared_task(bind=True, max_retries=3)
def resolve_event(self, event_id):
    try:
        event = Event.objects.get(id=event_id)
        # Task logic
    except Event.DoesNotExist:
        logger.error(f"Event {event_id} does not exist")
        raise
    except Exception as exc:
        logger.error(f"Error resolving event {event_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)
```

**Rationale**:
- **Retries**: Transient errors can be retried
- **Logging**: Errors logged for debugging
- **Monitoring**: Failed tasks can be monitored
- **Graceful Degradation**: System continues despite task failures

---

## Random Entity Behavior System

### Generator Pattern

**Decision**: Separate generator functions for each event type.

**Architecture**:
```
Event Type → Generator Function → Outcome Data
```

**Generators**:
1. `generate_sports_outcome()` - Sports match outcomes
2. `generate_financial_outcome()` - Financial price movements
3. `generate_random_outcome()` - Random events (coin flip, dice)
4. `generate_custom_outcome()` - Custom entity selection

**Rationale**:
- **Separation of Concerns**: Each generator handles its own logic
- **Extensibility**: Easy to add new event types
- **Testability**: Each generator can be tested independently
- **Flexibility**: Different algorithms for different event types

### Sports Outcome Algorithm

**Algorithm**:
1. Get participating teams/entities
2. Extract team strengths from current_state
3. Calculate win probability based on strength ratio
4. Add randomness (70% skill, 30% chance)
5. Generate random score for each team
6. Return outcome with winner and scores

**Example**:
```python
team1_strength = 60
team2_strength = 50
total_strength = 110
team1_prob = 60/110 = 0.545

# Random factor determines winner
# 70% chance winner follows probability
# 30% chance random upset
```

**Rationale**:
- **Realism**: Stronger teams have higher probability of winning
- **Unpredictability**: Random element allows for upsets
- **Balance**: Skill vs chance balance makes predictions interesting

### Financial Outcome Algorithm

**Algorithm**:
1. Get current price from entity state
2. Generate random percentage change (-10% to +10%)
3. Calculate new price
4. Determine direction (up/down/no change)
5. Return outcome with previous/new price and percentage

**Example**:
```python
current_price = 100.0
change_percent = random.uniform(-10, 10)  # e.g., 5.5
new_price = 100.0 * (1 + 0.055) = 105.5
result = "up"
```

**Rationale**:
- **Simplicity**: Simple random walk model
- **Range**: Reasonable price movement range
- **Direction**: Clear up/down/no change outcomes

**Note**: This is a simplified model and doesn't reflect real market behavior.

### Random Event Algorithm

**Algorithm**:
1. Parse event description to determine type
2. Based on type, generate appropriate random outcome:
   - Coin flip: heads/tails
   - Dice roll: 1-6
   - Random number: 1-100
   - Custom choice: random from options

**Rationale**:
- **Flexibility**: Can handle various random event types
- **Simplicity**: Simple random generation
- **Predictability**: Known probability distributions

### Entity State Updates

**Algorithm**:
1. Iterate through all entities
2. Based on entity type, update state:
   - Stock: Random price movement (-5% to +5%)
   - Random: Random value (1-100)
3. Save updated state

**Rationale**:
- **Dynamic**: Entity states change over time
- **Background**: Updates happen asynchronously
- **Independence**: Each entity updated independently

### Randomness Quality

**Current Implementation**: Uses Python's `random` module.

**For Production Consideration**:
- Use `secrets` module for cryptographic randomness
- Use dedicated random number generators for statistical randomness
- Seed random generators with entropy sources
- Consider external randomness services for true randomness

**Example**:
```python
import secrets

# Cryptographically secure random
def generate_secure_random():
    return secrets.randbelow(100)
```

---

## Frontend Architecture

### Template Hierarchy

**Decision**: Use Django template inheritance.

**Structure**:
```
base.html (base template)
├── home.html
├── dashboard.html
├── leaderboard.html
└── event_detail.html
```

**Rationale**:
- **DRY**: Common layout code in base template
- **Consistency**: Consistent look and feel across pages
- **Maintainability**: Changes to base template affect all pages
- **Flexibility**: Child templates can override specific blocks

### CSS Strategy

**Decision**: Inline CSS in base template for simplicity.

**Current State**: All CSS in `<style>` block in base.html.

**Rationale**:
- **Simplicity**: No build step required
- **Portability**: Single file contains all styles
- **Development Speed**: Fast iteration during development

**Production Consideration**:
- Extract to separate CSS file
- Use CSS preprocessor (SASS/LESS) for maintainability
- Minify CSS for production
- Consider CSS framework (Bootstrap, Tailwind)

### JavaScript Strategy

**Decision**: Minimal JavaScript, server-side processing.

**Current State**: Only form submissions, no complex client-side logic.

**Rationale**:
- **Simplicity**: No JavaScript framework complexity
- **Progressive Enhancement**: Works without JavaScript
- **Performance**: Faster initial page load
- **SEO**: Better search engine optimization

**Extension for Production**:
- Add JavaScript for real-time updates (WebSockets)
- Form validation on client side
- AJAX for non-blocking operations
- Progressive enhancement approach

### Form Handling

**Decision**: Django form handling with CSRF protection.

**Implementation**:
- Server-side form validation
- CSRF token for protection
- POST requests for data modification

**Rationale**:
- **Security**: CSRF protection built-in
- **Validation**: Server-side validation is authoritative
- **Accessibility**: Forms work without JavaScript
- **Progressive Enhancement**: Works with or without JS

### Navigation Structure

**Decision**: Simple navigation bar with conditional links.

**Links**:
- Always: Home, Leaderboard
- Authenticated: Dashboard, Logout, Score display
- Unauthenticated: Login, Sign Up

**Rationale**:
- **User Experience**: Context-aware navigation
- **Security**: Show/hide links based on auth state
- **Simplicity**: Easy to understand navigation

### Error Display

**Decision**: Simple error messages via Django messages framework.

**Current State**: Basic error handling in views.

**Rationale**:
- **User Experience**: Clear error messages
- **Integration**: Django's built-in messages framework
- **Flexibility**: Can be styled as needed

**Extension**: Add error page templates (404, 500) for better UX.

---

## Security Considerations

### Authentication Security

**Implementations**:
1. **Password Hashing**: Django uses PBKDF2 with SHA256
2. **Session Security**: Secure cookies, HTTPOnly, SameSite
3. **OAuth Security**: Provider-side authentication
4. **CSRF Protection**: Django's built-in CSRF middleware

**Best Practices**:
- Use HTTPS in production
- Enable secure cookie flags
- Set appropriate session expiration
- Implement rate limiting

### Authorization Security

**Current State**: Simple authenticated/unauthenticated model.

**Best Practices**:
- Object-level permissions (users can only edit their own data)
- Role-based access control for admin operations
- API rate limiting to prevent abuse
- Input validation on all endpoints

### Data Validation

**Implementation**:
- Model-level validation (field types, choices)
- Serializer-level validation (custom validation)
- Database constraints (unique constraints, foreign keys)

**Example**:
```python
def validate(self, data):
    user = self.context["request"].user
    event = data["event"]
    
    if event.status != "active":
        raise serializers.ValidationError("Event is not active")
    
    if Prediction.objects.filter(user=user, event=event).exists():
        raise serializers.ValidationError("Already predicted")
    
    return data
```

### SQL Injection Prevention

**Implementation**: Django ORM automatically prevents SQL injection.

**Rationale**:
- **Parameterized Queries**: ORM uses parameterized queries
- **No Raw SQL**: Avoid raw SQL queries when possible
- **Validation**: Input validation before database operations

### XSS Prevention

**Implementation**: Django templates auto-escape by default.

**Rationale**:
- **Auto-escaping**: Prevents script injection
- **Context Awareness**: Escapes based on context
- **Explicit Marking**: Can mark safe strings when needed

### CSRF Protection

**Implementation**: Django's built-in CSRF middleware.

**Mechanism**:
- CSRF token generated for each session
- Token included in forms
- Token validated on POST requests
- AJAX requests require special handling

**Best Practices**:
- Use CSRF exempt only when necessary
- Validate CSRF on all state-changing operations
- Use SameSite cookie attribute

### Secrets Management

**Implementation**: Environment variables via python-decouple.

**Rationale**:
- **No Hardcoded Secrets**: Secrets in environment variables
- **Separation**: .env file not committed to version control
- **Flexibility**: Different configs for dev/staging/prod

**Example**:
```python
SECRET_KEY = config("SECRET_KEY")
GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID")
```

### API Security

**Implementations**:
1. **Authentication Required**: Protected endpoints require auth
2. **Rate Limiting**: Can be added via DRF throttling
3. **CORS**: Configured for specific origins
4. **HTTPS**: Required in production

**Future Enhancements**:
- API key authentication for external integrations
- Request signing for sensitive operations
- IP whitelisting for admin operations

---

## Scalability Considerations

### Database Scalability

**Current State**: SQLite for development.

**Production Recommendations**:
1. **PostgreSQL**:
   - Better concurrency handling
   - Connection pooling
   - Read replicas for scaling reads
   - Partitioning for large tables

2. **Connection Pooling**:
   - Use PgBouncer or Django connection pool
   - Reduce connection overhead
   - Handle connection spikes

3. **Query Optimization**:
   - Add indexes on frequently queried fields
   - Use `select_related` and `prefetch_related`
   - Monitor slow queries
   - Use database-specific features (JSONB)

### Application Scalability

**Current State**: Single Django application server.

**Production Recommendations**:
1. **Load Balancing**:
   - Use Nginx or HAProxy
   - Distribute load across multiple app servers
   - Health checks for failover

2. **Horizontal Scaling**:
   - Stateless application design
   - Multiple app instances
   - Auto-scaling based on load

3. **Caching**:
   - Redis for caching
   - Cache frequently accessed data
   - Cache template fragments
   - Cache API responses

### Background Task Scalability

**Current State**: Single Celery worker.

**Production Recommendations**:
1. **Multiple Workers**:
   - Run multiple worker processes
   - Scale based on queue size
   - Different queues for different task types

2. **Worker Autoscaling**:
   - Scale workers based on queue length
   - Use Kubernetes or similar
   - Monitor worker health

3. **Task Prioritization**:
   - High priority queue for urgent tasks
   - Low priority queue for batch tasks
   - Configure worker priorities

### File Storage Scalability

**Current State**: Local file storage (static files).

**Production Recommendations**:
1. **CDN**:
   - Use CloudFront, Cloudflare, or similar
   - Serve static files from CDN
   - Reduce load on app servers

2. **Object Storage**:
   - Use S3 or similar for user uploads
   - Separate storage from app servers
   - Handle large files efficiently

### Session Storage Scalability

**Current State**: Database-backed sessions.

**Production Recommendations**:
1. **Redis Sessions**:
   - Faster than database sessions
   - Better for distributed systems
   - Automatic expiration

2. **Sticky Sessions**:
   - If using local storage, use sticky sessions
   - But Redis is preferred

### Monitoring and Observability

**Current State**: Basic logging.

**Production Recommendations**:
1. **Application Monitoring**:
   - Use Sentry for error tracking
   - Use New Relic or Datadog for APM
   - Monitor response times, error rates

2. **Infrastructure Monitoring**:
   - CPU, memory, disk usage
   - Network latency
   - Queue lengths

3. **Logging**:
   - Structured logging (JSON format)
   - Centralized logging (ELK stack)
   - Log correlation (request IDs)

---

## Error Handling Strategy

### Web Request Errors

**Implementation**:
- Django's built-in error handling
- Custom error pages (404, 500)
- Exception middleware for custom handling

**Strategy**:
1. **Validation Errors**: Return user-friendly messages
2. **Not Found Errors**: Return 404 with appropriate message
3. **Server Errors**: Return 500, log error, notify admins
4. **Permission Errors**: Return 403 with explanation

### API Errors

**Implementation**: DRF exception handling.

**Strategy**:
1. **Validation Errors**: 400 with field-level errors
2. **Authentication Errors**: 401 with challenge
3. **Permission Errors**: 403 with explanation
4. **Not Found Errors**: 404 with resource identifier
5. **Server Errors**: 500 with generic message

**Example**:
```python
class CreatePredictionSerializer(serializers.ModelSerializer):
    def validate(self, data):
        if event.status != "active":
            raise serializers.ValidationError(
                {"event": "Event is not active for predictions"}
            )
        return data
```

### Background Task Errors

**Implementation**: Celery error handling.

**Strategy**:
1. **Retry Logic**: Retry transient failures
2. **Error Logging**: Log all errors with context
3. **Dead Letter Queue**: Failed tasks go to DLQ
4. **Monitoring**: Alert on high failure rates

**Example**:
```python
@shared_task(bind=True, max_retries=3)
def resolve_event(self, event_id):
    try:
        # Task logic
    except Exception as exc:
        logger.error(f"Error: {exc}")
        raise self.retry(exc=exc, countdown=60)
```

### Database Errors

**Implementation**: Django ORM error handling.

**Strategy**:
1. **Constraint Violations**: Catch and return user-friendly message
2. **Connection Errors**: Retry with exponential backoff
3. **Transaction Errors**: Rollback and retry
4. **Deadlocks**: Implement retry logic

### Logging Strategy

**Current State**: Basic logging.

**Best Practices**:
1. **Structured Logging**: JSON format for parsing
2. **Log Levels**: Use appropriate levels (DEBUG, INFO, WARNING, ERROR)
3. **Context**: Include request ID, user ID in logs
4. **Centralization**: Send logs to centralized service

**Example**:
```python
import logging

logger = logging.getLogger(__name__)

def resolve_event(event_id):
    logger.info(f"Resolving event {event_id}")
    try:
        # Logic
        logger.info(f"Event {event_id} resolved successfully")
    except Exception as e:
        logger.error(f"Failed to resolve event {event_id}: {e}", exc_info=True)
```

---

## Testing Strategy

### Testing Pyramid

**Recommended Structure**:
```
    /\
   /E2E\    - End-to-end tests (few)
  /------\
 /Integration\ - Integration tests (more)
/------------\
    |          - Unit tests (most)
```

### Unit Tests

**Focus**: Test individual functions and methods in isolation.

**Examples**:
- Test random generators with known seeds
- Test model methods
- Test serializer validation
- Test utility functions

**Example**:
```python
from predictions.random_generators import generate_random_outcome
from predictions.models import Event

def test_coin_flip():
    event = Event(event_type="random", description="coin flip")
    result = generate_random_outcome(event)
    assert result["result"] in ["heads", "tails"]
    assert result["type"] == "coin_flip"
```

### Integration Tests

**Focus**: Test interactions between components.

**Examples**:
- Test API endpoints with database
- Test view with models
- Test background task execution
- Test authentication flow

**Example**:
```python
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User

class PredictionAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="test", password="test")
        self.client.force_authenticate(user=self.user)
    
    def test_create_prediction(self):
        response = self.client.post("/api/predictions/", {
            "event": 1,
            "predicted_outcome": {"result": "heads"}
        })
        self.assertEqual(response.status_code, 201)
```

### End-to-End Tests

**Focus**: Test complete user workflows.

**Examples**:
- Test complete prediction flow (register → login → predict → check score)
- Test event resolution flow (create event → wait → resolve → check scores)
- Test OAuth login flow

**Tools**: Selenium, Playwright, or similar.

### Test Data Management

**Strategy**:
- Use factories (factory_boy) for test data
- Rollback transactions after each test
- Use separate test database
- Seed test data with management command

### Background Task Testing

**Strategy**:
- Test task logic synchronously
- Mock Celery for unit tests
- Test task queue in integration tests
- Test task retries and error handling

**Example**:
```python
from predictions.tasks import resolve_event
from predictions.models import Event

def test_resolve_event():
    event = Event.objects.create(
        title="Test Event",
        status="active",
        end_time=timezone.now() - timedelta(hours=1)
    )
    result = resolve_event(event.id)
    event.refresh_from_db()
    assert event.status == "resolved"
```

---

## Deployment Considerations

### Development Deployment

**Current Setup**:
- SQLite database
- Development server (runserver)
- Local Redis (optional)
- Debug mode enabled

**Configuration**:
```python
DEBUG = True
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
```

### Production Deployment

**Recommended Stack**:
- **Web Server**: Nginx (reverse proxy, static files)
- **Application Server**: Gunicorn (WSGI server)
- **Database**: PostgreSQL
- **Cache/Queue**: Redis
- **Process Manager**: Supervisor or systemd
- **SSL**: Let's Encrypt or paid certificate

**Gunicorn Configuration**:
```bash
gunicorn prediction_market.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class sync \
    --timeout 120
```

**Nginx Configuration**:
```nginx
server {
    listen 80;
    server_name example.com;

    location /static/ {
        alias /path/to/static/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Celery Deployment

**Configuration**:
```bash
# Worker
celery -A prediction_market worker -l info -c 4

# Beat
celery -A prediction_market beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

**Process Management** (systemd):
```ini
[Unit]
Description=Celery Worker
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/project
ExecStart=/path/to/venv/bin/celery -A prediction_market worker -l info
Restart=always

[Install]
WantedBy=multi-user.target
```

### Environment Configuration

**Strategy**: Separate configs for each environment.

**Files**:
- `.env.development` - Development settings
- `.env.staging` - Staging settings
- `.env.production` - Production settings

**Loading**:
```python
from decouple import config

env = config("ENVIRONMENT", default="development")
load_dotenv(f".env.{env}")
```

### Static Files

**Strategy**:
- Development: Django serves static files
- Production: Nginx serves static files

**Commands**:
```bash
# Collect static files
python manage.py collectstatic

# Configure STATIC_ROOT
STATIC_ROOT = BASE_DIR / "staticfiles"
```

### Database Migrations

**Strategy**:
- Run migrations during deployment
- Use zero-downtime migrations for large tables
- Test migrations on staging first

**Deployment Script**:
```bash
# Backup database
pg_dump dbname > backup.sql

# Run migrations
python manage.py migrate

# If migration fails, restore
psql dbname < backup.sql
```

### Monitoring and Alerting

**Recommended Tools**:
- **Application Monitoring**: Sentry (errors), New Relic (APM)
- **Infrastructure Monitoring**: Datadog, CloudWatch
- **Log Aggregation**: ELK stack, CloudWatch Logs
- **Uptime Monitoring**: Pingdom, UptimeRobot

**Alerts**:
- High error rate
- High response time
- Database connection issues
- Celery queue backlog
- Disk space low

### Backup Strategy

**Components to Backup**:
1. **Database**: Regular backups (daily + hourly)
2. **Media Files**: Object storage with versioning
3. **Configuration**: Version control
4. **Redis**: Periodic snapshots

**Backup Schedule**:
- Database: Daily full backups, hourly incremental
- Redis: Daily snapshots
- Configuration: Continuous (git)

### Rollback Strategy

**Procedure**:
1. Keep previous deployment available
2. Database migrations should be reversible
3. Feature flags for new features
4. Canary deployments for risky changes

**Example**:
```bash
# Deploy new version
git pull origin main
python manage.py migrate
systemctl restart gunicorn

# If issues, rollback
git checkout previous_version
python manage.py migrate previous_migration
systemctl restart gunicorn
```

### CI/CD Pipeline

**Recommended Tools**:
- **CI**: GitHub Actions, GitLab CI, CircleCI
- **CD**: GitHub Actions, GitLab CI, or separate tool

**Pipeline Stages**:
1. **Lint**: Code quality checks
2. **Test**: Run test suite
3. **Build**: Build Docker image (if using Docker)
4. **Deploy**: Deploy to staging
5. **Integration Tests**: Run against staging
6. **Deploy Production**: Manual approval required

**Example GitHub Actions**:
```yaml
name: CI/CD

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python manage.py test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: ./deploy.sh
```

---

## Summary

This prediction market system follows industry best practices for Django web applications with a focus on:

- **Simplicity**: Monolithic architecture for ease of development
- **Scalability**: Designed to scale horizontally when needed
- **Security**: Multiple layers of security (auth, CSRF, validation)
- **Maintainability**: Clean code with clear separation of concerns
- **Extensibility**: Easy to add new features and event types
- **Reliability**: Background tasks with error handling and retries

The system is production-ready with proper error handling, logging, and deployment considerations documented. The architecture allows for growth from a simple MVP to a large-scale production system.
