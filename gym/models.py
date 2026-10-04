from datetime import timedelta
from django.db import models
from django.utils import timezone


class Trainer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    specialization = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class Plan(models.Model):
    name = models.CharField(max_length=100)
    duration_days = models.PositiveIntegerField(help_text="Length of the plan in days")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.name} ({self.duration_days} days)"


class Member(models.Model):
    GENDERS = [("M", "Male"), ("F", "Female"), ("O", "Other")]
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    gender = models.CharField(max_length=1, choices=GENDERS, default="M")
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    joined_on = models.DateField(default=timezone.localdate)
    trainer = models.ForeignKey(Trainer, null=True, blank=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["first_name", "last_name"]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def current_membership(self):
        today = timezone.localdate()
        return self.memberships.filter(start_date__lte=today, end_date__gte=today).order_by("-end_date").first()

    def __str__(self):
        return self.full_name


class Membership(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="memberships")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    start_date = models.DateField(default=timezone.localdate)
    end_date = models.DateField(blank=True)

    class Meta:
        ordering = ["-start_date"]

    def save(self, *args, **kwargs):
        self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.start_date <= timezone.localdate() <= self.end_date

    @property
    def days_left(self):
        return (self.end_date - timezone.localdate()).days

    def __str__(self):
        return f"{self.member} - {self.plan.name}"


class Payment(models.Model):
    METHODS = [("cash", "Cash"), ("card", "Card"), ("online", "Online / Wallet")]
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="payments")
    membership = models.ForeignKey(Membership, null=True, blank=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=10, choices=METHODS, default="cash")
    paid_on = models.DateField(default=timezone.localdate)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-paid_on", "-id"]

    def __str__(self):
        return f"{self.member} - {self.amount}"


class Attendance(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="attendance")
    check_in = models.DateTimeField(default=timezone.now)
    check_out = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-check_in"]

    def __str__(self):
        return f"{self.member} @ {self.check_in:%Y-%m-%d %H:%M}"
