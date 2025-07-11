from django.contrib import admin
from django.urls import include, path
from .views import webhooks_view

urlpatterns = [
  path('webhooks/', webhooks_view, name='webhooks-view')
]
