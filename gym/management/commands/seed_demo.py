import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from gym.models import Attendance, Member, Membership, Payment, Plan, Trainer


class Command(BaseCommand):
    help = "Create demo login (admin / admin123) and sample gym data."

    def handle(self, *args, **opts):
        User = get_user_model()
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin123")
        if Member.objects.exists():
            self.stdout.write("Demo data already exists - skipping.")
            return
        random.seed(1)
        today = timezone.localdate()
        trainers = [Trainer.objects.create(name=n, phone=p, specialization=s) for n, p, s in [
            ("Ramesh Thapa", "9801000001", "Weight Training"),
            ("Sunita Rai", "9801000002", "Yoga & Cardio"),
            ("Bikash Gurung", "9801000003", "CrossFit"),
        ]]
        plans = [Plan.objects.create(name=n, duration_days=d, price=pr, description=ds) for n, d, pr, ds in [
            ("Monthly", 30, 2000, "Full gym access"),
            ("Quarterly", 90, 5500, "Full gym access, 3 months"),
            ("Half Yearly", 180, 10000, "Gym + 2 trainer sessions"),
            ("Yearly", 365, 18000, "Gym + trainer + locker"),
        ]]
        names = [("Aarav", "Sharma"), ("Sita", "Karki"), ("Anil", "Shrestha"), ("Pooja", "Basnet"),
                 ("Rohan", "Adhikari"), ("Nisha", "Magar"), ("Suman", "Tamang"), ("Kabita", "Poudel"),
                 ("Dipesh", "Khadka"), ("Mina", "Lama")]
        for i, (fn, ln) in enumerate(names):
            m = Member.objects.create(
                first_name=fn, last_name=ln, phone=f"98410000{i:02d}", email=f"{fn.lower()}@example.com",
                gender="F" if fn in ("Sita", "Pooja", "Nisha", "Kabita", "Mina") else "M",
                address="Kathmandu", joined_on=today - timedelta(days=random.randint(10, 200)),
                trainer=random.choice(trainers))
            plan = random.choice(plans)
            start = today - timedelta(days=random.randint(0, plan.duration_days + 20))
            ms = Membership.objects.create(member=m, plan=plan, start_date=start)
            Payment.objects.create(member=m, membership=ms, amount=plan.price, paid_on=start,
                                   method=random.choice(["cash", "card", "online"]), note=f"Plan: {plan.name}")
            if ms.is_active:
                for d in range(random.randint(1, 8)):
                    t = timezone.now() - timedelta(days=d, hours=random.randint(1, 5))
                    Attendance.objects.create(member=m, check_in=t, check_out=t + timedelta(hours=1, minutes=15))
        self.stdout.write(self.style.SUCCESS("Demo data created. Login: admin / admin123"))
