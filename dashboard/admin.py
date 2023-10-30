from django.contrib import admin

# Register your models here.
from .models import Transaction, Budget, RecurringBills

admin.site.register(Transaction)
admin.site.register(Budget)
admin.site.register(RecurringBills)