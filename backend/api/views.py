import os
import boto3
from django.http import StreamingHttpResponse
import requests

import urllib.parse
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework import status

from tutoring.models import Attendance, Group, Lesson, LocalInvoice, Resource, TutoringStudent
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

class DashboardView(APIView):
    def get(self, request):
        # Get date range from query params or default to last 90 days
        end_date_str = request.query_params.get('end_date')
        start_date_str = request.query_params.get('start_date')
        
        if end_date_str and start_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            except ValueError:
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=90)
        
        # Calculate metrics
        metrics_data = self._get_metrics_data(start_date, end_date)
        attendance_data = self._get_attendance_trends(start_date, end_date)
        revenue_data = self._get_revenue_data()
        group_performance = self._get_group_performance(start_date, end_date)
        engagement_distribution = self._get_engagement_distribution(start_date, end_date)
        at_risk_students = self._get_at_risk_students(start_date, end_date)
        top_performers = self._get_top_performers(start_date, end_date)
        
        return Response({
            'dateRange': {
                'start': start_date.date().isoformat(),
                'end': end_date.date().isoformat()
            },
            'metricsData': metrics_data,
            'attendanceData': attendance_data,
            'revenueData': revenue_data,
            'groupPerformance': group_performance,
            'engagementDistribution': engagement_distribution,
            'atRiskStudents': at_risk_students,
            'topPerformers': top_performers
        })
    
    def _get_metrics_data(self, start_date, end_date):
        """Calculate key metrics with comparison to previous period"""
        period_length = (end_date - start_date).days
        prev_start = start_date - timedelta(days=period_length)
        prev_end = start_date
        
        # Total active students (current)
        current_students = TutoringStudent.objects.filter(
            active=True,
            start_date__lte=end_date
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=start_date)
        ).count()
        
        # Previous period students
        prev_students = TutoringStudent.objects.filter(
            active=True,
            start_date__lte=prev_end
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=prev_start)
        ).count()
        
        # Attendance rate (current period)
        current_attendance = Attendance.objects.filter(
            lesson__date__gte=start_date,
            lesson__date__lte=end_date
        ).aggregate(
            total=Count('id'),
            present=Count('id', filter=Q(present=True))
        )
        
        current_rate = (
            (current_attendance['present'] / current_attendance['total'] * 100)
            if current_attendance['total'] > 0 else 0
        )
        
        # Previous period attendance
        prev_attendance = Attendance.objects.filter(
            lesson__date__gte=prev_start,
            lesson__date__lt=prev_end
        ).aggregate(
            total=Count('id'),
            present=Count('id', filter=Q(present=True))
        )
        
        prev_rate = (
            (prev_attendance['present'] / prev_attendance['total'] * 100)
            if prev_attendance['total'] > 0 else 0
        )
        
        # Revenue (current period)
        current_revenue = LocalInvoice.objects.filter(
            status='paid',
            status_transitions_paid_at__gte=start_date,
            status_transitions_paid_at__lte=end_date
        ).aggregate(
            total=Sum('amount_paid')
        )['total'] or 0
        
        # Previous period revenue
        prev_revenue = LocalInvoice.objects.filter(
            status='paid',
            status_transitions_paid_at__gte=prev_start,
            status_transitions_paid_at__lt=prev_end
        ).aggregate(
            total=Sum('amount_paid')
        )['total'] or 0
        
        # Payment rate (% of invoices paid on time)
        current_invoices = LocalInvoice.objects.filter(
            created__gte=start_date,
            created__lte=end_date
        ).aggregate(
            total=Count('id'),
            paid=Count('id', filter=Q(status='paid'))
        )
        
        current_payment_rate = (
            (current_invoices['paid'] / current_invoices['total'] * 100)
            if current_invoices['total'] > 0 else 0
        )
        
        prev_invoices = LocalInvoice.objects.filter(
            created__gte=prev_start,
            created__lt=prev_end
        ).aggregate(
            total=Count('id'),
            paid=Count('id', filter=Q(status='paid'))
        )
        
        prev_payment_rate = (
            (prev_invoices['paid'] / prev_invoices['total'] * 100)
            if prev_invoices['total'] > 0 else 0
        )
        
        return {
            'totalStudents': {
                'value': current_students,
                'change': current_students - prev_students,
                'trend': 'up' if current_students >= prev_students else 'down'
            },
            'avgAttendance': {
                'value': round(current_rate, 1),
                'change': round(current_rate - prev_rate, 1),
                'trend': 'up' if current_rate >= prev_rate else 'down'
            },
            'termRevenue': {
                'value': current_revenue / 100,  # Convert cents to dollars
                'change': round(
                    ((current_revenue - prev_revenue) / prev_revenue * 100) 
                    if prev_revenue > 0 else 0, 
                    1
                ),
                'trend': 'up' if current_revenue >= prev_revenue else 'down'
            },
            'paymentRate': {
                'value': round(current_payment_rate, 1),
                'change': round(current_payment_rate - prev_payment_rate, 1),
                'trend': 'up' if current_payment_rate >= prev_payment_rate else 'down'
            }
        }
    
    def _get_attendance_trends(self, start_date, end_date):
        """Get weekly attendance rates"""
        # Get all attendances in the date range grouped by week
        attendances = Attendance.objects.filter(
            lesson__date__gte=start_date,
            lesson__date__lte=end_date
        ).annotate(
            week_start=TruncWeek('lesson__date')
        ).values('week_start').annotate(
            total=Count('id'),
            present=Count('id', filter=Q(present=True))
        ).order_by('week_start')
        
        # Format for frontend
        result = []
        for i, attendance in enumerate(attendances, 1):
            rate = (attendance['present'] / attendance['total'] * 100) if attendance['total'] > 0 else 0
            result.append({
                'week': f'Week {i}',
                'rate': round(rate, 1)
            })
        
        return result
    
    def _get_revenue_data(self):
        """Get last 6 months of revenue"""
        six_months_ago = datetime.now(timezone.utc) - timedelta(days=180)
        
        revenue_by_month = LocalInvoice.objects.filter(
            status='paid',
            status_transitions_paid_at__gte=six_months_ago
        ).annotate(
            month=TruncMonth('status_transitions_paid_at')
        ).values('month').annotate(
            revenue=Sum('amount_paid')
        ).order_by('month')
        
        result = []
        for item in revenue_by_month:
            result.append({
                'month': item['month'].strftime('%b'),
                'revenue': item['revenue'] / 100  # Convert cents to dollars
            })
        
        return result
    
    def _get_group_performance(self, start_date, end_date):
        """Calculate performance metrics for each group"""
        groups = Group.objects.all()
        result = []
        
        for group in groups:
            # Get all attendances for this group in the date range
            attendances = Attendance.objects.filter(
                lesson__group=group,
                lesson__date__gte=start_date,
                lesson__date__lte=end_date
            )
            
            total_attendances = attendances.count()
            if total_attendances == 0:
                continue
            
            present_count = attendances.filter(present=True).count()
            homework_count = attendances.filter(homework=True).count()
            
            # Get students in this group
            students = group.tutoringStudents.filter(active=True)
            
            # Calculate payment rate for students in this group
            invoices = LocalInvoice.objects.filter(
                attendances__lesson__group=group,
                attendances__lesson__date__gte=start_date,
                attendances__lesson__date__lte=end_date
            ).distinct()
            
            total_invoices = invoices.count()
            paid_invoices = invoices.filter(status='paid').count()
            
            attendance_rate = round((present_count / total_attendances * 100), 1) if total_attendances > 0 else 0
            homework_rate = round((homework_count / total_attendances * 100), 1) if total_attendances > 0 else 0
            payment_rate = round((paid_invoices / total_invoices * 100), 1) if total_invoices > 0 else 0
            
            result.append({
                'name': str(group.course) if group.course else f"Group {group.id}",
                'attendance': attendance_rate,
                'payment': payment_rate,
                'homework': homework_rate
            })
        
        return result
    
    def _get_engagement_distribution(self, start_date, end_date):
        """Calculate student engagement distribution"""
        students = TutoringStudent.objects.filter(active=True)
        
        distribution = {
            'high': 0,      # >90%
            'medium': 0,    # 70-90%
            'low': 0,       # 50-70%
            'at_risk': 0    # <50%
        }
        
        for student in students:
            attendances = Attendance.objects.filter(
                tutoringStudent=student,
                lesson__date__gte=start_date,
                lesson__date__lte=end_date
            )
            
            total = attendances.count()
            if total == 0:
                continue
            
            present = attendances.filter(present=True).count()
            rate = (present / total * 100)
            
            if rate > 90:
                distribution['high'] += 1
            elif rate >= 70:
                distribution['medium'] += 1
            elif rate >= 50:
                distribution['low'] += 1
            else:
                distribution['at_risk'] += 1
        
        return [
            {'name': 'High (>90%)', 'value': distribution['high'], 'color': '#004aad'},
            {'name': 'Medium (70-90%)', 'value': distribution['medium'], 'color': '#17a2b8'},
            {'name': 'Low (50-70%)', 'value': distribution['low'], 'color': '#ffc107'},
            {'name': 'At Risk (<50%)', 'value': distribution['at_risk'], 'color': '#dc3545'},
        ]
    
    def _get_at_risk_students(self, start_date, end_date):
        """Identify students at risk based on attendance and payment"""
        students = TutoringStudent.objects.filter(active=True)
        at_risk = []
        
        for student in students:
            attendances = Attendance.objects.filter(
                tutoringStudent=student,
                lesson__date__gte=start_date,
                lesson__date__lte=end_date
            )
            
            total = attendances.count()
            if total == 0:
                continue
            
            present = attendances.filter(present=True).count()
            attendance_rate = (present / total * 100)
            
            # Get payment rate for this student
            invoices = LocalInvoice.objects.filter(
                attendances__tutoringStudent=student,
                created__gte=start_date,
                created__lte=end_date
            ).distinct()
            
            total_invoices = invoices.count()
            paid_invoices = invoices.filter(status='paid').count()
            payment_rate = (paid_invoices / total_invoices * 100) if total_invoices > 0 else 100
            
            # Get last absence
            last_absence = attendances.filter(present=False).order_by('-lesson__date').first()
            
            # Mark as at-risk if attendance < 75% or payment < 80%
            if attendance_rate < 75 or payment_rate < 80:
                days_since_absence = 'N/A'
                if last_absence:
                    days = (datetime.now(timezone.utc) - last_absence.lesson.date).days
                    if days == 0:
                        days_since_absence = 'today'
                    elif days == 1:
                        days_since_absence = '1 day ago'
                    elif days < 7:
                        days_since_absence = f'{days} days ago'
                    elif days < 14:
                        days_since_absence = '1 week ago'
                    else:
                        weeks = days // 7
                        days_since_absence = f'{weeks} weeks ago'
                
                at_risk.append({
                    'id': student.id,
                    'name': student.name,
                    'attendance': round(attendance_rate, 1),
                    'payment': round(payment_rate, 1),
                    'lastAbsence': days_since_absence
                })
        
        # Sort by attendance rate (lowest first)
        at_risk.sort(key=lambda x: x['attendance'])
        
        return at_risk[:10]  # Return top 10 at-risk students
    
    def _get_top_performers(self, start_date, end_date):
        """Identify top performing students based on engagement"""
        students = TutoringStudent.objects.filter(active=True)
        performers = []
        
        for student in students:
            attendances = Attendance.objects.filter(
                tutoringStudent=student,
                lesson__date__gte=start_date,
                lesson__date__lte=end_date
            ).order_by('lesson__date')
            
            total = attendances.count()
            if total == 0:
                continue
            
            present = attendances.filter(present=True).count()
            homework = attendances.filter(homework=True).count()
            
            # Calculate engagement score (weighted average)
            attendance_rate = (present / total * 100)
            homework_rate = (homework / total * 100)
            engagement_score = (attendance_rate * 0.6 + homework_rate * 0.4)
            
            # Calculate current streak
            streak = 0
            for attendance in attendances.reverse():
                if attendance.present and attendance.homework:
                    streak += 1
                else:
                    break
            
            if engagement_score >= 85:  # Only include high performers
                performers.append({
                    'id': student.id,
                    'name': student.name,
                    'engagement': round(engagement_score, 1),
                    'streak': streak
                })
        
        # Sort by engagement score (highest first)
        performers.sort(key=lambda x: x['engagement'], reverse=True)
        
        return performers[:10]  # Return top 10 performers