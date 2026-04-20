from django.shortcuts import render
from .models import Product, Category,Inventory
from sales.views import *

def product_list(request, return_data=False):
    query = request.GET.get('q')
    category_id = request.GET.get('category')

    products = Product.objects.all()
    categories = Category.objects.all()

    if query and query.strip():
        products = products.filter(name__icontains=query)

    if category_id and category_id.isdigit():
        products = products.filter(category_id=int(category_id))

    if return_data:
        return products, categories, query, category_id

    return render(request, 'salesman_dashboard.html', {
        'products': products,
        'categories': categories,
        'search_query': query,
        'selected_category': category_id,
    })


import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from django.http import HttpResponse
from django.shortcuts import render
from .models import InventoryLog
from io import BytesIO
import base64

def inventory_analytics(request):
    logs = InventoryLog.objects.all().values(
        'timestamp', 'quantity', 'transaction_type', 'source'
    )
    
    df = pd.DataFrame(logs)
    
    if df.empty:
        return HttpResponse("No data available")
    
    # 📅 Time processing
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date
    
    graphs = []
    
    # -------------------------------
    # 📈 1. TREND GRAPH
    # -------------------------------
    inflow = df[df['transaction_type'] == 'in'].groupby('date')['quantity'].sum()
    outflow = df[df['transaction_type'] == 'out'].groupby('date')['quantity'].sum()
    
    trend = pd.DataFrame({
        'Inflow': inflow,
        'Outflow': outflow
    }).fillna(0)
    
    plt.figure(figsize=(10, 6))
    trend.plot(marker='o')
    plt.title("Inflow vs Outflow Trend", fontsize=14)
    plt.xlabel("Date")
    plt.ylabel("Quantity")
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    graphs.append(save_plot_to_base64())
    
    # -------------------------------
    # 🧑‍💼 2. ADMIN vs SALES
    # -------------------------------
    source_data = df.groupby('source')['quantity'].sum()
    
    plt.figure(figsize=(8, 6))
    colors = ['#2ecc71', '#e74c3c', '#f39c12']
    source_data.plot(kind='bar', color=colors[:len(source_data)])
    plt.title("Admin vs Sales vs Returns", fontsize=14)
    plt.xlabel("Source")
    plt.ylabel("Quantity")
    plt.xticks(rotation=45)
    plt.tight_layout()
    graphs.append(save_plot_to_base64())
    
    # -------------------------------
    # 📊 3. DAILY BAR CHART
    # -------------------------------
    daily = df.groupby('date')['quantity'].sum()
    
    plt.figure(figsize=(12, 6))
    daily.plot(kind='bar', color='#3498db')
    plt.title("Daily Inventory Movement", fontsize=14)
    plt.xlabel("Date")
    plt.ylabel("Total Quantity")
    plt.xticks(rotation=45)
    plt.tight_layout()
    graphs.append(save_plot_to_base64())
    
    # -------------------------------
    # 🥧 4. PIE CHART
    # -------------------------------
    plt.figure(figsize=(8, 8))
    source_data.plot(kind='pie', autopct='%1.1f%%', startangle=90)
    plt.title("Distribution by Source", fontsize=14)
    plt.ylabel("")  # Remove y-label for better appearance
    plt.tight_layout()
    graphs.append(save_plot_to_base64())
    
    # -------------------------------
    # 📉 5. HISTOGRAM
    # -------------------------------
    plt.figure(figsize=(10, 6))
    df['quantity'].plot(kind='hist', bins=10, color='#9b59b6', edgecolor='black')
    plt.title("Quantity Distribution", fontsize=14)
    plt.xlabel("Quantity")
    plt.ylabel("Frequency")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    graphs.append(save_plot_to_base64())
    
    # -------------------------------
    # 📦 6. BOX PLOT
    # -------------------------------
    plt.figure(figsize=(8, 6))
    df.boxplot(column='quantity', grid=True)
    plt.title("Outlier Detection - Quantity Distribution", fontsize=14)
    plt.ylabel("Quantity")
    plt.tight_layout()
    graphs.append(save_plot_to_base64())
    
    # Add summary statistics
    summary = {
        'total_records': len(df),
        'total_inflow': inflow.sum(),
        'total_outflow': outflow.sum(),
        'net_change': inflow.sum() - outflow.sum(),
        'unique_dates': df['date'].nunique(),
        'by_source': source_data.to_dict()
    }
    
    return render(request, 'inventory_analytics.html', {
        'graphs': graphs,
        'summary': summary
    })

def save_plot_to_base64():
    """Save current matplotlib plot to base64 string"""
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()  # Close the figure to free memory
    return base64.b64encode(image_png).decode('utf-8')