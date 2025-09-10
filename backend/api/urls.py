from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import routers

from .views import MyTokenObtainPairView, GroupViewSet, LessonRollViewSet
# Router
router = routers.DefaultRouter()

router.register(r'groups', GroupViewSet)
router.register(r'lessons', LessonRollViewSet, basename='lesson')

urlpatterns = [
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]
