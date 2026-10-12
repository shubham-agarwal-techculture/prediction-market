from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Category, Entity, Event, Prediction


class UserProfileSerializer(serializers.ModelSerializer):
    win_rate = serializers.ReadOnlyField()

    class Meta:
        model = UserProfile
        fields = ["score", "total_predictions", "correct_predictions", "win_rate"]


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "profile"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description", "created_at"]


class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = ["id", "name", "entity_type", "category", "current_state", "created_at", "updated_at"]


class EventSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    entities = EntitySerializer(many=True, read_only=True)
    is_active = serializers.ReadOnlyField()
    is_resolved = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "category",
            "event_type",
            "entities",
            "start_time",
            "end_time",
            "status",
            "actual_outcome",
            "is_active",
            "is_resolved",
            "created_at",
            "updated_at",
        ]


class PredictionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    event = EventSerializer(read_only=True)

    class Meta:
        model = Prediction
        fields = [
            "id",
            "user",
            "event",
            "predicted_outcome",
            "status",
            "points_won",
            "created_at",
            "updated_at",
        ]


class CreatePredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = ["event", "predicted_outcome"]

    def validate(self, data):
        user = self.context["request"].user
        event = data["event"]

        if event.status != "active":
            raise serializers.ValidationError("Event is not active for predictions")

        if Prediction.objects.filter(user=user, event=event).exists():
            raise serializers.ValidationError("You have already predicted on this event")

        return data
