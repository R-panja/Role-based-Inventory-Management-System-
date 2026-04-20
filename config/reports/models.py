from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
# Create your models here.
class ReportException(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    exception = models.TextField()
    salesman = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_exception')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_exception')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')