from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from accounts.models import *
from inventory.views import *
from django.http import HttpResponse
from inventory.models import Inventory
from inventory.models import InventoryLog
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from reports.models import ReportException


redirect_url = "/sales/create/"


def create_bill(request):
    if request.method == "POST":
        product_id = request.POST.get('product')
        quantity = int(request.POST.get('quantity', 0))
        manager_id = request.POST.get('manager')
        bill_type = request.POST.get('bill_type')  # ✅ NEW

        if quantity <= 0:
            return HttpResponse("Quantity must be greater than 0")

        product = get_object_or_404(Product, id=product_id)
        manager = get_object_or_404(User, id=manager_id)
        inventory = get_object_or_404(Inventory, product=product)

        # ✅ ONLY check stock for SALE (NOT return)
        if bill_type == 'sale' and inventory.quantity < quantity:
            return HttpResponse(f"""
                <html>
                    <body>
                        <h2 style='color:red;'>Not enough stock</h2>
                        <p>Redirecting in 5 seconds...</p>
                        <script>
                            setTimeout(function() {{
                                window.location.href = "{redirect_url}";
                            }}, 5000);
                        </script>
                    </body>
                </html>
            """)

        bill = Bill.objects.create(
            salesman=request.user,
            assigned_to=manager,
            total_amount=product.price * quantity,
            status='pending',
            bill_type=bill_type   # ✅ IMPORTANT
        )

        BillItem.objects.create(
            bill=bill,
            product=product,
            quantity=quantity,
            price=product.price
        )

        return redirect('sales:bill_detail', bill_id=bill.id)

    managers = User.objects.filter(role='inventory')
    products = Product.objects.all()

    return render(request, 'create_bill.html', {
        'products': products,
        'managers': managers
    })

def manager_dashboard(request):
    bills = Bill.objects.filter(status='pending')

    products, categories, query, category_id = product_list(request, return_data=True)

    return render(request, 'manager_dashboard.html', {
        'bills': bills,
        'products': products,
        'categories': categories,
        'search_query': query,
        'selected_category': category_id,
    })

def bill_detail(request, bill_id):
    bill = Bill.objects.get(id=bill_id)
    return render(request, 'bill_detail.html', {'bill': bill})


# inventory manager views

def approve_bill(request, bill_id):
    bill = Bill.objects.get(id=bill_id)

    for item in bill.items.all():
        inventory = Inventory.objects.get(product=item.product)

        if bill.bill_type == 'sale':
            # 🔻 Decrease stock
            if inventory.quantity < item.quantity:
                bill.status = 'rejected'
                bill.save()
                return HttpResponse("Not enough stock")

            inventory.quantity -= item.quantity
            InventoryLog.objects.create(
                product=item.product,
                quantity=item.quantity,
                transaction_type='out',
                source='sale',
                user=request.user
            )

        elif bill.bill_type == 'return':
            # 🔺 Increase stock
            inventory.quantity += item.quantity
            InventoryLog.objects.create(
                product=item.product,
                quantity=item.quantity,
                transaction_type='in',
                source='return',
                user=request.user
            )

        inventory.save()

    bill.status = 'approved'
    bill.save()

    return redirect('sales:manager_dashboard')

def reject_bill(request, bill_id):
    bill = Bill.objects.get(id=bill_id)
    bill.status = 'rejected'
    bill.save()

    return redirect('sales:manager_dashboard')




# sales manager functions

def sales_manager_dashboard(request):
    today = timezone.now().date()

    # 📄 1. Bills generated today
    today_bills = Bill.objects.filter(created_at__date=today)
    total_bills = today_bills.count()

    # 💰 2. Total money transacted today (only approved bills)
    total_revenue = today_bills.filter(status='approved').aggregate(
        total=models.Sum('total_amount')
    )['total'] or 0

    # 🔄 3. Items returned today
    # (assuming you create ReturnBill or mark returns separately)
    returned_items = BillItem.objects.filter(
        bill__created_at__date=today,
        bill__status='approved',
        bill__bill_type='return'   # ⚠️ only if you added type field
    ).aggregate(
        total=models.Sum('quantity')
    )['total'] or 0
    products, categories, query, category_id = product_list(request, return_data=True)
    context = {
        'total_bills': total_bills,
        'total_revenue': total_revenue,
        'returned_items': returned_items,
        'products': products,
        'categories': categories,
        'search_query': query,
        'selected_category': category_id,
    }
    return render(request,'salesmanager_dashboard.html' ,context)


# exception handling 
from django.contrib.auth import get_user_model
User = get_user_model()




def report_exception(request):
    managers = User.objects.filter(role='sales_manager')  # adjust if needed

    if request.method == 'POST':
        text = request.POST.get('exception')
        manager_id = request.POST.get('manager')

        ReportException.objects.create(
            exception=text,
            salesman=request.user,
            assigned_to=User.objects.get(id=manager_id)
        )

        return redirect('dashboard')  # your existing logic

    return render(request, 'report_exception.html', {
        'managers': managers
    })


@login_required
def manager_exceptions(request):
    exceptions = ReportException.objects.filter(
        assigned_to=request.user
    ).order_by('-created_at')

    return render(request, 'manager_exceptions.html', {
        'exceptions': exceptions
    })