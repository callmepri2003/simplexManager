from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.db import transaction
from tutoring.models import Lesson, Attendance, Resource, Student, Group

class StudentSerializer(serializers.ModelSerializer):
    """Basic student serializer for displaying student info"""
    # Since your Student model doesn't have a name field, we'll use the ID
    # In a real implementation, you'd want to add a name field or link to User model
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = ['id', 'display_name']
    
    def get_display_name(self, obj):
        # This is a placeholder - you'd want to replace with actual name logic
        if hasattr(obj, 'user') and obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return f"Student {obj.id}"

class AttendanceSerializer(serializers.ModelSerializer):
    """Serializer for attendance records"""
    student_info = StudentSerializer(source='student', read_only=True)
    
    class Meta:
        model = Attendance
        fields = ['student', 'student_info', 'homework', 'paid']

class ResourceSerializer(serializers.ModelSerializer):
    """Serializer for lesson resources"""
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Resource
        fields = ["id", "file", "file_url"]
    
    def get_file_url(self, obj):
        if obj.file:
            return obj.file.url
        return None
        
class LessonRollReadSerializer(serializers.ModelSerializer):
    """Read-only serializer for getting lesson roll data"""
    attendances = AttendanceSerializer(many=True, read_only=True)
    all_students = serializers.SerializerMethodField()
    group_info = serializers.SerializerMethodField()
    resources = ResourceSerializer(many=True, read_only=True)  # 👈 nested resources

    class Meta:
        model = Lesson
        fields = ['id', 'notes', 'attendances', 'all_students', 'group_info', 'resources']

    def get_all_students(self, obj):
        """Get all students in the lesson's group"""
        if obj.group:
            return StudentSerializer(obj.group.students.all(), many=True).data
        return []

    def get_group_info(self, obj):
        """Get basic group information"""
        if obj.group:
            return {
                'id': obj.group.id,
                'course': obj.group.course,
                'tutor': obj.group.tutor,
                'day_of_week': obj.group.get_day_of_week_display() if obj.group.day_of_week else None,
                'time_of_day': obj.group.time_of_day.strftime('%I:%M %p') if obj.group.time_of_day else None
            }
        return None


class AttendanceUpdateSerializer(serializers.Serializer):
    """Serializer for updating attendance data"""
    student = serializers.IntegerField()
    homework = serializers.BooleanField(default=False)
    paid = serializers.BooleanField(default=False)

class LessonRollUpdateSerializer(serializers.Serializer):
    """Serializer for updating lesson roll"""
    attendances = AttendanceUpdateSerializer(many=True)
    notes = serializers.CharField(max_length=100, required=False, allow_blank=True)
    
    def validate_attendances(self, value):
        """Validate that all students exist"""
        student_ids = [attendance['student'] for attendance in value]
        existing_students = Student.objects.filter(id__in=student_ids)
        existing_student_ids = set(existing_students.values_list('id', flat=True))
        
        invalid_student_ids = set(student_ids) - existing_student_ids
        if invalid_student_ids:
            raise serializers.ValidationError(
                f"Invalid student IDs: {list(invalid_student_ids)}"
            )
        return value
    
    def validate(self, data):
        """Validate that students belong to the lesson's group"""
        lesson = self.context.get('lesson')
        if not lesson or not lesson.group:
            raise serializers.ValidationError("Lesson must have an associated group")
        
        student_ids = [attendance['student'] for attendance in data['attendances']]
        group_student_ids = set(lesson.group.students.values_list('id', flat=True))
        
        invalid_students = set(student_ids) - group_student_ids
        if invalid_students:
            raise serializers.ValidationError(
                f"Students {list(invalid_students)} are not in this lesson's group"
            )
        
        return data

class GroupSerializer(serializers.ModelSerializer):
    weekly_time = serializers.SerializerMethodField()
    associated_product = serializers.SerializerMethodField()  # override to show str()

    class Meta:
        model = Group
        fields = [
            "id",
            "lesson_length",
            "associated_product",
            "tutor",
            "course",
            "day_of_week",
            "time_of_day",
            "weekly_time",
            "image_base64",
            "image_upload",  # transient field for upload
        ]
        extra_kwargs = {
            "image_upload": {"write_only": True, "required": False},
        }

    def get_weekly_time(self, obj):
        try:
            return f"{obj.get_day_of_week_display()} {obj.time_of_day.strftime('%I:%M %p')}"
        except:
            return ""

    def get_associated_product(self, obj):
        return str(obj.associated_product) if obj.associated_product else None


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
