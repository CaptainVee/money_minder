from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from common.models import BaseModel


class User(AbstractUser):
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

