from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('salesman', 'Salesman'),
        ('inventory', 'Inventory Manager'),
        ('sales_manager', 'Sales Manager'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_approved = models.BooleanField(default=False)