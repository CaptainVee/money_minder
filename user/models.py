from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
import uuid
from common.models import BaseModel
from django.conf import settings

class User(AbstractUser):
    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(_("Name of user"), blank=False, null=False, max_length=250)
    first_name = None
    last_name = None
    email = models.EmailField(_("Email Address"), unique=True)
    username = models.CharField(
        verbose_name=_("username"), db_index=True, max_length=255, unique=True
    )
    date_joined = models.DateTimeField(auto_now_add=True)
    is_instructor = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse("profile")

    def __str__(self):
        return self.email

    @property
    def get_full_name(self):
        if self.name:
            return self.name
        return self.username

    @property
    def courses(self):
        return self.course_set.all().order_by("created_at")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")


class Profile(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=False, null=False, related_name='profile')
    total_balance = models.PositiveSmallIntegerField(default=0)
    auth_id = models.JSONField(max_length=100, blank=True, null=True)


class BankAccount(BaseModel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=False, null=False)
    account_name = models.CharField(max_length=120, blank=False, null=False)
    account_number = models.PositiveIntegerField(blank=False, null=False)
    bank = models.CharField(max_length=120, blank=False, null=False)