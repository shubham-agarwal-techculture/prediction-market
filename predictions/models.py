from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    score = models.IntegerField(default=0)
    total_predictions = models.IntegerField(default=0)
    correct_predictions = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Score: {self.score}"

    @property
    def win_rate(self):
        if self.total_predictions == 0:
            return 0.0
        return (self.correct_predictions / self.total_predictions) * 100


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Entity(models.Model):
    ENTITY_TYPES = [
        ("team", "Team"),
        ("stock", "Stock"),
        ("random", "Random Generator"),
        ("custom", "Custom"),
    ]

    name = models.CharField(max_length=200)
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPES, default="custom")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="entities")
    current_state = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.entity_type})"


class Event(models.Model):
    EVENT_TYPES = [
        ("match", "Sports Match"),
        ("price", "Price Movement"),
        ("random", "Random Event"),
        ("custom", "Custom Event"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("active", "Active"),
        ("resolved", "Resolved"),
        ("cancelled", "Cancelled"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default="custom")
    entities = models.ManyToManyField(Entity, related_name="events", blank=True)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    actual_outcome = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.status})"

    @property
    def is_active(self):
        now = timezone.now()
        return self.status == "active" and self.start_time <= now <= self.end_time

    @property
    def is_resolved(self):
        return self.status == "resolved"


class Prediction(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("correct", "Correct"),
        ("incorrect", "Incorrect"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="predictions")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="predictions")
    predicted_outcome = models.JSONField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    points_won = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.event.title} ({self.status})"

    class Meta:
        unique_together = ["user", "event"]
