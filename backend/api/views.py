import os
import boto3
from django.http import StreamingHttpResponse
import requests

import urllib.parse
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView

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
        return Response(sz.errors)
    
class addLessons(APIView):
    def post(self, request):
        sz = LessonSerializer(data=request.data)
        if sz.is_valid():
            sz.save()
            return Response(sz.data)
        return Response(sz.errors)

class addResources(APIView):
    def post(self, request):
        sz = ResourceSerializer(data=request.data)
        if sz.is_valid():
            print(sz)
            sz.save()
            return Response(sz.data)
        return Response(sz.errors)


class getFileUrl(APIView):
    def get(self, request, file_key):
        try:
            # If file_key is a full URL, extract just the S3 key part
            if file_key.startswith('https://'):
                # Parse the URL and extract the path (removing leading slash)
                parsed_url = urllib.parse.urlparse(file_key)
                actual_key = parsed_url.path.lstrip('/')
            else:
                actual_key = file_key
            
            s3_client = boto3.client(
                's3',
                aws_access_key_id=os.environ.get('BUCKETEER_AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('BUCKETEER_AWS_SECRET_ACCESS_KEY'),
                region_name=os.environ.get('BUCKETEER_AWS_REGION')
            )
            
            bucket_name = os.environ.get('BUCKETEER_BUCKET_NAME')
            
            url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': actual_key},
                ExpiresIn=3600
            )
            
            return Response({'url': url})
            
        except Exception as e:
            return Response({'error': str(e)}, status=500)