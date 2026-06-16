from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django import forms
from datetime import datetime, timezone as dt_timezone
from .models import *
import stripe
import os

class ResourceInline(admin.TabularInline):
    model = Resource
    extra = 1

class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 0
    fields = ['tutoringStudent', 'present', 'homework', 'paid', 'local_invoice']
    readonly_fields = ['local_invoice']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "local_invoice":
            # Show invoice details in the dropdown
            kwargs["queryset"] = LocalInvoice.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['lesson', 'tutoringStudent', 'present', 'homework', 'paid', 'get_invoice_info']
    fields = ['lesson', 'tutoringStudent', 'present', 'homework', 'paid', 'local_invoice', 'invoice_info']
    readonly_fields = ['invoice_info']
    
    def get_invoice_info(self, obj):
        if obj.local_invoice:
            return f"{obj.local_invoice.stripeInvoiceId} ({obj.local_invoice.status})"
        return "-"
    get_invoice_info.short_description = "Invoice"
    
    def invoice_info(self, obj):
        if obj.local_invoice:
            related_attendances = obj.local_invoice.attendances.count()
            return format_html(
                '<strong>Invoice ID:</strong> {}<br>'
                '<strong>Status:</strong> {}<br>'
                '<strong>Amount Paid:</strong> ${:.2f}<br>'
                '<strong>Currency:</strong> {}<br>'
                '<strong>Last Synced:</strong> {}<br>'
                '<strong>Related Attendances:</strong> {}<br>'
                '<em>To edit invoice details, go to <a href="/admin/tutoring/localinvoice/{}/change/">LocalInvoice admin</a></em>',
                obj.local_invoice.stripeInvoiceId,
                obj.local_invoice.status,
                obj.local_invoice.get_amount_in_dollars(),
                obj.local_invoice.currency.upper(),
                obj.local_invoice.last_synced,
                related_attendances,
                obj.local_invoice.pk
            )
        return "No invoice linked yet. Select an invoice above or create one in LocalInvoice admin."
    invoice_info.short_description = "Invoice Details"

@admin.register(LocalInvoice)
class LocalInvoiceAdmin(admin.ModelAdmin):
    list_display = ['stripeInvoiceId', 'status', 'get_amount_in_dollars', 'customer_stripe_id', 'get_attendance_count', 'last_synced']
    list_filter = ['status', 'currency']
    search_fields = ['stripeInvoiceId', 'customer_stripe_id']
    fields = ['stripeInvoiceId', 'sync_button_info', 'status', 'amount_due', 'amount_paid', 'currency', 
              'created', 'status_transitions_paid_at', 'customer_stripe_id', 'last_synced', 'related_attendances_info']
    readonly_fields = ['sync_button_info', 'status', 'amount_due', 'amount_paid', 'currency', 'created',
                       'status_transitions_paid_at', 'customer_stripe_id', 'last_synced', 'related_attendances_info']
    
    def get_attendance_count(self, obj):
        return obj.attendances.count()
    get_attendance_count.short_description = "# Attendances"
    
    def sync_button_info(self, obj):
        if obj.pk:
            return format_html(
                '<div style="background: #ffc; padding: 10px; border: 1px solid #ee9; border-radius: 4px;">'
                '<strong>💡 Tip:</strong> Change the Stripe Invoice ID above and save to sync from Stripe.<br>'
                'All fields below will be automatically updated from Stripe.'
                '</div>'
            )
        return "Save to sync from Stripe"
    sync_button_info.short_description = ""
    
    def related_attendances_info(self, obj):
        if obj.pk:
            attendances = obj.attendances.all()
            if attendances.exists():
                attendance_list = '<br>'.join([
                    f'• <a href="/admin/tutoring/attendance/{att.pk}/change/">{att.tutoringStudent.name} - {att.lesson}</a>'
                    for att in attendances[:10]  # Show first 10
                ])
                total = attendances.count()
                if total > 10:
                    attendance_list += f'<br>... and {total - 10} more'
                return format_html(
                    '<strong>This invoice is linked to {} attendance(s):</strong><br>{}',
                    total,
                    attendance_list
                )
            return "No attendances linked to this invoice yet."
        return "Save the invoice first to see related attendances."
    related_attendances_info.short_description = "Related Attendances"
    
    def save_model(self, request, obj, form, change):
        """Sync from Stripe when creating/updating stripeInvoiceId"""
        if 'stripeInvoiceId' in form.changed_data or not change:
            try:
                stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
                stripe_invoice = stripe.Invoice.retrieve(obj.stripeInvoiceId)
                
                obj.status = stripe_invoice.status
                obj.amount_due = stripe_invoice.amount_due
                obj.amount_paid = stripe_invoice.amount_paid
                obj.currency = stripe_invoice.currency
                obj.created = datetime.fromtimestamp(stripe_invoice.created, tz=dt_timezone.utc)
                obj.customer_stripe_id = stripe_invoice.customer
                
                if stripe_invoice.status_transitions and stripe_invoice.status_transitions.paid_at:
                    obj.status_transitions_paid_at = datetime.fromtimestamp(
                        stripe_invoice.status_transitions.paid_at,
                        tz=dt_timezone.utc
                    )
                else:
                    obj.status_transitions_paid_at = None
                
                obj.last_synced = timezone.now()
                
                from django.contrib import messages
                related_count = obj.attendances.count() if obj.pk else 0
                messages.success(
                    request, 
                    f"✓ Invoice {obj.stripeInvoiceId} synced successfully from Stripe! "
                    f"({related_count} related attendance(s) will now see updated data)"
                )
                
            except stripe.error.StripeError as e:
                from django.contrib import messages
                messages.error(request, f"✗ Failed to sync from Stripe: {str(e)}")
                # Don't save if sync failed
                return
        
        super().save_model(request, obj, form, change)

# Inline for Lessons inside TutoringWeek
class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    verbose_name = "Lesson"
    verbose_name_plural = "Lessons"


# Inline for TutoringWeek inside TutoringTerm
class TutoringWeekInline(admin.TabularInline):
    model = TutoringWeek
    extra = 1
    min_num = 1
    verbose_name = "Week"
    verbose_name_plural = "Weeks"
    show_change_link = True


# Inline for TutoringTerm inside TutoringYear
class TutoringTermInline(admin.StackedInline):
    model = TutoringTerm
    extra = 1
    min_num = 1
    verbose_name = "Term"
    verbose_name_plural = "Terms"
    show_change_link = True


# Admin for TutoringYear
@admin.register(TutoringYear)
class TutoringYearAdmin(admin.ModelAdmin):
    list_display = ("index",)
    inlines = [TutoringTermInline]


# Admin for TutoringTerm
@admin.register(TutoringTerm)
class TutoringTermAdmin(admin.ModelAdmin):
    list_display = ("index", "year", "previousTerm")
    inlines = [TutoringWeekInline]


# Admin for TutoringWeek
@admin.register(TutoringWeek)
class TutoringWeekAdmin(admin.ModelAdmin):
    list_display = ("index", "term")
    inlines = [LessonInline]


# Admin for Lesson
@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ["group", "notes", "date", "tutoringWeek", "get_term"]
    list_select_related = ["tutoringWeek__term"]
    search_fields = ["group__course", "notes"]

    def get_term(self, obj):
        return obj.tutoringWeek.term if obj.tutoringWeek else None
    get_term.short_description = "Term"

# Register other models normally
admin.site.register(Group)
admin.site.register(Parent)
admin.site.register(TutoringStudent)