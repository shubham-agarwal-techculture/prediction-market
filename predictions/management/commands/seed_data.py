from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from predictions.models import Category, Entity, Event


class Command(BaseCommand):
    help = "Seed the database with sample data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding database with sample data...")

        # Create categories
        sports_cat, _ = Category.objects.get_or_create(
            name="Sports",
            defaults={"description": "Sports matches and events"}
        )
        financial_cat, _ = Category.objects.get_or_create(
            name="Financial",
            defaults={"description": "Financial market predictions"}
        )
        random_cat, _ = Category.objects.get_or_create(
            name="Random",
            defaults={"description": "Random events"}
        )

        # Create entities
        team1, _ = Entity.objects.get_or_create(
            name="Team Alpha",
            defaults={
                "entity_type": "team",
                "category": sports_cat,
                "current_state": {"strength": 60}
            }
        )
        team2, _ = Entity.objects.get_or_create(
            name="Team Beta",
            defaults={
                "entity_type": "team",
                "category": sports_cat,
                "current_state": {"strength": 50}
            }
        )

        stock1, _ = Entity.objects.get_or_create(
            name="Tech Stock",
            defaults={
                "entity_type": "stock",
                "category": financial_cat,
                "current_state": {"price": 100.0}
            }
        )

        # Create events
        now = timezone.now()
        
        # Active sports event
        sports_event, _ = Event.objects.get_or_create(
            title="Team Alpha vs Team Beta",
            defaults={
                "description": "Who will win the match?",
                "category": sports_cat,
                "event_type": "match",
                "start_time": now - timedelta(hours=1),
                "end_time": now + timedelta(hours=2),
                "status": "active"
            }
        )
        sports_event.entities.add(team1, team2)

        # Active financial event
        financial_event, _ = Event.objects.get_or_create(
            title="Tech Stock Price Movement",
            defaults={
                "description": "Will the stock price go up or down?",
                "category": financial_cat,
                "event_type": "price",
                "start_time": now - timedelta(hours=1),
                "end_time": now + timedelta(hours=1),
                "status": "active"
            }
        )
        financial_event.entities.add(stock1)

        # Active random event
        Event.objects.get_or_create(
            title="Coin Flip",
            defaults={
                "description": "Heads or tails?",
                "category": random_cat,
                "event_type": "random",
                "start_time": now - timedelta(minutes=30),
                "end_time": now + timedelta(minutes=30),
                "status": "active"
            }
        )

        # Pending event
        future_event, _ = Event.objects.get_or_create(
            title="Future Match",
            defaults={
                "description": "Upcoming match prediction",
                "category": sports_cat,
                "event_type": "match",
                "start_time": now + timedelta(hours=5),
                "end_time": now + timedelta(hours=7),
                "status": "pending"
            }
        )
        future_event.entities.add(team1, team2)

        self.stdout.write(self.style.SUCCESS("Sample data seeded successfully!"))
