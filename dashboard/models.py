from django.db import models
from django.conf import settings
from common.models import BaseModel
from user.models import BankAccount

User = settings.AUTH_USER_MODEL



class Expense(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

class Transaction(BaseModel):
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    date = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    category = models.CharField(max_length=50)

class Budget(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def is_within_budget(self, expense_amount):
        """
        Check if the expense amount is within the budget amount.
        """
        return self.amount >= expense_amount

    def remaining_amount(self):
        """
        Calculate the remaining amount within the budget.
        """
        expenses = Expense.objects.filter(user=self.user)
        total_expense_amount = sum(expense.amount for expense in expenses)
        remaining_amount = self.amount - total_expense_amount
        return remaining_amount
