from django.urls import path
from . import views as v

urlpatterns = [
    path("", v.dashboard, name="dashboard"),
    path("members/", v.member_list, name="member_list"),
    path("members/add/", v.member_create, name="member_create"),
    path("members/<int:pk>/", v.member_detail, name="member_detail"),
    path("members/<int:pk>/edit/", v.member_edit, name="member_edit"),
    path("members/<int:pk>/delete/", v.member_delete, name="member_delete"),
    path("plans/", v.plan_list, name="plan_list"),
    path("plans/add/", v.plan_create, name="plan_create"),
    path("plans/<int:pk>/edit/", v.plan_edit, name="plan_edit"),
    path("plans/<int:pk>/delete/", v.plan_delete, name="plan_delete"),
    path("trainers/", v.trainer_list, name="trainer_list"),
    path("trainers/add/", v.trainer_create, name="trainer_create"),
    path("trainers/<int:pk>/edit/", v.trainer_edit, name="trainer_edit"),
    path("trainers/<int:pk>/delete/", v.trainer_delete, name="trainer_delete"),
    path("memberships/", v.membership_list, name="membership_list"),
    path("memberships/add/", v.membership_create, name="membership_create"),
    path("memberships/<int:pk>/delete/", v.membership_delete, name="membership_delete"),
    path("payments/", v.payment_list, name="payment_list"),
    path("payments/add/", v.payment_create, name="payment_create"),
    path("attendance/", v.attendance, name="attendance"),
    path("attendance/<int:pk>/checkout/", v.check_out, name="check_out"),
]
