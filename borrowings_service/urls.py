from django.urls import path, include
from rest_framework import routers

from borrowings_service.views import BorrowingsListRetrieveAPIView

router = routers.DefaultRouter()
router.register("", BorrowingsListRetrieveAPIView)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "borrowings_service"
