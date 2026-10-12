from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    EventViewSet,
    PredictionViewSet,
    UserScoreViewSet,
    LeaderboardViewSet,
    home,
    dashboard,
    leaderboard,
    event_detail,
    make_prediction,
)

router = DefaultRouter()
router.register(r"categories", CategoryViewSet)
router.register(r"events", EventViewSet)
router.register(r"predictions", PredictionViewSet, basename="prediction")
router.register(r"user-score", UserScoreViewSet, basename="user-score")
router.register(r"leaderboard", LeaderboardViewSet, basename="leaderboard")

urlpatterns = [
    path("api/", include(router.urls)),
    path("", home, name="home"),
    path("dashboard/", dashboard, name="dashboard"),
    path("leaderboard/", leaderboard, name="leaderboard"),
    path("event/<int:event_id>/", event_detail, name="event_detail"),
    path("make-prediction/", make_prediction, name="make_prediction"),
]
