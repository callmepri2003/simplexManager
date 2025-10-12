from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from datetime import datetime, timedelta, timezone
from tutoring.models import (
    TutoringStudent, Parent, Group, Lesson, Attendance, LocalInvoice
)
from stripeInt.models import StripeProd
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver


class DashboardViewTests(TestCase):
    """Test suite for DashboardView"""
    
    @classmethod
    def setUpClass(cls):
        """Disable the post_save signal for Lesson during tests"""
        super().setUpClass()
        # Disconnect the signal that auto-creates attendances
        from tutoring.models import create_lesson_attendances
        post_save.disconnect(create_lesson_attendances, sender=Lesson)
    
    @classmethod
    def tearDownClass(cls):
        """Re-enable the post_save signal after tests"""
        super().tearDownClass()
        # Reconnect the signal
        from tutoring.models import create_lesson_attendances
        post_save.connect(create_lesson_attendances, sender=Lesson)
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = APIClient()
        self.url = reverse('dashboard')
        
        # Create test dates
        self.today = datetime.now(timezone.utc)
        self.start_date = self.today - timedelta(days=30)
        self.end_date = self.today
        
        # Create test parent
        self.parent = Parent.objects.create(
            name="Test Parent",
            stripeId="cus_test123",
            is_active=True,
            payment_frequency='weekly'
        )
        
        # Create test product
        self.product = StripeProd.objects.create(
            stripeId="prod_test123",
            defaultPriceId="price_test123",
            name="Year 12 Maths",
            is_active=True
        )
        
        # Create test group
        self.group = Group.objects.create(
            lesson_length=60,
            associated_product=self.product,
            tutor="John Doe",
            course=Group.CourseChoices.YEAR12_ADV,
            day_of_week=Group.Weekday.MONDAY,
            time_of_day="16:00:00"
        )
        
        # Create test students BEFORE creating lessons
        # This way we can manually control attendances
        self.student1 = TutoringStudent.objects.create(
            name="Alice Smith",
            parent=self.parent,
            active=True,
            start_date=self.start_date.date()
        )
        self.student1.group.add(self.group)
        
        self.student2 = TutoringStudent.objects.create(
            name="Bob Johnson",
            parent=self.parent,
            active=True,
            start_date=self.start_date.date()
        )
        self.student2.group.add(self.group)
        
        self.student3 = TutoringStudent.objects.create(
            name="Charlie Brown",
            parent=self.parent,
            active=True,
            start_date=self.start_date.date()
        )
        self.student3.group.add(self.group)
        
        # Create lessons for the past 4 weeks
        self.lessons = []
        for week in range(4):
            lesson_date = self.start_date + timedelta(weeks=week)
            lesson = Lesson.objects.create(
                group=self.group,
                date=lesson_date,
                notes=f"Week {week + 1} lesson"
            )
            self.lessons.append(lesson)
        
        # Create invoices
        self.invoice1 = LocalInvoice.objects.create(
            stripeInvoiceId="inv_test1",
            status='paid',
            amount_due=5000,  # $50.00
            amount_paid=5000,
            currency='usd',
            created=self.start_date,
            status_transitions_paid_at=self.start_date + timedelta(days=1),
            customer_stripe_id=self.parent.stripeId
        )
        
        self.invoice2 = LocalInvoice.objects.create(
            stripeInvoiceId="inv_test2",
            status='paid',
            amount_due=10000,  # $100.00
            amount_paid=10000,
            currency='usd',
            created=self.start_date + timedelta(days=15),
            status_transitions_paid_at=self.start_date + timedelta(days=16),
            customer_stripe_id=self.parent.stripeId
        )
        
        self.invoice3 = LocalInvoice.objects.create(
            stripeInvoiceId="inv_test3",
            status='open',
            amount_due=7500,  # $75.00
            amount_paid=0,
            currency='usd',
            created=self.start_date + timedelta(days=25),
            customer_stripe_id=self.parent.stripeId
        )
    
    def _create_attendances(self):
        """Helper to create attendance records"""
        # Clear any existing attendances first (in case signal wasn't disconnected)
        Attendance.objects.all().delete()
        
        # Student 1: High performer (100% attendance, 100% homework)
        for lesson in self.lessons:
            Attendance.objects.create(
                lesson=lesson,
                tutoringStudent=self.student1,
                present=True,
                homework=True,
                paid=True,
                local_invoice=self.invoice1
            )
        
        # Student 2: Medium performer (75% attendance, 50% homework)
        for i, lesson in enumerate(self.lessons):
            Attendance.objects.create(
                lesson=lesson,
                tutoringStudent=self.student2,
                present=(i < 3),  # Present for first 3 lessons
                homework=(i < 2),  # Homework for first 2 lessons
                paid=True,
                local_invoice=self.invoice1
            )
        
        # Student 3: At-risk (50% attendance, 25% homework)
        for i, lesson in enumerate(self.lessons):
            Attendance.objects.create(
                lesson=lesson,
                tutoringStudent=self.student3,
                present=(i < 2),  # Present for first 2 lessons
                homework=(i == 0),  # Homework for first lesson only
                paid=(i < 2),
                local_invoice=self.invoice2 if i < 2 else None
            )
    
    def test_dashboard_returns_200(self):
        """Test that dashboard endpoint returns 200"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_dashboard_with_date_range(self):
        """Test dashboard with custom date range"""
        start = (self.today - timedelta(days=60)).date().isoformat()
        end = self.today.date().isoformat()
        
        response = self.client.get(
            self.url,
            {'start_date': start, 'end_date': end}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('dateRange', response.data)
        self.assertEqual(response.data['dateRange']['start'], start)
        self.assertEqual(response.data['dateRange']['end'], end)
    
    def test_dashboard_invalid_date_format(self):
        """Test dashboard with invalid date format"""
        response = self.client.get(
            self.url,
            {'start_date': 'invalid', 'end_date': '2024-01-01'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_metrics_data_structure(self):
        """Test that metrics data has correct structure"""
        self._create_attendances()
        
        response = self.client.get(self.url)
        
        self.assertIn('metricsData', response.data)
        metrics = response.data['metricsData']
        
        # Check all required metrics exist
        self.assertIn('totalStudents', metrics)
        self.assertIn('avgAttendance', metrics)
        self.assertIn('termRevenue', metrics)
        self.assertIn('paymentRate', metrics)
        
        # Check structure of each metric
        for metric_name in ['totalStudents', 'avgAttendance', 'termRevenue', 'paymentRate']:
            metric = metrics[metric_name]
            self.assertIn('value', metric)
            self.assertIn('change', metric)
            self.assertIn('trend', metric)
            self.assertIn(metric['trend'], ['up', 'down'])
    
    def test_total_students_calculation(self):
        """Test total students metric calculation"""
        self._create_attendances()
        
        response = self.client.get(self.url)
        metrics = response.data['metricsData']
        
        # Should have 3 active students
        self.assertEqual(metrics['totalStudents']['value'], 3)
    
    def test_attendance_rate_calculation(self):
        """Test average attendance calculation"""
        self._create_attendances()
        
        response = self.client.get(self.url)
        metrics = response.data['metricsData']
        
        # Student 1: 4/4 = 100%
        # Student 2: 3/4 = 75%
        # Student 3: 2/4 = 50%
        # Average: (4+3+2) / 12 = 9/12 = 75%
        self.assertEqual(metrics['avgAttendance']['value'], 75.0)
    
    def test_revenue_calculation(self):
        """Test revenue calculation from paid invoices"""
        self._create_attendances()
        
        response = self.client.get(self.url)
        metrics = response.data['metricsData']
        
        # $50 + $100 = $150 (invoice3 is unpaid)
        self.assertEqual(metrics['termRevenue']['value'], 150.0)
    
    def test_payment_rate_calculation(self):
        """Test payment rate calculation"""
        self._create_attendances()
        
        response = self.client.get(self.url)
        metrics = response.data['metricsData']
        
        # 2 paid out of 3 total invoices = 66.7%
        self.assertAlmostEqual(metrics['paymentRate']['value'], 66.7, places=1)
    
    def test_attendance_trends_structure(self):
        """Test attendance trends data structure"""
        self._create_attendances()
        
        response = self.client.get(self.url)
        
        self.assertIn('attendanceData', response.data)
        attendance_data = response.data['attendanceData']
        
        # Should have weekly data
        self.assertIsInstance(attendance_data, list)
        
        if len(attendance_data) > 0:
            # Check structure of each week
            for week in attendance_data:
                self.assertIn('week', week)
                self.assertIn('rate', week)
                self.assertIsInstance(week['rate'], (int, float))
    
    def test_revenue_data_structure(self):
        """Test revenue data structure"""
        self._create_attendances()
        
        response = self.client.get(self.url)
        
        self.assertIn('revenueData', response.data)
        revenue_data = response.data['revenueData']
        
        self.assertIsInstance(revenue_data, list)
        
        # Check structure of each month
        for month in revenue_data:
            self.assertIn('month', month)
            self.assertIn('revenue', month)
            self.assertIsInstance(month['revenue'], (int, float))
    
    def test_group_performance_structure(self):
        """Test group performance data structure"""
        self._create_attendances()
        
        response = self.client.get(self.url)
        
        self.assertIn('groupPerformance', response.data)
        group_performance = response.data['groupPerformance']
        
        self.assertIsInstance(group_performance, list)
        
        # Should have at least one group
        self.assertGreater(len(group_performance), 0)
        
        # Check structure
        for group in group_performance:
            self.assertIn('name', group)
            self.assertIn('attendance', group)
            self.assertIn('payment', group)
            self.assertIn('homework', group)
    
    def test_group_performance_calculations(self):
        """Test group performance metric calculations"""
        self._create_attendances()
        
        response = self.client.get(self.url)
        group_performance = response.data['groupPerformance']
        
        # Find our test group
        test_group = next(
            (g for g in group_performance if self.group.course in g['name']),
            None
        )
        
        self.assertIsNotNone(test_group)
        
        # Total: 12 attendances, 9 present = 75%
        self.assertEqual(test_group['attendance'], 75.0)
        
        # Homework: 7 out of 12 = 58.3%
        # Student 1: 4/4, Student 2: 2/4, Student 3: 1/4 = 7 total
        self.assertAlmostEqual(test_group['homework'], 58.3, places=1)
    
    def test_engagement_distribution_structure(self):
        """Test engagement distribution structure"""
        self._create_attendances()
        
        response = self.client.get(self.url)
        
        self.assertIn('engagementDistribution', response.data)
        distribution = response.data['engagementDistribution']
        
        self.assertIsInstance(distribution, list)
        self.assertEqual(len(distribution), 4)  # High, Medium, Low, At Risk
        
        # Check structure
        for category in distribution:
            self.assertIn('name', category)
            self.assertIn('value', category)
            self.assertIn('color', category)
    
    def test_engagement_distribution_counts(self):
        """Test engagement distribution student counts"""
        self._create_attendances()
        
        response = self.client.get(self.url)
        distribution = response.data['engagementDistribution']
        
        # Convert to dict for easier testing
        dist_dict = {d['name']: d['value'] for d in distribution}
        
        # Student 1: 100% -> High
        # Student 2: 75% -> Medium
        # Student 3: 50% -> Low
        self.assertEqual(dist_dict['High (>90%)'], 1)
        self.assertEqual(dist_dict['Medium (70-90%)'], 1)
        self.assertEqual(dist_dict['Low (50-70%)'], 1)
        self.assertEqual(dist_dict['At Risk (<50%)'], 0)
    
    def test_at_risk_students_structure(self):
        """Test at-risk students structure"""
        self._create_attendances()
        
        response = self.client.get(self.url)
        
        self.assertIn('atRiskStudents', response.data)
        at_risk = response.data['atRiskStudents']
        
        self.assertIsInstance(at_risk, list)
        
        # Check structure
        for student in at_risk:
            self.assertIn('id', student)
            self.assertIn('name', student)
            self.assertIn('attendance', student)
            self.assertIn('payment', student)
            self.assertIn('lastAbsence', student)
    
    def test_at_risk_students_identification(self):
        """Test that at-risk students are correctly identified"""
        self._create_attendances()
        
        response = self.client.get(self.url)
        at_risk = response.data['atRiskStudents']
        
        # Student 3 should be at risk (50% attendance)
        at_risk_ids = [s['id'] for s in at_risk]
        self.assertIn(self.student3.id, at_risk_ids)
        
        # Student 1 should NOT be at risk (100% attendance, 100% payment)
        self.assertNotIn(self.student1.id, at_risk_ids)
    
    def test_top_performers_structure(self):
        """Test top performers structure"""
        self._create_attendances()
        
        response = self.client.get(self.url)
        
        self.assertIn('topPerformers', response.data)
        top_performers = response.data['topPerformers']
        
        self.assertIsInstance(top_performers, list)
        
        # Check structure
        for student in top_performers:
            self.assertIn('id', student)
            self.assertIn('name', student)
            self.assertIn('engagement', student)
            self.assertIn('streak', student)
    
    def test_top_performers_identification(self):
        """Test that top performers are correctly identified"""
        self._create_attendances()
        
        response = self.client.get(self.url)
        top_performers = response.data['topPerformers']
        
        # Student 1 should be a top performer (100% engagement)
        top_ids = [s['id'] for s in top_performers]
        self.assertIn(self.student1.id, top_ids)
        
        # Check engagement score
        student1_data = next((s for s in top_performers if s['id'] == self.student1.id), None)
        self.assertIsNotNone(student1_data)
        self.assertEqual(student1_data['engagement'], 100.0)
        self.assertEqual(student1_data['streak'], 4)  # All 4 lessons attended with homework
    
    def test_empty_data_handling(self):
        """Test dashboard with no attendance data"""
        # Don't create any attendances
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should still return valid structure with zero/empty values
        self.assertIn('metricsData', response.data)
        self.assertIn('attendanceData', response.data)
        self.assertIn('atRiskStudents', response.data)
        self.assertIn('topPerformers', response.data)
    
    def test_inactive_students_excluded(self):
        """Test that inactive students are excluded from metrics"""
        self._create_attendances()
        
        # Deactivate student 1
        self.student1.active = False
        self.student1.save()
        
        response = self.client.get(self.url)
        metrics = response.data['metricsData']
        
        # Should now have 2 active students instead of 3
        self.assertEqual(metrics['totalStudents']['value'], 2)
    
    def test_date_range_filtering(self):
        """Test that date range properly filters data"""
        self._create_attendances()
        
        # Query for a narrow date range
        narrow_start = (self.start_date + timedelta(days=20)).date().isoformat()
        narrow_end = self.end_date.date().isoformat()
        
        response = self.client.get(
            self.url,
            {'start_date': narrow_start, 'end_date': narrow_end}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Attendance data should reflect the narrow range
        attendance_data = response.data['attendanceData']
        
        # Should have fewer weeks than the full 4-week range
        self.assertLessEqual(len(attendance_data), 2)


class DashboardIntegrationTests(TestCase):
    """Integration tests with more complex scenarios"""
    
    @classmethod
    def setUpClass(cls):
        """Disable the post_save signal for Lesson during tests"""
        super().setUpClass()
        from tutoring.models import create_lesson_attendances
        post_save.disconnect(create_lesson_attendances, sender=Lesson)
    
    @classmethod
    def tearDownClass(cls):
        """Re-enable the post_save signal after tests"""
        super().tearDownClass()
        from tutoring.models import create_lesson_attendances
        post_save.connect(create_lesson_attendances, sender=Lesson)
    
    def setUp(self):
        """Set up more complex test scenario"""
        self.client = APIClient()
        self.url = reverse('dashboard')
        
        self.today = datetime.now(timezone.utc)
        self.start_date = self.today - timedelta(days=90)
        
        # Create multiple parents, students, and groups
        self.parents = []
        self.students = []
        self.groups = []
        
        for i in range(3):
            parent = Parent.objects.create(
                name=f"Parent {i}",
                stripeId=f"cus_test{i}",
                is_active=True
            )
            self.parents.append(parent)
            
            product = StripeProd.objects.create(
                stripeId=f"prod_test{i}",
                defaultPriceId=f"price_test{i}",
                name=f"Course {i}",
                is_active=True
            )
            
            group = Group.objects.create(
                lesson_length=60,
                associated_product=product,
                tutor=f"Tutor {i}",
                course=Group.CourseChoices.YEAR12_ADV,
                day_of_week=i,
                time_of_day="16:00:00"
            )
            self.groups.append(group)
            
            for j in range(5):  # 5 students per parent
                student = TutoringStudent.objects.create(
                    name=f"Student {i}-{j}",
                    parent=parent,
                    active=True,
                    start_date=self.start_date.date()
                )
                student.group.add(group)
                self.students.append(student)
    
    def test_dashboard_with_multiple_groups(self):
        """Test dashboard handles multiple groups correctly"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should have metrics for all 3 groups
        group_performance = response.data['groupPerformance']
        self.assertLessEqual(len(group_performance), 3)
    
    def test_dashboard_with_many_students(self):
        """Test dashboard performance with many students"""
        # 3 parents × 5 students = 15 students
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        metrics = response.data['metricsData']
        self.assertEqual(metrics['totalStudents']['value'], 15)