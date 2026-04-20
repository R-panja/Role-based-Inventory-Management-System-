# inventory/management/commands/populate_db.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import random
from inventory.models import *
from sales.models import *

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with realistic test data'

    def handle(self, *args, **options):
        self.stdout.write('Starting database population...')
        
        # Clear existing data (but keep existing users if you want)
        self.clean_database()
        
        # Create data
        self.create_users()
        self.create_categories()
        self.create_products()
        self.create_bills()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Database populated successfully!\n'
                f'   - Users: {User.objects.count()}\n'
                f'   - Categories: {Category.objects.count()}\n'
                f'   - Products: {Product.objects.count()}\n'
                f'   - Inventory: {Inventory.objects.count()}\n'
                f'   - Bills: {Bill.objects.count()}\n'
                f'   - Bill Items: {BillItem.objects.count()}'
            )
        )

    def clean_database(self):
        """Clear existing data in correct order to avoid foreign key issues"""
        self.stdout.write('Cleaning existing data...')
        
        # Delete in correct order (child tables first)
        BillItem.objects.all().delete()
        Bill.objects.all().delete()
        Inventory.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        
        # Don't delete users if you want to keep them
        # User.objects.exclude(is_superuser=True).delete()
        
        self.stdout.write('   Database cleaned')

    def create_users(self):
        """Create users with different roles"""
        
        # Create or update admin user
        admin, created = User.objects.update_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'is_approved': True,
                'is_active': True
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write('   ✓ Created admin user (admin/admin123)')
        else:
            # Update password for existing admin
            admin.set_password('admin123')
            admin.save()
            self.stdout.write('   ✓ Updated admin user (admin/admin123)')
        
        # Create salesmen (skip if they already exist)
        salesmen_data = [
            ('salesman1', 'salesman1@example.com', 'Sales', 'Person1'),
            ('salesman2', 'salesman2@example.com', 'Sales', 'Person2'),
            ('salesman3', 'salesman3@example.com', 'Sales', 'Person3'),
            ('salesman4', 'salesman4@example.com', 'Sales', 'Person4'),
            ('salesman5', 'salesman5@example.com', 'Sales', 'Person5'),
        ]
        
        for username, email, first_name, last_name in salesmen_data:
            salesman, created = User.objects.update_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': 'salesman',
                    'is_approved': True,
                    'is_active': True,
                    'is_staff': False,
                    'is_superuser': False
                }
            )
            if created:
                salesman.set_password('salesman123')
                salesman.save()
        
        self.stdout.write(f'   ✓ Created/Updated {len(salesmen_data)} salesmen')

    def create_categories(self):
        """Create product categories"""
        categories_data = [
            'Electronics', 'Clothing', 'Food & Beverages', 'Books', 
            'Sports Equipment', 'Toys & Games', 'Furniture', 'Beauty & Health'
        ]
        
        for cat_name in categories_data:
            Category.objects.get_or_create(name=cat_name)
        
        self.stdout.write(f'   ✓ Created {Category.objects.count()} categories')

    def create_products(self):
        """Create products with inventory"""
        products_data = {
            'Electronics': [
                ('Smartphone X', 699.99, 50, 'Latest smartphone with 5G support'),
                ('Laptop Pro', 1299.99, 30, 'High-performance laptop for professionals'),
                ('Wireless Headphones', 199.99, 100, 'Noise-cancelling bluetooth headphones'),
                ('Smart Watch', 299.99, 75, 'Fitness tracking with heart rate monitor'),
                ('Tablet', 499.99, 45, '10-inch tablet with retina display'),
            ],
            'Clothing': [
                ("Men's T-Shirt", 19.99, 200, '100% cotton comfortable t-shirt'),
                ("Women's Jeans", 49.99, 150, 'Slim fit denim jeans'),
                ("Winter Jacket", 89.99, 75, 'Warm waterproof winter jacket'),
                ("Running Shoes", 79.99, 100, 'Lightweight athletic shoes'),
                ("Summer Dress", 39.99, 120, 'Floral pattern summer dress'),
            ],
            'Food & Beverages': [
                ('Coffee Beans (1kg)', 15.99, 300, 'Premium arabica coffee beans'),
                ('Green Tea (100 bags)', 9.99, 250, 'Organic green tea bags'),
                ('Potato Chips (200g)', 3.99, 500, 'Crunchy salted chips'),
                ('Chocolate Bar', 2.99, 400, 'Milk chocolate with almonds'),
                ('Orange Juice (1L)', 4.99, 200, 'Fresh squeezed orange juice'),
            ],
            'Books': [
                ('Python Programming Guide', 49.99, 80, 'Complete Python tutorial for beginners'),
                ('Django Web Development', 39.99, 60, 'Build web apps with Django'),
                ('Data Science Essentials', 59.99, 45, 'Introduction to data science'),
                ('Fiction Bestseller', 14.99, 150, 'Award-winning mystery novel'),
                ('Cookbook: Healthy Recipes', 24.99, 90, 'Quick and healthy meals'),
            ],
            'Sports Equipment': [
                ('Football', 29.99, 120, 'Official size soccer ball'),
                ('Basketball', 24.99, 100, 'Indoor/outdoor basketball'),
                ('Tennis Racket', 89.99, 50, 'Lightweight carbon fiber racket'),
                ('Yoga Mat', 19.99, 80, 'Non-slip exercise mat'),
                ('Dumbbell Set (5kg)', 49.99, 60, 'Adjustable dumbbell pair'),
            ],
            'Toys & Games': [
                ('LEGO Building Set', 49.99, 150, '500 piece creative building set'),
                ('Barbie Doll', 19.99, 200, 'Fashion doll with accessories'),
                ('Remote Control Car', 39.99, 100, 'High-speed RC car'),
                ('Board Game - Monopoly', 29.99, 80, 'Classic property trading game'),
                ('Stuffed Teddy Bear', 14.99, 120, 'Soft plush teddy bear'),
            ],
            'Furniture': [
                ('Office Chair', 149.99, 30, 'Ergonomic mesh office chair'),
                ('Desk Lamp LED', 29.99, 60, 'Adjustable brightness desk lamp'),
                ('Bookshelf', 89.99, 25, '5-tier wooden bookshelf'),
                ('Coffee Table', 199.99, 20, 'Modern glass coffee table'),
                ('Bed Frame Queen', 399.99, 15, 'Sturdy metal bed frame'),
            ],
            'Beauty & Health': [
                ('Shampoo', 12.99, 200, 'Moisturizing shampoo for all hair types'),
                ('Face Moisturizer', 24.99, 150, 'SPF 30 daily moisturizer'),
                ('Perfume Gift Set', 49.99, 80, 'Luxury fragrance set'),
                ('Makeup Kit', 39.99, 100, 'Complete makeup starter kit'),
                ('Hair Dryer', 34.99, 70, 'Ionic hair dryer with diffuser'),
            ]
        }
        
        for category_name, products in products_data.items():
            try:
                category = Category.objects.get(name=category_name)
                
                for name, price, qty, description in products:
                    product, created = Product.objects.get_or_create(
                        name=name,
                        category=category,
                        defaults={
                            'description': description,
                            'price': price
                        }
                    )
                    
                    if created:
                        Inventory.objects.create(
                            product=product,
                            quantity=qty,
                            last_updated=timezone.now()
                        )
                    else:
                        # Update existing inventory
                        inventory, inv_created = Inventory.objects.get_or_create(
                            product=product,
                            defaults={'quantity': qty, 'last_updated': timezone.now()}
                        )
                        if not inv_created:
                            inventory.quantity = qty
                            inventory.save()
            except Category.DoesNotExist:
                self.stdout.write(f'   Warning: Category "{category_name}" not found')
        
        self.stdout.write(f'   ✓ Created/Updated {Product.objects.count()} products with inventory')

    def create_bills(self):
        """Create bills/invoices for the last 90 days"""
        # Clear existing bills
        BillItem.objects.all().delete()
        Bill.objects.all().delete()
        
        salesmen = list(User.objects.filter(role='salesman'))
        if not salesmen:
            self.stdout.write('   Warning: No salesmen found, using all users')
            salesmen = list(User.objects.all())
        
        products = list(Product.objects.all())
        if not products:
            self.stdout.write('   No products found, skipping bill creation')
            return
        
        statuses = ['pending', 'paid', 'cancelled', 'refunded']
        bills_created = 0
        
        for day in range(90):
            date = timezone.now() - timedelta(days=day)
            # Generate 2-10 bills per day
            num_bills = random.randint(2, 10)
            
            for _ in range(num_bills):
                salesman = random.choice(salesmen)
                
                # Weighted status based on how old the bill is
                if day < 7:  # Recent bills (last week)
                    status = random.choices(statuses, weights=[0.4, 0.5, 0.05, 0.05])[0]
                elif day < 30:  # Medium age (1-4 weeks)
                    status = random.choices(statuses, weights=[0.2, 0.7, 0.05, 0.05])[0]
                else:  # Older bills (> 1 month)
                    status = random.choices(statuses, weights=[0.05, 0.85, 0.05, 0.05])[0]
                
                # Create bill
                bill = Bill.objects.create(
                    salesman=salesman,
                    created_at=date,
                    status=status,
                    total_amount=0,
                    assigned_to=None
                )
                
                # Add 1-8 items to bill
                num_items = random.randint(1, 8)
                selected_products = random.sample(products, min(num_items, len(products)))
                total = 0
                
                for product in selected_products:
                    quantity = random.randint(1, 5)
                    price = product.price
                    item_total = price * quantity
                    total += item_total
                    
                    BillItem.objects.create(
                        bill=bill,
                        product=product,
                        price=price,
                        quantity=quantity
                    )
                    
                    # Update inventory (deduct stock)
                    try:
                        inv = Inventory.objects.get(product=product)
                        if inv.quantity >= quantity:
                            inv.quantity -= quantity
                            inv.save()
                    except Inventory.DoesNotExist:
                        pass
                
                bill.total_amount = round(total, 2)
                bill.save()
                bills_created += 1
                
                if bills_created % 50 == 0:
                    self.stdout.write(f'      Created {bills_created} bills...')
        
        self.stdout.write(f'   ✓ Created {bills_created} bills with {BillItem.objects.count()} items')