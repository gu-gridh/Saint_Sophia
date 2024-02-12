from django.db import models
from django.utils.translation import gettext_lazy as _


class GenderedMixin(models.Model):

    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('-', 'Other'),
        ('X', 'Unknown'),
    )

    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True, verbose_name=_("abstract.gender"))

    class Meta:
        abstract = True