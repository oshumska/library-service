from django.urls import path, include
from rest_framework import routers

from payment_service.views import PaymentViewSet, CreateStripeSessionView

router = routers.DefaultRouter()
router.register("payments", PaymentViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("session/", CreateStripeSessionView.as_view(), name="session-url"),
]


app_name = "payment-service"
