from django.db import models
from inventory.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()

class Bill(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    BILL_TYPE = [
        ('sale', 'Sale'),
        ('return', 'Return'),
    ]

    salesman = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_bills')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_bills')

    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.FloatField(default=0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    bill_type = models.CharField(max_length=10, choices=BILL_TYPE, default='sale')  # ✅ NEW

    def __str__(self):
        return f"Bill #{self.id} - {self.status} ({self.bill_type})"


class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()