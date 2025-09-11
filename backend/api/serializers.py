from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

from stripeInt.models import StripeProd
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

class StripeProdSerializer(serializers.ModelSerializer):
    class Meta:
        model = StripeProd
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    # attendances = AttendanceSerializer(many=True)
    associated_product = StripeProdSerializer()
    class Meta:
        model = Group
        fields = '__all__'