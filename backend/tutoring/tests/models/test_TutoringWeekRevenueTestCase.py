from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from tutoring.models import (
    TutoringWeek, TutoringTerm, TutoringYear, 
    Group, Lesson, Attendance, TutoringStudent, 
    Parent, LocalInvoice
)
from stripeInt.models import StripeProd


class TutoringWeekRevenueTestCase(TestCase):
    
    def setUp(self):
        """Set up test data"""
        # Create tutoring year and term
        self.year = TutoringYear.objects.create(index=2025)
        self.term = TutoringTerm.objects.create(index=1, year=self.year)
        self.week1 = TutoringWeek.objects.create(index=1, term=self.term)
        self.week2 = TutoringWeek.objects.create(index=2, term=self.term)
        
        # Create a product
        self.product = StripeProd.objects.create(
            stripeId='prod_test123',
            name='Test Product',
            defaultPriceId='price_test123'
        )
        
        # Create a group
        self.group = Group.objects.create(
            lesson_length=90,
            tutor='Test Tutor',
            course='12 Advanced',
            day_of_week=0,
            associated_product=self.product
        )
        
        # Create parent and students
        self.parent = Parent.objects.create(
            name='Test Parent',
            stripeId='cus_test123'
        )
        
        self.student1 = TutoringStudent.objects.create(
            name='Student 1',
            parent=self.parent,
            active=True
        )
        self.student1.group.add(self.group)
        
        self.student2 = TutoringStudent.objects.create(
            name='Student 2',
            parent=self.parent,
            active=True
        )
        self.student2.group.add(self.group)
    
    def test_revenue_with_no_lessons(self):
        """Test that revenue is zero when there are no lessons"""
        revenue = self.week1.get_revenue()
        self.assertEqual(revenue, Decimal('0.00'))
    
    def test_revenue_with_unpaid_invoices(self):
        """Test that unpaid invoices don't contribute to revenue"""
        # Create lesson
        lesson = Lesson.objects.create(
            group=self.group,
            date=timezone.now(),
            tutoringWeek=self.week1
        )
        
        # Create unpaid invoice
        invoice = LocalInvoice.objects.create(
            stripeInvoiceId='inv_unpaid123',
            status='open',
            amount_due=5000,  # $50
            amount_paid=0,
            created=timezone.now()
        )
        
        # Create attendance with unpaid invoice
        attendance = Attendance.objects.create(
            lesson=lesson,
            tutoringStudent=self.student1,
            present=True,
            paid=False,
            local_invoice=invoice
        )
        
        revenue = self.week1.get_revenue()
        self.assertEqual(revenue, Decimal('0.00'))
    
    def test_revenue_with_single_paid_invoice(self):
        """Test revenue calculation with one paid invoice"""
        # Create lesson
        lesson = Lesson.objects.create(
            group=self.group,
            date=timezone.now(),
            tutoringWeek=self.week1
        )
        
        # Create paid invoice
        invoice = LocalInvoice.objects.create(
            stripeInvoiceId='inv_paid123',
            status='paid',
            amount_due=5000,  # $50
            amount_paid=5000,
            created=timezone.now(),
            status_transitions_paid_at=timezone.now()
        )
        
        # Create attendance with paid invoice
        attendance = Attendance.objects.create(
            lesson=lesson,
            tutoringStudent=self.student1,
            present=True,
            paid=True,
            local_invoice=invoice
        )
        
        revenue = self.week1.get_revenue()
        self.assertEqual(revenue, Decimal('50.00'))
    
    def test_revenue_with_multiple_paid_invoices(self):
        """Test revenue calculation with multiple paid invoices"""
        # Create two lessons
        lesson1 = Lesson.objects.create(
            group=self.group,
            date=timezone.now(),
            tutoringWeek=self.week1
        )
        
        lesson2 = Lesson.objects.create(
            group=self.group,
            date=timezone.now() + timedelta(days=1),
            tutoringWeek=self.week1
        )
        
        # Create paid invoices
        invoice1 = LocalInvoice.objects.create(
            stripeInvoiceId='inv_paid1',
            status='paid',
            amount_due=5000,
            amount_paid=5000,
            created=timezone.now(),
            status_transitions_paid_at=timezone.now()
        )
        
        invoice2 = LocalInvoice.objects.create(
            stripeInvoiceId='inv_paid2',
            status='paid',
            amount_due=7500,
            amount_paid=7500,
            created=timezone.now(),
            status_transitions_paid_at=timezone.now()
        )
        
        # Create attendances
        Attendance.objects.create(
            lesson=lesson1,
            tutoringStudent=self.student1,
            present=True,
            paid=True,
            local_invoice=invoice1
        )
        
        Attendance.objects.create(
            lesson=lesson2,
            tutoringStudent=self.student2,
            present=True,
            paid=True,
            local_invoice=invoice2
        )
        
        revenue = self.week1.get_revenue()
        self.assertEqual(revenue, Decimal('125.00'))
    
    def test_revenue_with_mixed_paid_and_unpaid_invoices(self):
        """Test that only paid invoices contribute to revenue"""
        lesson = Lesson.objects.create(
            group=self.group,
            date=timezone.now(),
            tutoringWeek=self.week1
        )
        
        # Paid invoice
        paid_invoice = LocalInvoice.objects.create(
            stripeInvoiceId='inv_paid',
            status='paid',
            amount_due=5000,
            amount_paid=5000,
            created=timezone.now(),
            status_transitions_paid_at=timezone.now()
        )
        
        # Unpaid invoice
        unpaid_invoice = LocalInvoice.objects.create(
            stripeInvoiceId='inv_unpaid',
            status='open',
            amount_due=3000,
            amount_paid=0,
            created=timezone.now()
        )
        
        Attendance.objects.create(
            lesson=lesson,
            tutoringStudent=self.student1,
            present=True,
            paid=True,
            local_invoice=paid_invoice
        )
        
        Attendance.objects.create(
            lesson=lesson,
            tutoringStudent=self.student2,
            present=True,
            paid=False,
            local_invoice=unpaid_invoice
        )
        
        revenue = self.week1.get_revenue()
        self.assertEqual(revenue, Decimal('50.00'))
    
    def test_revenue_with_attendance_without_invoice(self):
        """Test that attendances without invoices don't break the calculation"""
        lesson = Lesson.objects.create(
            group=self.group,
            date=timezone.now(),
            tutoringWeek=self.week1
        )
        
        # Attendance without invoice
        Attendance.objects.create(
            lesson=lesson,
            tutoringStudent=self.student1,
            present=True,
            paid=False,
            local_invoice=None
        )
        
        revenue = self.week1.get_revenue()
        self.assertEqual(revenue, Decimal('0.00'))
    
    def test_revenue_isolation_between_weeks(self):
        """Test that revenue is calculated per week correctly"""
        # Create lessons in different weeks
        lesson_week1 = Lesson.objects.create(
            group=self.group,
            date=timezone.now(),
            tutoringWeek=self.week1
        )
        
        lesson_week2 = Lesson.objects.create(
            group=self.group,
            date=timezone.now() + timedelta(days=7),
            tutoringWeek=self.week2
        )
        
        # Create paid invoices
        invoice1 = LocalInvoice.objects.create(
            stripeInvoiceId='inv_week1',
            status='paid',
            amount_due=5000,
            amount_paid=5000,
            created=timezone.now(),
            status_transitions_paid_at=timezone.now()
        )
        
        invoice2 = LocalInvoice.objects.create(
            stripeInvoiceId='inv_week2',
            status='paid',
            amount_due=7500,
            amount_paid=7500,
            created=timezone.now(),
            status_transitions_paid_at=timezone.now()
        )
        
        Attendance.objects.create(
            lesson=lesson_week1,
            tutoringStudent=self.student1,
            present=True,
            paid=True,
            local_invoice=invoice1
        )
        
        Attendance.objects.create(
            lesson=lesson_week2,
            tutoringStudent=self.student2,
            present=True,
            paid=True,
            local_invoice=invoice2
        )
        
        # Check each week's revenue separately
        revenue_week1 = self.week1.get_revenue()
        revenue_week2 = self.week2.get_revenue()
        
        self.assertEqual(revenue_week1, Decimal('50.00'))
        self.assertEqual(revenue_week2, Decimal('75.00'))
    
    def test_revenue_with_partial_payment(self):
        """Test revenue when amount_paid differs from amount_due"""
        lesson = Lesson.objects.create(
            group=self.group,
            date=timezone.now(),
            tutoringWeek=self.week1
        )
        
        # Invoice with partial payment
        invoice = LocalInvoice.objects.create(
            stripeInvoiceId='inv_partial',
            status='paid',
            amount_due=10000,
            amount_paid=7500,  # Only 75% paid
            created=timezone.now(),
            status_transitions_paid_at=timezone.now()
        )
        
        Attendance.objects.create(
            lesson=lesson,
            tutoringStudent=self.student1,
            present=True,
            paid=True,
            local_invoice=invoice
        )
        
        revenue = self.week1.get_revenue()
        self.assertEqual(revenue, Decimal('75.00'))
    
    def test_revenue_with_voided_invoice(self):
        """Test that voided invoices don't contribute to revenue"""
        lesson = Lesson.objects.create(
            group=self.group,
            date=timezone.now(),
            tutoringWeek=self.week1
        )
        
        invoice = LocalInvoice.objects.create(
            stripeInvoiceId='inv_void',
            status='void',
            amount_due=5000,
            amount_paid=0,
            created=timezone.now()
        )
        
        Attendance.objects.create(
            lesson=lesson,
            tutoringStudent=self.student1,
            present=True,
            paid=False,
            local_invoice=invoice
        )
        
        revenue = self.week1.get_revenue()
        self.assertEqual(revenue, Decimal('0.00'))