from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import routers

from .views import ListOrCreateGroupView, MyTokenObtainPairView, getUpdateDeleteGroupView
from .views import bulkAddAttendances, addLessons, addResources

# Router
router = routers.DefaultRouter()

urlpatterns = [
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('groups/', ListOrCreateGroupView.as_view(), name='listOrCreateGroupView'),
    path('groups/<int:id>/', getUpdateDeleteGroupView.as_view(), name='getUpdateDeleteGroupView'),
    path('attendances/bulk/', bulkAddAttendances.as_view(), name='bulkAddAttendances'),
    path('lessons/', addLessons.as_view(), name='addLessons'),
    path('resources/bulk/', addResources.as_view(), name='addResources'),
    path('', include(router.urls)),
]