import base64
from django.urls import reverse
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

from stripeInt.models import StripeProd
from tutoring.models import Attendance, Group, Lesson, Resource, TutoringStudent

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # You can also add custom claims to the token here if needed
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Add custom response fields
        groups = []
        for group in self.user.groups.all():
            groups.append(str(group))
        data['roles'] = groups
        
        return data

class StripeProdSerializer(serializers.ModelSerializer):
    class Meta:
        model = StripeProd
        fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'

class ResourceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Resource
        fields = "__all__"


class LessonSerializer(serializers.ModelSerializer):
    attendances = AttendanceSerializer(many=True, read_only=True)
    resources = ResourceSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = '__all__'

class TutoringStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutoringStudent
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    associated_product = StripeProdSerializer()
    lessons = LessonSerializer(many=True, read_only=True)
    tutoringStudents = TutoringStudentSerializer(many=True, read_only=True)
    class Meta:
        model = Group
        fields = '__all__'