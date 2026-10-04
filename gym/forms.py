from django import forms
from .models import Trainer, Plan, Member, Membership, Payment, Attendance


class BootstrapMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            w = f.widget
            if isinstance(w, forms.CheckboxInput):
                w.attrs["class"] = "form-check-input"
            elif isinstance(w, forms.Select):
                w.attrs["class"] = "form-select"
            else:
                w.attrs["class"] = "form-control"


class DateInput(forms.DateInput):
    input_type = "date"

    def __init__(self, **kw):
        super().__init__(format="%Y-%m-%d", **kw)


class TrainerForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Trainer
        fields = "__all__"


class PlanForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Plan
        fields = "__all__"


class MemberForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Member
        fields = "__all__"
        widgets = {"date_of_birth": DateInput(), "joined_on": DateInput()}


class MembershipForm(BootstrapMixin, forms.ModelForm):
    record_payment = forms.BooleanField(required=False, initial=True, label="Record payment for this plan")
    method = forms.ChoiceField(choices=Payment.METHODS, label="Payment method")

    class Meta:
        model = Membership
        fields = ["member", "plan", "start_date"]
        widgets = {"start_date": DateInput()}


class PaymentForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["member", "amount", "method", "paid_on", "note"]
        widgets = {"paid_on": DateInput()}


class CheckInForm(BootstrapMixin, forms.Form):
    member = forms.ModelChoiceField(queryset=Member.objects.filter(is_active=True))
