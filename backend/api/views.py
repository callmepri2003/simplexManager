from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView

from tutoring.models import Group
from .serializers import AttendanceSerializer, MyTokenObtainPairSerializer, GroupSerializer

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
        return Response(sz.errors)