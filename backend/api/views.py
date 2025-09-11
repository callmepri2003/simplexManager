from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import LessonRollReadSerializer, LessonRollUpdateSerializer, MyTokenObtainPairSerializer
from rest_framework import viewsets
from tutoring.models import Group, Lesson, TutoringStudent, Attendance
from .serializers import GroupSerializer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction

class LessonRollViewSet(viewsets.ModelViewSet):
    """ViewSet for managing lesson rolls"""
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'roll':
            return LessonRollReadSerializer
        elif self.action == 'update_roll':
            return LessonRollUpdateSerializer
        return LessonRollReadSerializer
    
    @action(detail=True, methods=['get'], url_path='roll')
    def roll(self, request, pk=None):
        """
        Get roll data for a specific lesson
        GET /api/lessons/{lesson_id}/roll/
        """
        lesson = self.get_object()
        serializer = LessonRollReadSerializer(lesson)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post', 'put'], url_path='roll/update')
    def update_roll(self, request, pk=None):
        """
        Update roll data for a specific lesson
        POST/PUT /api/lessons/{lesson_id}/roll/
        """
        lesson = self.get_object()
        serializer = LessonRollUpdateSerializer(
            data=request.data, 
            context={'lesson': lesson}
        )

        print('***here1***')
        
        if serializer.is_valid():
            
            with transaction.atomic():
                
                # Update lesson notes if provided
                if 'notes' in serializer.validated_data:
                    lesson.notes = serializer.validated_data['notes']
                    lesson.save()
                
                # Process attendance data
                attendance_data = serializer.validated_data['attendances']
                
                for attendance_item in attendance_data:
                    student_id = attendance_item['tutoringStudent']
                    tutoringStudent = TutoringStudent.objects.get(id=student_id)
                    
                    # Update or create attendance record
                    attendance, created = Attendance.objects.update_or_create(
                        lesson=lesson,
                        tutoringStudent=tutoringStudent,
                        defaults={
                            'homework': attendance_item['homework'],
                            'paid': attendance_item['paid']
                        }
                    )
                
                # Return updated lesson data
                response_serializer = LessonRollReadSerializer(lesson)
                return Response(
                    response_serializer.data, 
                    status=status.HTTP_200_OK
                )
        print("=== SERIALIZER VALIDATION FAILED ===")
        print(f"Raw request data: {request.data}")
        print(f"Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'], url_path='roll/reset')
    def reset_roll(self, request, pk=None):
        """
        Reset all attendance records for a lesson
        DELETE /api/lessons/{lesson_id}/roll/reset/
        """
        lesson = self.get_object()
        deleted_count = lesson.attendances.all().delete()[0]
        
        return Response(
            {'message': f'Reset {deleted_count} attendance records for lesson {lesson.id}'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'], url_path='roll/summary')
    def roll_summary(self, request, pk=None):
        """
        Get attendance summary for a lesson
        GET /api/lessons/{lesson_id}/roll/summary/
        """
        lesson = self.get_object()
        attendances = lesson.attendances.all()
        
        total_students = lesson.group.tutoringStudents.count() if lesson.group else 0
        present_count = attendances.count()
        homework_completed = attendances.filter(homework=True).count()
        paid_count = attendances.filter(paid=True).count()
        
        summary = {
            'lesson_id': lesson.id,
            'total_students_in_group': total_students,
            'present_count': present_count,
            'absent_count': total_students - present_count,
            'homework_completed': homework_completed,
            'homework_not_completed': present_count - homework_completed,
            'paid_count': paid_count,
            'unpaid_count': present_count - paid_count,
            'attendance_rate': (present_count / total_students * 100) if total_students > 0 else 0
        }
        
        return Response(summary)

    @action(detail=False, methods=['get'], url_path='group/(?P<group_id>[^/.]+)')
    def lessons_by_group(self, request, group_id=None):
        """
        Get all lessons for a specific group
        GET /api/lessons/group/{group_id}/
        """
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response(
                {'error': f'Group with id {group_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        lessons = Lesson.objects.filter(group=group).order_by('-id')  # Most recent first
        serializer = LessonRollReadSerializer(lessons, many=True)
        
        return Response({
            'group_info': {
                'id': group.id,
                'course': group.course,
                'tutor': group.tutor,
                'day_of_week': group.get_day_of_week_display() if group.day_of_week else None,
                'time_of_day': group.time_of_day.strftime('%I:%M %p') if group.time_of_day else None
            },
            'lessons': serializer.data,
            'total_lessons': lessons.count()
        })

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer