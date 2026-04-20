from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
# 📂 Category Model
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# 📦 Product Model
class Product(models.Model):
    name = models.CharField(max_length=150)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.FloatField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# 📊 Inventory Model (Stock tracking)
class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.pk:
            old = Inventory.objects.get(pk=self.pk)

            diff = self.quantity - old.quantity

            if diff != 0:
                from .models import InventoryLog

                InventoryLog.objects.create(
                    product=self.product,
                    quantity=abs(diff),
                    transaction_type='in' if diff > 0 else 'out',
                    source='admin',
                    user=None  # optional
                )

        super().save(*args, **kwargs)



class InventoryLog(models.Model):
    TRANSACTION_TYPE = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
    ]

    SOURCE_TYPE = [
        ('sale', 'Sales Bill'),
        ('return', 'Return Bill'),
        ('admin', 'Admin Update'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)
    source = models.CharField(max_length=10, choices=SOURCE_TYPE)

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    timestamp = models.DateTimeField(auto_now_add=True)