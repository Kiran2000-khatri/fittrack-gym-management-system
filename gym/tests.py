from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Attendance, Member, Payment, Plan


class FlowTests(TestCase):
    def setUp(self):
        get_user_model().objects.create_user("staff", password="pw12345!")
        self.client.login(username="staff", password="pw12345!")
        self.plan = Plan.objects.create(name="Monthly", duration_days=30, price=2000)

    def test_pages_load(self):
        for n in ["dashboard", "member_list", "member_create", "plan_list", "plan_create", "trainer_list",
                  "trainer_create", "membership_list", "membership_create", "payment_list",
                  "payment_create", "attendance"]:
            self.assertEqual(self.client.get(reverse(n)).status_code, 200, n)

    def test_login_required(self):
        self.client.logout()
        self.assertEqual(self.client.get("/").status_code, 302)

    def test_full_flow(self):
        self.client.post(reverse("member_create"), {"first_name": "T", "last_name": "U", "phone": "1",
                                                    "gender": "M", "joined_on": "2026-10-04"})
        m = Member.objects.get(first_name="T")
        # no plan -> check-in refused
        self.client.post(reverse("attendance"), {"member": m.pk})
        self.assertEqual(Attendance.objects.count(), 0)
        # assign plan with payment
        self.client.post(reverse("membership_create"), {"member": m.pk, "plan": self.plan.pk,
                         "start_date": "2026-10-04", "record_payment": "on", "method": "cash"})
        self.assertEqual(Payment.objects.filter(member=m).count(), 1)
        self.assertEqual(str(m.memberships.first().end_date), "2026-11-03")
