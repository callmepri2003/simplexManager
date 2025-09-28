import os
import boto3
from django.http import StreamingHttpResponse
import requests

import urllib.parse
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework import status

from tutoring.models import Group, Resource
from .serializers import AttendanceSerializer, LessonSerializer, MyTokenObtainPairSerializer, GroupSerializer, ResourceSerializer


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class ListOrCreateGroupView(APIView):
    def get(self, request):
        groups = Group.objects.all()
        sz = GroupSerializer(groups, many=True)
        return Response(sz.data)

class getUpdateDeleteGroupView(APIView):
    def get(self, request, id):
        group = Group.objects.get(id=id)
        sz = GroupSerializer(group)
        return Response(sz.data)
    
class bulkAddAttendances(APIView):
    def post(self, request):
        sz = AttendanceSerializer(data=request.data, many=True)
        if sz.is_valid():
            sz.save()
            return Response(sz.data)
        return Response(sz.errors, status=status.HTTP_400_BAD_REQUEST)
    
class addLessons(APIView):
    def post(self, request):
        sz = LessonSerializer(data=request.data)
        if sz.is_valid():
            sz.save()
            return Response(sz.data)
        return Response(sz.errors, status=status.HTTP_400_BAD_REQUEST)

class addResources(APIView):
    def post(self, request):
        sz = ResourceSerializer(data=request.data)
        if sz.is_valid():
            print(sz)
            sz.save()
            return Response(sz.data)
        return Response(sz.errors, status=status.HTTP_400_BAD_REQUEST)