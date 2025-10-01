import os
import boto3
from django.http import StreamingHttpResponse
import requests

import urllib.parse
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework import status

from tutoring.models import Group, Lesson, Resource
from .serializers import AttendanceSerializer, LessonSerializer, MyTokenObtainPairSerializer, GroupSerializer, ResourceSerializer
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError


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

class getEditDeleteLessons(APIView):

    def delete(self, request, pk):
        try:
            item = Lesson.objects.get(pk=pk)
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Lesson.DoesNotExist:
            return Response(
                {'error': 'Item not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
class addResource(APIView):
    def post(self, request):
        sz = ResourceSerializer(data=request.data)

        if sz.is_valid():
            try:

                sz.save()
                return Response(sz.data, status=status.HTTP_201_CREATED)

            except (IntegrityError, ValidationError) as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(sz.errors, status=status.HTTP_400_BAD_REQUEST)
