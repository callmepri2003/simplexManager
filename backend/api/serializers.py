from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from tutoring.models import Group
from rest_framework import serializers

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
