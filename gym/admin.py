from django.contrib import admin
from .models import Trainer, Plan, Member, Membership, Payment, Attendance

for m in (Trainer, Plan, Member, Membership, Payment, Attendance):
    admin.site.register(m)
