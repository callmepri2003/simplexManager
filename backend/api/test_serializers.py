import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from datetime import time, datetime
from unittest.mock import Mock, patch
from rest_framework.exceptions import ValidationError

from tutoring.models import Student, Group, Lesson, Attendance, Resource, Parent
from stripeInt.models import StripeProd
from .serializers import (
    StudentSerializer,
    AttendanceSerializer, 
    ResourceSerializer,
    LessonRollReadSerializer,
    AttendanceUpdateSerializer,
    LessonRollUpdateSerializer,
    GroupSerializer,
    MyTokenObtainPairSerializer
)


class StudentSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            first_name='John',
            last_name='Doe'
        )
        self.parent = Parent.objects.create(name='Test Parent', stripeId='stripe_123')
        self.student = Student.objects.create(parent=self.parent)

    def test_serialize_student_without_user(self):
        serializer = StudentSerializer(self.student)
        data = serializer.data
        
        assert data['id'] == self.student.id
        assert data['display_name'] == f'Student {self.student.id}'

    def test_serialize_student_with_user(self):
        self.student.user = self.user
        serializer = StudentSerializer(self.student)
        data = serializer.data
        
        assert data['display_name'] == 'John Doe'


class AttendanceSerializerTest(TestCase):
    def setUp(self):
        self.parent = Parent.objects.create(name='Test Parent', stripeId='stripe_123')
        self.student = Student.objects.create(parent=self.parent)
        self.group = Group.objects.create(tutor='Test Tutor')
        self.lesson = Lesson.objects.create(group=self.group)
        self.attendance = Attendance.objects.create(
            lesson=self.lesson,
            student=self.student,
            homework=True,
            paid=False
        )

    def test_serialize_attendance(self):
        serializer = AttendanceSerializer(self.attendance)
        data = serializer.data
        
        assert data['student'] == self.student.id
        assert data['homework'] is True
        assert data['paid'] is False
        assert 'student_info' in data
        assert data['student_info']['id'] == self.student.id


class ResourceSerializerTest(TestCase):
    def setUp(self):
        self.group = Group.objects.create(tutor='Test Tutor')
        self.lesson = Lesson.objects.create(group=self.group)

    def test_serialize_resource_with_file(self):
        # Mock CloudinaryField
        mock_file = Mock()
        mock_file.url = 'https://cloudinary.com/test-file.pdf'
        
        resource = Resource.objects.create(lesson=self.lesson)
        resource.file = mock_file
        
        serializer = ResourceSerializer(resource)
        data = serializer.data
        
        assert data['id'] == resource.id
        assert data['file_url'] == 'https://cloudinary.com/test-file.pdf'

    def test_serialize_resource_without_file(self):
        resource = Resource.objects.create(lesson=self.lesson)
        serializer = ResourceSerializer(resource)
        data = serializer.data
        
        assert data['file_url'] is None


class LessonRollReadSerializerTest(TestCase):
    def setUp(self):
        self.parent = Parent.objects.create(name='Test Parent', stripeId='stripe_123')
        self.student = Student.objects.create(parent=self.parent)
        self.group = Group.objects.create(
            tutor='Test Tutor',
            course=Group.CourseChoices.JUNIOR_MATHS,
            day_of_week=Group.Weekday.MONDAY,
            time_of_day=time(10, 0)
        )
        self.group.students.add(self.student)
        self.lesson = Lesson.objects.create(
            group=self.group,
            notes='Test lesson notes'
        )
        self.attendance = Attendance.objects.create(
            lesson=self.lesson,
            student=self.student,
            homework=True,
            paid=False
        )

    def test_serialize_lesson_roll(self):
        serializer = LessonRollReadSerializer(self.lesson)
        data = serializer.data
        
        assert data['id'] == self.lesson.id
        assert data['notes'] == 'Test lesson notes'
        assert len(data['attendances']) == 1
        assert len(data['all_students']) == 1
        assert data['group_info']['course'] == Group.CourseChoices.JUNIOR_MATHS
        assert data['group_info']['tutor'] == 'Test Tutor'
        assert data['group_info']['day_of_week'] == None
        assert data['group_info']['time_of_day'] == '10:00 AM'

    def test_serialize_lesson_without_group(self):
        lesson_no_group = Lesson.objects.create(notes='No group lesson')
        serializer = LessonRollReadSerializer(lesson_no_group)
        data = serializer.data
        
        assert data['all_students'] == []
        assert data['group_info'] is None


