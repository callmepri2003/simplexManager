from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

from tutoring.models import Group

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

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'