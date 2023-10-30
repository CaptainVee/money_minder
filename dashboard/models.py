from django.db import models
from django.conf import settings
from common.models import BaseModel
from user.models import BankAccount
from django.db.models import Sum

User = settings.AUTH_USER_MODEL


class Category(BaseModel):
    name = models.CharField(max_length=120, null=True, blank=False)


class Expense(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

class Transaction(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=120, null=True, blank=False)
    date = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=10, null=True, blank=True)
    description = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    budget = models.ForeignKey("Budget", on_delete=models.SET_NULL, null=True, blank=True)

class Budget(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def is_within_budget(self, expense_amount):
        """
        Check if the expense amount is within the budget amount.
        """
        return self.amount >= expense_amount

    def calculate_total_transactons(self):
        total_transactions_amount = self.transaction_set.aggregate(total_amount=Sum('amount'))['total_amount']
        if total_transactions_amount is None:
            total_transactions_amount = 0

        return total_transactions_amount

    def calculate_excess_amount(self):
        total_transactions_amount = self.calculate_total_transactons()
        amount_left = self.amount - total_transactions_amount
        if amount_left > 0:
            return 0
        return amount_left
    

class RecurringBills(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=120, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    payment_date = models.DateField(null=True, blank=True)
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, null=True)
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True)

