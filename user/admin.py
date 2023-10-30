from django.contrib import admin

from .models import User, Profile, BankAccount
# Register your models here.

admin.site.register(User)
admin.site.register(Profile)
admin.site.register(BankAccount)