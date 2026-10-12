from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.db.models import Q, F
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.http import JsonResponse
from .models import UserProfile, Category, Event, Prediction
from .serializers import (
    CategorySerializer,
    EventSerializer,
    PredictionSerializer,
    CreatePredictionSerializer,
    UserSerializer,
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.select_related("category").prefetch_related("entities")
    serializer_class = EventSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get("category")
        status_filter = self.request.query_params.get("status")

        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    @action(detail=False, methods=["get"])
    def active(self, request):
        active_events = self.get_queryset().filter(status="active")
        serializer = self.get_serializer(active_events, many=True)
        return Response(serializer.data)


class PredictionViewSet(viewsets.ModelViewSet):
    serializer_class = PredictionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Prediction.objects.filter(user=self.request.user).select_related("event", "user")

    def get_serializer_class(self):
        if self.action == "create":
            return CreatePredictionSerializer
        return PredictionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"])
    def my_predictions(self, request):
        predictions = self.get_queryset()
        serializer = self.get_serializer(predictions, many=True)
        return Response(serializer.data)


class UserScoreViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)


class LeaderboardViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        top_users = UserProfile.objects.order_by("-score")[:10]
        leaderboard_data = []
        for profile in top_users:
            leaderboard_data.append(
                {
                    "username": profile.user.username,
                    "score": profile.score,
                    "total_predictions": profile.total_predictions,
                    "correct_predictions": profile.correct_predictions,
                    "win_rate": profile.win_rate,
                }
            )
        return Response(leaderboard_data)


# Template Views
def home(request):
    category_id = request.GET.get("category")
    events = Event.objects.filter(status="active").select_related("category").prefetch_related("entities")
    if category_id:
        events = events.filter(category_id=category_id)
    categories = Category.objects.all()
    return render(request, "home.html", {"events": events, "categories": categories})


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("/accounts/login/")
    predictions = Prediction.objects.filter(user=request.user).select_related("event").order_by("-created_at")
    return render(request, "dashboard.html", {"predictions": predictions})


def leaderboard(request):
    profiles = UserProfile.objects.order_by("-score")[:10]
    leaderboard_data = []
    for profile in profiles:
        leaderboard_data.append(
            {
                "username": profile.user.username,
                "score": profile.score,
                "total_predictions": profile.total_predictions,
                "correct_predictions": profile.correct_predictions,
                "win_rate": profile.win_rate,
            }
        )
    return render(request, "leaderboard.html", {"leaderboard": leaderboard_data})


def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, "event_detail.html", {"event": event})


@csrf_exempt
def make_prediction(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)
    
    if request.method == "POST":
        event_id = request.POST.get("event_id")
        predicted_outcome = request.POST.get("predicted_outcome")
        
        try:
            event = Event.objects.get(id=event_id)
            if event.status != "active":
                return JsonResponse({"error": "Event is not active"}, status=400)
            
            if Prediction.objects.filter(user=request.user, event=event).exists():
                return JsonResponse({"error": "You have already predicted on this event"}, status=400)
            
            prediction = Prediction.objects.create(
                user=request.user,
                event=event,
                predicted_outcome={"result": predicted_outcome}
            )
            
            return JsonResponse({"success": True, "prediction_id": prediction.id})
        except Event.DoesNotExist:
            return JsonResponse({"error": "Event not found"}, status=404)
    
    return JsonResponse({"error": "Invalid request"}, status=400)
