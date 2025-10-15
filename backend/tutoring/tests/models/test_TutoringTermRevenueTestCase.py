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


class TutoringTermRevenueTestCase(TestCase):
    
    def setUp(self):
        """Set up test data"""
        # Create tutoring year and term
        self.year = TutoringYear.objects.create(index=2025)
        # Note: Creating term will auto-create 10 weeks
        self.term1 = TutoringTerm.objects.create(index=1, year=self.year)
        
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
    
    def test_term_creates_10_weeks_by_default(self):
        """Test that creating a term automatically creates 10 weeks"""
        new_term = TutoringTerm.objects.create(index=2, year=self.year)
        weeks = new_term.weeks.all()
        
        self.assertEqual(weeks.count(), 10)
        
        # Verify week indices are 1-10
        week_indices = sorted([week.index for week in weeks])
        self.assertEqual(week_indices, list(range(1, 11)))
    
    def test_term_revenue_with_no_paid_invoices(self):
        """Test that term revenue is zero when no invoices are paid"""
        revenue = self.term1.get_revenue()
        self.assertEqual(revenue, Decimal('0.00'))
    
    def test_term_revenue_with_single_week_revenue(self):
        """Test term revenue calculation with revenue in one week"""
        week1 = self.term1.weeks.get(index=1)
        
        # Create lesson in week 1
        lesson = Lesson.objects.create(
            group=self.group,
            date=timezone.now(),
            tutoringWeek=week1
        )
        
        # Create paid invoice
        invoice = LocalInvoice.objects.create(
            stripeInvoiceId='inv_paid123',
            status='paid',
            amount_due=5000,
            amount_paid=5000,
            created=timezone.now(),
            status_transitions_paid_at=timezone.now()
        )
        
        # Create attendance with paid invoice
        Attendance.objects.create(
            lesson=lesson,
            tutoringStudent=self.student1,
            present=True,
            paid=True,
            local_invoice=invoice
        )
        
        revenue = self.term1.get_revenue()
        self.assertEqual(revenue, Decimal('50.00'))
    
    def test_term_revenue_with_multiple_weeks(self):
        """Test term revenue aggregates across multiple weeks"""
        week1 = self.term1.weeks.get(index=1)
        week2 = self.term1.weeks.get(index=2)
        week3 = self.term1.weeks.get(index=3)
        
        # Create lessons in different weeks
        lesson1 = Lesson.objects.create(
            group=self.group,
            date=timezone.now(),
            tutoringWeek=week1
        )
        
        lesson2 = Lesson.objects.create(
            group=self.group,
            date=timezone.now() + timedelta(days=7),
            tutoringWeek=week2
        )
        
        lesson3 = Lesson.objects.create(
            group=self.group,
            date=timezone.now() + timedelta(days=14),
            tutoringWeek=week3
        )
        
        # Create paid invoices for each week
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
        
        invoice3 = LocalInvoice.objects.create(
            stripeInvoiceId='inv_week3',
            status='paid',
            amount_due=10000,
            amount_paid=10000,
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
            tutoringStudent=self.student1,
            present=True,
            paid=True,
            local_invoice=invoice2
        )
        
        Attendance.objects.create(
            lesson=lesson3,
            tutoringStudent=self.student2,
            present=True,
            paid=True,
            local_invoice=invoice3
        )
        
        revenue = self.term1.get_revenue()
        self.assertEqual(revenue, Decimal('225.00'))
    
    def test_term_revenue_excludes_unpaid_invoices(self):
        """Test that term revenue only counts paid invoices"""
        week1 = self.term1.weeks.get(index=1)
        week2 = self.term1.weeks.get(index=2)
        
        lesson1 = Lesson.objects.create(
            group=self.group,
            date=timezone.now(),
            tutoringWeek=week1
        )
        
        lesson2 = Lesson.objects.create(
            group=self.group,
            date=timezone.now() + timedelta(days=7),
            tutoringWeek=week2
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
            amount_due=10000,
            amount_paid=0,
            created=timezone.now()
        )
        
        Attendance.objects.create(
            lesson=lesson1,
            tutoringStudent=self.student1,
            present=True,
            paid=True,
            local_invoice=paid_invoice
        )
        
        Attendance.objects.create(
            lesson=lesson2,
            tutoringStudent=self.student2,
            present=True,
            paid=False,
            local_invoice=unpaid_invoice
        )
        
        revenue = self.term1.get_revenue()
        self.assertEqual(revenue, Decimal('50.00'))
    
    def test_term_revenue_with_all_10_weeks(self):
        """Test term revenue when all 10 weeks have revenue"""
        invoices = []
        
        # Create paid invoices for all 10 weeks
        for i in range(1, 11):
            week = self.term1.weeks.get(index=i)
            
            lesson = Lesson.objects.create(
                group=self.group,
                date=timezone.now() + timedelta(days=7 * (i - 1)),
                tutoringWeek=week
            )
            
            invoice = LocalInvoice.objects.create(
                stripeInvoiceId=f'inv_week{i}',
                status='paid',
                amount_due=5000,
                amount_paid=5000,
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
        
        revenue = self.term1.get_revenue()
        # 10 weeks * $50 per week = $500
        self.assertEqual(revenue, Decimal('500.00'))
    
    def test_term_revenue_with_custom_number_of_weeks(self):
        """Test term revenue with more or fewer than 10 weeks"""
        # Create a new term and manually add extra weeks
        term2 = TutoringTerm.objects.create(index=2, year=self.year)
        
        # Add 2 more weeks (term2 already has 10 from auto-creation)
        TutoringWeek.objects.create(index=11, term=term2)
        TutoringWeek.objects.create(index=12, term=term2)
        
        # Add revenue to week 11 and 12
        for week_index in [11, 12]:
            week = term2.weeks.get(index=week_index)
            
            lesson = Lesson.objects.create(
                group=self.group,
                date=timezone.now(),
                tutoringWeek=week
            )
            
            invoice = LocalInvoice.objects.create(
                stripeInvoiceId=f'inv_week{week_index}',
                status='paid',
                amount_due=7500,
                amount_paid=7500,
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
        
        revenue = term2.get_revenue()
        # 2 weeks * $75 per week = $150
        self.assertEqual(revenue, Decimal('150.00'))
    
    def test_term_with_fewer_than_10_weeks(self):
        """Test that we can manually create a term with fewer weeks"""
        # Create term without triggering save signal for this test
        term3 = TutoringTerm(index=3, year=self.year)
        term3.save()  # This will auto-create 10 weeks
        
        # Delete some weeks to simulate a shorter term
        term3.weeks.filter(index__gt=6).delete()
        
        # Verify only 6 weeks remain
        self.assertEqual(term3.weeks.count(), 6)
        
        # Add revenue to remaining weeks
        for i in range(1, 7):
            week = term3.weeks.get(index=i)
            
            lesson = Lesson.objects.create(
                group=self.group,
                date=timezone.now(),
                tutoringWeek=week
            )
            
            invoice = LocalInvoice.objects.create(
                stripeInvoiceId=f'inv_term3_week{i}',
                status='paid',
                amount_due=5000,
                amount_paid=5000,
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
        
        revenue = term3.get_revenue()
        # 6 weeks * $50 = $300
        self.assertEqual(revenue, Decimal('300.00'))
    
    def test_term_revenue_isolation(self):
        """Test that each term's revenue is calculated independently"""
        term2 = TutoringTerm.objects.create(index=2, year=self.year)
        
        week1_term1 = self.term1.weeks.get(index=1)
        week1_term2 = term2.weeks.get(index=1)
        
        # Add revenue to term 1
        lesson1 = Lesson.objects.create(
            group=self.group,
            date=timezone.now(),
            tutoringWeek=week1_term1
        )
        
        invoice1 = LocalInvoice.objects.create(
            stripeInvoiceId='inv_term1',
            status='paid',
            amount_due=5000,
            amount_paid=5000,
            created=timezone.now(),
            status_transitions_paid_at=timezone.now()
        )
        
        Attendance.objects.create(
            lesson=lesson1,
            tutoringStudent=self.student1,
            present=True,
            paid=True,
            local_invoice=invoice1
        )
        
        # Add revenue to term 2
        lesson2 = Lesson.objects.create(
            group=self.group,
            date=timezone.now(),
            tutoringWeek=week1_term2
        )
        
        invoice2 = LocalInvoice.objects.create(
            stripeInvoiceId='inv_term2',
            status='paid',
            amount_due=10000,
            amount_paid=10000,
            created=timezone.now(),
            status_transitions_paid_at=timezone.now()
        )
        
        Attendance.objects.create(
            lesson=lesson2,
            tutoringStudent=self.student2,
            present=True,
            paid=True,
            local_invoice=invoice2
        )
        
        # Verify each term has correct revenue
        revenue_term1 = self.term1.get_revenue()
        revenue_term2 = term2.get_revenue()
        
        self.assertEqual(revenue_term1, Decimal('50.00'))
        self.assertEqual(revenue_term2, Decimal('100.00'))
    
    def test_term_revenue_with_multiple_students_per_week(self):
        """Test term revenue when multiple students have paid invoices in the same week"""
        week1 = self.term1.weeks.get(index=1)
        
        lesson = Lesson.objects.create(
            group=self.group,
            date=timezone.now(),
            tutoringWeek=week1
        )
        
        # Create separate invoices for each student
        invoice1 = LocalInvoice.objects.create(
            stripeInvoiceId='inv_student1',
            status='paid',
            amount_due=5000,
            amount_paid=5000,
            created=timezone.now(),
            status_transitions_paid_at=timezone.now()
        )
        
        invoice2 = LocalInvoice.objects.create(
            stripeInvoiceId='inv_student2',
            status='paid',
            amount_due=5000,
            amount_paid=5000,
            created=timezone.now(),
            status_transitions_paid_at=timezone.now()
        )
        
        Attendance.objects.create(
            lesson=lesson,
            tutoringStudent=self.student1,
            present=True,
            paid=True,
            local_invoice=invoice1
        )
        
        Attendance.objects.create(
            lesson=lesson,
            tutoringStudent=self.student2,
            present=True,
            paid=True,
            local_invoice=invoice2
        )
        
        revenue = self.term1.get_revenue()
        # 2 students * $50 = $100
        self.assertEqual(revenue, Decimal('100.00'))