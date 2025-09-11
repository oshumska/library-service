from django.urls import path, include
from rest_framework import routers

from borrowings_service.views import BorrowingsAPIView

router = routers.DefaultRouter()
router.register("", BorrowingsAPIView)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "borrowings_service"
