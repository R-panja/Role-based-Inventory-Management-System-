from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from inventory.models import Inventory
from datetime import datetime


def generate_inventory_report(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="inventory_report.pdf"'

    doc = SimpleDocTemplate(response)
    elements = []

    styles = getSampleStyleSheet()

    # 🕒 Timestamp
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    elements.append(Paragraph("Inventory Report", styles['Title']))
    elements.append(Paragraph(f"Generated on: {now}", styles['Normal']))

    # 📊 Table Data
    data = [['Product', 'Category', 'Price', 'Quantity']]
    total_value = 0
    inventory_items = Inventory.objects.select_related('product__category').order_by('-product__price')
    
    for item in inventory_items:
        data.append([
            item.product.name,
            item.product.category.name,
            f"Rs {item.product.price}",
            item.quantity
        ])

        total_value += item.product.price * item.quantity

    # 📋 Table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))

    elements.append(table)
    elements.append(Paragraph(f"Total Inventory Value: Rs {total_value}", styles['Heading2']))
    doc.build(elements)

    return response