from celery import shared_task
from django.utils import timezone
from .models import Event, Prediction, UserProfile
from .random_generators import (
    generate_sports_outcome,
    generate_financial_outcome,
    generate_random_outcome,
    generate_custom_outcome,
)


@shared_task
def resolve_event(event_id):
    try:
        event = Event.objects.get(id=event_id)
        if event.status != "active":
            return f"Event {event_id} is not active"

        now = timezone.now()
        if now < event.end_time:
            return f"Event {event_id} has not ended yet"

        outcome = None
        if event.event_type == "match":
            outcome = generate_sports_outcome(event)
        elif event.event_type == "price":
            outcome = generate_financial_outcome(event)
        elif event.event_type == "random":
            outcome = generate_random_outcome(event)
        else:
            outcome = generate_custom_outcome(event)

        event.actual_outcome = outcome
        event.status = "resolved"
        event.save()

        update_user_scores(event)

        return f"Event {event_id} resolved successfully"
    except Event.DoesNotExist:
        return f"Event {event_id} does not exist"


@shared_task
def update_user_scores(event):
    predictions = Prediction.objects.filter(event=event, status="pending")

    for prediction in predictions:
        is_correct = compare_outcomes(prediction.predicted_outcome, event.actual_outcome)

        prediction.status = "correct" if is_correct else "incorrect"
        profile = prediction.user.profile

        if is_correct:
            prediction.points_won = 10
            profile.score += 10
            profile.correct_predictions += 1
        else:
            prediction.points_won = 0

        profile.total_predictions += 1
        profile.save()
        prediction.save()


def compare_outcomes(predicted, actual):
    if isinstance(predicted, dict) and isinstance(actual, dict):
        return predicted.get("result") == actual.get("result")
    return predicted == actual


@shared_task
def resolve_expired_events():
    now = timezone.now()
    expired_events = Event.objects.filter(status="active", end_time__lte=now)

    for event in expired_events:
        resolve_event.delay(event.id)

    return f"Queued resolution for {expired_events.count()} expired events"


@shared_task
def generate_random_entity_states():
    from .models import Entity
    import random

    entities = Entity.objects.all()
    for entity in entities:
        if entity.entity_type == "stock":
            current_price = entity.current_state.get("price", 100)
            change_percent = random.uniform(-5, 5)
            new_price = current_price * (1 + change_percent / 100)
            entity.current_state = {"price": round(new_price, 2)}
        elif entity.entity_type == "random":
            entity.current_state = {"value": random.randint(1, 100)}
        entity.save()

    return f"Updated states for {entities.count()} entities"
