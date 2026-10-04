from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import (CheckInForm, MemberForm, MembershipForm, PaymentForm,
                    PlanForm, TrainerForm)
from .models import Attendance, Member, Membership, Payment, Plan, Trainer


@login_required
def dashboard(request):
    today = timezone.localdate()
    month_start = today.replace(day=1)
    active_ids = Membership.objects.filter(start_date__lte=today, end_date__gte=today).values_list("member_id", flat=True).distinct()
    revenue = Payment.objects.filter(paid_on__gte=month_start).aggregate(t=Sum("amount"))["t"] or Decimal("0")
    expiring = Membership.objects.filter(end_date__gte=today, end_date__lte=today + timedelta(days=7)).select_related("member", "plan")
    # revenue for the last 6 months
    months = []
    y, m = today.year, today.month
    for _ in range(6):
        start = today.replace(year=y, month=m, day=1)
        ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
        end = start.replace(year=ny, month=nm)
        total = Payment.objects.filter(paid_on__gte=start, paid_on__lt=end).aggregate(t=Sum("amount"))["t"] or 0
        months.append({"label": start.strftime("%b %Y"), "total": total})
        y, m = (y - 1, 12) if m == 1 else (y, m - 1)
    months.reverse()
    top = max([x["total"] for x in months] + [1])
    for x in months:
        x["pct"] = int(x["total"] * 100 / top)
    ctx = {
        "total_members": Member.objects.count(),
        "active_members": len(set(active_ids)),
        "revenue": revenue,
        "checkins_today": Attendance.objects.filter(check_in__date=today).count(),
        "inside_now": Attendance.objects.filter(check_in__date=today, check_out__isnull=True).count(),
        "expiring": expiring,
        "recent_payments": Payment.objects.select_related("member")[:5],
        "months": months,
    }
    return render(request, "gym/dashboard.html", ctx)


# ---------- generic helpers ----------
def _form_view(request, form_class, title, back, instance=None):
    form = form_class(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Saved successfully.")
        return redirect(back)
    return render(request, "gym/form.html", {"form": form, "title": title, "back": back})


def _delete_view(request, obj, back):
    if request.method == "POST":
        try:
            obj.delete()
            messages.success(request, "Deleted.")
        except Exception:
            messages.error(request, "Cannot delete: this record is in use.")
        return redirect(back)
    return render(request, "gym/confirm_delete.html", {"obj": obj, "back": back})


# ---------- members ----------
@login_required
def member_list(request):
    q = request.GET.get("q", "").strip()
    members = Member.objects.select_related("trainer")
    if q:
        members = members.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(phone__icontains=q))
    return render(request, "gym/member_list.html", {"members": members, "q": q})


@login_required
def member_detail(request, pk):
    member = get_object_or_404(Member, pk=pk)
    return render(request, "gym/member_detail.html", {
        "member": member,
        "memberships": member.memberships.select_related("plan"),
        "payments": member.payments.all()[:10],
        "attendance": member.attendance.all()[:10],
    })


@login_required
def member_create(request):
    return _form_view(request, MemberForm, "Add Member", "member_list")


@login_required
def member_edit(request, pk):
    return _form_view(request, MemberForm, "Edit Member", "member_list", get_object_or_404(Member, pk=pk))


@login_required
def member_delete(request, pk):
    return _delete_view(request, get_object_or_404(Member, pk=pk), "member_list")


# ---------- plans ----------
@login_required
def plan_list(request):
    return render(request, "gym/plan_list.html", {"plans": Plan.objects.all()})


@login_required
def plan_create(request):
    return _form_view(request, PlanForm, "Add Plan", "plan_list")


@login_required
def plan_edit(request, pk):
    return _form_view(request, PlanForm, "Edit Plan", "plan_list", get_object_or_404(Plan, pk=pk))


@login_required
def plan_delete(request, pk):
    return _delete_view(request, get_object_or_404(Plan, pk=pk), "plan_list")


# ---------- trainers ----------
@login_required
def trainer_list(request):
    return render(request, "gym/trainer_list.html", {"trainers": Trainer.objects.all()})


@login_required
def trainer_create(request):
    return _form_view(request, TrainerForm, "Add Trainer", "trainer_list")


@login_required
def trainer_edit(request, pk):
    return _form_view(request, TrainerForm, "Edit Trainer", "trainer_list", get_object_or_404(Trainer, pk=pk))


@login_required
def trainer_delete(request, pk):
    return _delete_view(request, get_object_or_404(Trainer, pk=pk), "trainer_list")


# ---------- memberships ----------
@login_required
def membership_list(request):
    return render(request, "gym/membership_list.html", {"memberships": Membership.objects.select_related("member", "plan")})


@login_required
def membership_create(request):
    initial = {}
    if request.GET.get("member"):
        initial["member"] = request.GET["member"]
    form = MembershipForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        ms = form.save()
        if form.cleaned_data["record_payment"]:
            Payment.objects.create(member=ms.member, membership=ms, amount=ms.plan.price,
                                   method=form.cleaned_data["method"], note=f"Plan: {ms.plan.name}")
        messages.success(request, "Membership assigned.")
        return redirect("membership_list")
    return render(request, "gym/form.html", {"form": form, "title": "Assign Membership", "back": "membership_list"})


@login_required
def membership_delete(request, pk):
    return _delete_view(request, get_object_or_404(Membership, pk=pk), "membership_list")


# ---------- payments ----------
@login_required
def payment_list(request):
    payments = Payment.objects.select_related("member")
    total = payments.aggregate(t=Sum("amount"))["t"] or 0
    return render(request, "gym/payment_list.html", {"payments": payments[:200], "total": total})


@login_required
def payment_create(request):
    return _form_view(request, PaymentForm, "Record Payment", "payment_list")


# ---------- attendance ----------
@login_required
def attendance(request):
    form = CheckInForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        member = form.cleaned_data["member"]
        if not member.current_membership:
            messages.error(request, f"{member} has no active membership.")
        elif Attendance.objects.filter(member=member, check_out__isnull=True, check_in__date=timezone.localdate()).exists():
            messages.warning(request, f"{member} is already checked in.")
        else:
            Attendance.objects.create(member=member)
            messages.success(request, f"{member} checked in.")
        return redirect("attendance")
    today = timezone.localdate()
    return render(request, "gym/attendance.html", {
        "form": form,
        "today_records": Attendance.objects.filter(check_in__date=today).select_related("member"),
        "history": Attendance.objects.exclude(check_in__date=today).select_related("member")[:20],
    })


@login_required
@require_POST
def check_out(request, pk):
    rec = get_object_or_404(Attendance, pk=pk)
    if not rec.check_out:
        rec.check_out = timezone.now()
        rec.save()
        messages.success(request, f"{rec.member} checked out.")
    return redirect("attendance")
