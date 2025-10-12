import base64
from django.urls import reverse
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

from stripeInt.models import StripeProd
from tutoring.models import Attendance, Group, Lesson, LocalInvoice, Parent, Resource, TutoringStudent

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

class LocalInvoiceSerializer(serializers.ModelSerializer):
    """
    Serializer for LocalInvoice that uses cached local data.
    Does not make Stripe API calls unless explicitly requested.
    """
    # Computed fields using local data
    is_paid = serializers.SerializerMethodField()
    amount_in_dollars = serializers.SerializerMethodField()
    amount_due_in_dollars = serializers.SerializerMethodField()
    
    # Related data
    customer_name = serializers.SerializerMethodField()
    
    # Human-readable dates
    created_formatted = serializers.SerializerMethodField()
    paid_at_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = LocalInvoice
        fields = [
            'id',
            'stripeInvoiceId',
            'status',
            'amount_due',
            'amount_paid',
            'amount_due_in_dollars',
            'amount_in_dollars',
            'currency',
            'created',
            'created_formatted',
            'status_transitions_paid_at',
            'paid_at_formatted',
            'customer_stripe_id',
            'customer_name',
            'last_synced',
            'is_paid',
            'attendances',
        ]
        read_only_fields = [
            'id',
            'stripeInvoiceId',
            'last_synced',
        ]
    
    def get_is_paid(self, obj):
        """Check if invoice is paid using local data"""
        return obj.is_paid()
    
    def get_amount_in_dollars(self, obj):
        """Convert amount_paid from cents to dollars"""
        return obj.get_amount_in_dollars()
    
    def get_amount_due_in_dollars(self, obj):
        """Convert amount_due from cents to dollars"""
        return obj.amount_due / 100
    
    def get_customer_name(self, obj):
        """Get customer name from Parent model"""
        try:
            parent = Parent.objects.get(stripeId=obj.customer_stripe_id)
            return parent.name
        except Parent.DoesNotExist:
            return None
    
    def get_created_formatted(self, obj):
        """Format created date as human-readable string"""
        if obj.created:
            return obj.created.strftime("%B %d, %Y at %I:%M %p")
        return None
    
    def get_paid_at_formatted(self, obj):
        """Format paid_at date as human-readable string"""
        if obj.status_transitions_paid_at:
            return obj.status_transitions_paid_at.strftime("%B %d, %Y at %I:%M %p")
        return None

class AttendanceSerializer(serializers.ModelSerializer):
    local_invoice = LocalInvoiceSerializer(read_only=True)
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