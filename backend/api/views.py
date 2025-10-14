import os
import re
import boto3
from django.http import StreamingHttpResponse
import requests

import urllib.parse
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework import status

from api.utils import collateAnalyticsAmountOfEnrolments, fetch_term, parse_term, validate_term_format
from tutoring.models import Attendance, Group, Lesson, LocalInvoice, Resource, TutoringTerm, TutoringStudent, TutoringWeek, TutoringYear
from .serializers import AttendanceSerializer, LessonSerializer, MyTokenObtainPairSerializer, GroupSerializer, ResourceSerializer, TutoringStudentSerializer
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q, Avg, Sum, Case, When, FloatField, F
from django.db.models.functions import TruncWeek, TruncMonth
from datetime import datetime, timedelta, timezone
from tutoring.models import TutoringStudent, Attendance, Lesson, LocalInvoice, Group
from collections import defaultdict



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

class editAttendance(APIView):
    def put(self, request, id):
        try:
            attendance = Attendance.objects.get(id=id)
        except Attendance.DoesNotExist:
            return Response(
                {"error": "Attendance record not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        sz = AttendanceSerializer(attendance, data=request.data)
        if sz.is_valid():
            sz.save()
            return Response(sz.data, status=status.HTTP_200_OK)
        
        return Response(sz.errors, status=status.HTTP_400_BAD_REQUEST)

class getAllAttendances(APIView):
    def get(self, request):
        attendances = Attendance.objects.all()
        sz = AttendanceSerializer(attendances, many=True)
        return Response(sz.data)
    
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

# Add to your views.py

class getFullInvoice(APIView):
    def get(self, request, stripe_invoice_id):
        try:
            local_invoice = LocalInvoice.objects.get(stripeInvoiceId=stripe_invoice_id)
            stripe_invoice = local_invoice.get_stripe_invoice()
            
            invoice_dict = stripe_invoice.to_dict()
            
            return Response(invoice_dict, status=status.HTTP_200_OK)
            
        except LocalInvoice.DoesNotExist:
            return Response(
                {"error": "Invoice not found in local database"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class getAllStudents(APIView):
    def get(self, request):
        students = TutoringStudent.objects.all()
        sz = TutoringStudentSerializer(students, many=True)
        return Response(sz.data)

class getStudentById(APIView):
    def get(self, request, id):
        try:
            student = TutoringStudent.objects.get(id=id)
            sz = TutoringStudentSerializer(student)
            return Response(sz.data)
        except TutoringStudent.DoesNotExist:
            return Response(
                {"error": "Student not found"},
                status=status.HTTP_404_NOT_FOUND
            )

class getAllLessons(APIView):
    def get(self, request):
        lessons = Lesson.objects.all()
        sz = LessonSerializer(lessons, many=True)
        return Response(sz.data)

class getLessonById(APIView):
    def get(self, request, id):
        try:
            lesson = Lesson.objects.get(id=id)
            sz = LessonSerializer(lesson)
            return Response(sz.data)
        except Lesson.DoesNotExist:
            return Response(
                {"error": "Lesson not found"},
                status=status.HTTP_404_NOT_FOUND
            )

class getBusinessAnalytics(APIView):
    def get(self, request):
        term_str = request.query_params.get('term')

        # Validate input format
        validate_term_format(term_str, "term")

        # Parse into dict
        term_dict = parse_term(term_str)

        # Fetch the term object
        term_obj = fetch_term(term_dict)

        # Compute analytics
        amount_of_enrolments = collateAnalyticsAmountOfEnrolments(term_obj)

        return Response({
            "amount_of_enrolments": amount_of_enrolments
        }, status=status.HTTP_200_OK)