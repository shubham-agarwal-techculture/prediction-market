from django.contrib import admin
from .models import UserProfile, Category, Entity, Event, Prediction


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "score", "total_predictions", "correct_predictions", "win_rate"]
    list_filter = ["created_at"]
    search_fields = ["user__username", "user__email"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    search_fields = ["name"]


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ["name", "entity_type", "category", "created_at"]
    list_filter = ["entity_type", "category"]
    search_fields = ["name"]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "event_type", "status", "start_time", "end_time"]
    list_filter = ["status", "event_type", "category"]
    search_fields = ["title", "description"]
    filter_horizontal = ["entities"]


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ["user", "event", "status", "points_won", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["user__username", "event__title"]

