from django import forms
from .models import Budget, Transaction

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['title','amount']


class TransactionForm(forms.ModelForm):
    budget = forms.ModelChoiceField(queryset=Budget.objects.all())

    class Meta:
        model = Transaction
        fields = ['budget']