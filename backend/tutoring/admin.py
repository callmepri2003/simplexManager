from django.contrib import admin
from .models import *

class BasketItemInline(admin.TabularInline):
    model = BasketItem
    extra = 1
    fields = ['product', 'quantity']

class BasketAdmin(admin.ModelAdmin):
    inlines = [BasketItemInline]
    list_display = ['id', 'get_parent_name', 'get_total_items']
    
    def get_parent_name(self, obj):
        try:
            return obj.parent.name
        except:
            return "No parent assigned"
    get_parent_name.short_description = "Parent"
    
    def get_total_items(self, obj):
        return obj.items.count()
    get_total_items.short_description = "Total Items"


class ResourceInline(admin.TabularInline):
    model = Resource
    extra = 1  # show one empty row for quick add

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ["group", "notes"]
    inlines = [ResourceInline]


admin.site.register(Basket, BasketAdmin)

# Register other models normally
admin.site.register(Group)
admin.site.register(Attendance)
admin.site.register(Parent)
admin.site.register(Student)
admin.site.register(BasketItem)