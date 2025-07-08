from django.contrib import admin
from .models import *

admin.site.register(Group)
admin.site.register(Lesson)
admin.site.register(Attendance)
admin.site.register(Parent)
admin.site.register(Student)
admin.site.register(Basket)
admin.site.register(BasketItem)