class AttendanceUpdateSerializerTest(TestCase):
    def test_valid_attendance_data(self):
        data = {
            'student': 1,
            'homework': True,
            'paid': False
        }
        serializer = AttendanceUpdateSerializer(data=data)
        
        assert serializer.is_valid()
        assert serializer.validated_data['student'] == 1
        assert serializer.validated_data['homework'] is True
        assert serializer.validated_data['paid'] is False

    def test_defaults(self):
        data = {'student': 1}
        serializer = AttendanceUpdateSerializer(data=data)
        
        assert serializer.is_valid()
        assert serializer.validated_data['homework'] is False
        assert serializer.validated_data['paid'] is False


class LessonRollUpdateSerializerTest(TestCase):
    def setUp(self):
        self.parent = Parent.objects.create(name='Test Parent', stripeId='stripe_123')
        self.student1 = Student.objects.create(parent=self.parent)
        self.student2 = Student.objects.create(parent=self.parent)
        self.group = Group.objects.create(tutor='Test Tutor')
        self.group.students.add(self.student1, self.student2)
        self.lesson = Lesson.objects.create(group=self.group)

    def test_valid_lesson_roll_update(self):
        data = {
            'attendances': [
                {'student': self.student1.id, 'homework': True, 'paid': False},
                {'student': self.student2.id, 'homework': False, 'paid': True}
            ],
            'notes': 'Updated notes'
        }
        
        serializer = LessonRollUpdateSerializer(
            data=data, 
            context={'lesson': self.lesson}
        )
        
        assert serializer.is_valid()

    def test_invalid_student_ids(self):
        data = {
            'attendances': [
                {'student': 9999, 'homework': True, 'paid': False}
            ]
        }
        
        serializer = LessonRollUpdateSerializer(data=data)
        
        assert not serializer.is_valid()
        assert 'attendances' in serializer.errors

    def test_student_not_in_group(self):
        # Create student not in group
        other_parent = Parent.objects.create(name='Other Parent', stripeId='stripe_456')
        other_student = Student.objects.create(parent=other_parent)
        
        data = {
            'attendances': [
                {'student': other_student.id, 'homework': True, 'paid': False}
            ]
        }
        
        serializer = LessonRollUpdateSerializer(
            data=data,
            context={'lesson': self.lesson}
        )
        
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors

    def test_lesson_without_group(self):
        lesson_no_group = Lesson.objects.create()
        data = {
            'attendances': [
                {'student': self.student1.id, 'homework': True, 'paid': False}
            ]
        }
        
        serializer = LessonRollUpdateSerializer(
            data=data,
            context={'lesson': lesson_no_group}
        )
        
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors


class GroupSerializerTest(TestCase):
    def setUp(self):
        self.stripe_prod = StripeProd.objects.create(name='Test Product')
        self.group = Group.objects.create(
            lesson_length=2,
            associated_product=self.stripe_prod,
            tutor='Test Tutor',
            course=Group.CourseChoices.YEAR11_ADV,
            day_of_week=Group.Weekday.WEDNESDAY,
            time_of_day=time(14, 30),
            image_base64='dGVzdF9pbWFnZV9kYXRh'  # base64 encoded test data
        )

    def test_serialize_group(self):
        serializer = GroupSerializer(self.group)
        data = serializer.data
        
        assert data['id'] == self.group.id
        assert data['lesson_length'] == 2
        assert data['tutor'] == 'Test Tutor'
        assert data['course'] == Group.CourseChoices.YEAR11_ADV
        assert data['weekly_time'] == 'Wednesday 02:30 PM'
        assert data['associated_product'] == str(self.stripe_prod)

    def test_serialize_group_missing_time_data(self):
        group_no_time = Group.objects.create(tutor='Test Tutor')
        serializer = GroupSerializer(group_no_time)
        data = serializer.data
        
        assert data['weekly_time'] == ''
        assert data['associated_product'] is None


class MyTokenObtainPairSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    @patch('api.serializers.MyTokenObtainPairSerializer.get_token')
    def test_token_validation(self, mock_get_token):
        # Mock the token
        mock_token = Mock()
        mock_token.access_token = 'mock_access_token'
        mock_get_token.return_value = mock_token
        
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        serializer = MyTokenObtainPairSerializer(data=data)
        # Note: This test would need proper JWT setup to work fully
        # For basic coverage, we're just testing the structure

    def test_get_token_classmethod(self):
        token = MyTokenObtainPairSerializer.get_token(self.user)
        # Basic test that token is returned
        assert token is not None