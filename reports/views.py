import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from django.shortcuts import render
from django.utils.timezone import make_aware
from datetime import datetime
from billing.models import TransactionInvoice
from store.models import Store
from reports.models import PriceHistory

def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct * total / 100.0))
        return f'{val}'
    return my_autopct


def generate_bar_chart(labels, values, title, xlabel="Category", ylabel="Amount"):
    values = [float(v) for v in values]  # ensure floats

    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(labels, values, color=['green' if v >= 0 else 'red' for v in values])

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    # Add value labels on top of bars
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax.annotate(
            f'{value:.2f}',
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),  # 3 points vertical offset
            textcoords="offset points",
            ha='center',
            va='bottom'
        )

    plt.xticks(rotation=45, ha='right')

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    image_png = buf.getvalue()
    buf.close()
    return base64.b64encode(image_png).decode('utf-8')


def profit_and_loss_view(request):
    store_id = request.GET.get('store')
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')

    invoices = TransactionInvoice.objects.select_related('product', 'store').all()

    selected_store = None

    if store_id is not None and store_id.isdigit():
        invoices = invoices.filter(product__store_id=store_id)
        selected_store = int(store_id)

    start_dt = None
    end_dt = None

    if start_date and end_date:
        try:
            start_dt = make_aware(datetime.strptime(start_date, "%Y-%m-%d"))
            end_dt = make_aware(datetime.strptime(end_date, "%Y-%m-%d"))
            if start_dt.date() == end_dt.date():
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
            invoices = invoices.filter(created_at__range=(start_dt, end_dt))
        except ValueError:
            pass

    # Get stores based on filtered invoices' product stores only
    stores = Store.objects.filter(id__in=invoices.values_list('product__store_id', flat=True).distinct())

    summary = {}
    for invoice in invoices:
        product = invoice.product
        store = invoice.product.store

        discount_value = product.selling_price * (product.discount / 100)
        selling_price_after_discount = product.selling_price - discount_value
        tax_value = selling_price_after_discount * (product.product_tax / 100)
        final_price = selling_price_after_discount + tax_value

        key = (product.id, store.id)
        if key not in summary:
            summary[key] = {
                'product_name': product.name,
                'store_name': store.name,
                'total_qty': 0,
                'total_revenue': 0,
                'unit_price': product.selling_price,
                'final_selling_price': final_price,
            }

        qty = invoice.quantity
        total_revenue = final_price * qty

        summary[key]['total_qty'] += qty
        summary[key]['total_revenue'] += total_revenue

    # Calculate unit cost and profit for each summary item
    for (product_id, store_id), item in summary.items():
        product_name = item['product_name']
        store_name = item['store_name']

        if start_dt:
            latest_price = PriceHistory.objects.filter(
                product__name=product_name,
                product__store__name=store_name,
                date_changed__lte=start_dt
            ).order_by('-date_changed').first()
        else:
            latest_price = None

        if latest_price:
            unit_cost = latest_price.new_cp
        else:
            invoice_instance = TransactionInvoice.objects.filter(
                product__name=product_name,
                product__store__name=store_name
            ).first()

            if invoice_instance and invoice_instance.product:
                unit_cost = invoice_instance.product.cost_price
            else:
                unit_cost = 0

        item['unit_cost'] = unit_cost
        item['total_cost'] = round(unit_cost * item['total_qty'], 2)
        item['total_profit'] = round(item['total_revenue'] - item['total_cost'], 2)

    total_revenue = sum(item['total_revenue'] for item in summary.values())
    total_cost = sum(item['total_cost'] for item in summary.values())
    total_profit = sum(item['total_profit'] for item in summary.values() if item['total_profit'] > 0)
    total_loss = sum(item['total_profit'] for item in summary.values() if item['total_profit'] < 0)


    # Prepare data for pie charts:
    # Profit by Store
    profit_by_store = {}
    for item in summary.values():
        store_name = item['store_name']
        profit_by_store[store_name] = profit_by_store.get(store_name, 0) + item['total_profit']

    # Remove negatives
    profit_by_store = {k: v for k, v in profit_by_store.items() if v > 0}

    # Profit by Product
    profit_by_product = {}
    for item in summary.values():
        product_name = item['product_name']
        profit_by_product[product_name] = profit_by_product.get(product_name, 0) + item['total_profit']

    profit_by_product = {k: v for k, v in profit_by_product.items() if v > 0}

    # Generate pie charts images in base64
    store_bar_chart = None   # ✅ always define a default
    if profit_by_store:
        store_bar_chart = generate_bar_chart(
        labels=list(profit_by_store.keys()),
        values=list(profit_by_store.values()),
        title="Profit/Loss by Store",
        xlabel="Store",
        ylabel="Profit / Loss"
    )


    product_bar_chart = None # ✅ always define a default
    if profit_by_product:
        product_bar_chart = generate_bar_chart(
        labels=list(profit_by_product.keys()),
        values=list(profit_by_product.values()),
        title="Profit/Loss by Product",
        xlabel="Product",
        ylabel="Profit / Loss"
    )

    context = {
        'invoices': list(summary.values()),
        'total_revenue': total_revenue,
        'total_cost': total_cost,
        'total_profit': total_profit,
        'total_loss': total_loss,  # ✅ ✅ ✅ You forgot this!
        'stores': stores,
        'selected_store': selected_store,
        'start_date': start_date,
        'end_date': end_date,
        'store_bar_chart': store_bar_chart,
        'product_bar_chart': product_bar_chart,

    }

    return render(request, 'reports/profit_and_loss.html', context)



#===========================================================
# reports/views.py



from django.db.models import Sum, F, FloatField, ExpressionWrapper
import openpyxl
from openpyxl.utils import get_column_letter
from django.http import HttpResponse
from billing.models import TransactionInvoice
from store.models import Store

def export_profit_loss_excel(request):
    def clean_param(value):
        return value if value and value != 'None' else None

    store_id = clean_param(request.GET.get('store'))
    start_date = clean_param(request.GET.get('start'))
    end_date = clean_param(request.GET.get('end'))

    txns = TransactionInvoice.objects.select_related('product', 'store', 'customer_invoice')

    if store_id:
        txns = txns.filter(product__store_id=store_id)
    if start_date:
        txns = txns.filter(created_at__date__gte=start_date)
    if end_date:
        txns = txns.filter(created_at__date__lte=end_date)


    # Annotate final selling price (price - discount per unit)
    txns = txns.annotate(
        final_price=ExpressionWrapper(
            F('price') - F('discount'),
            output_field=FloatField()
        ),
        total_cost=ExpressionWrapper(
            F('quantity') * F('product__cost_price'),
            output_field=FloatField()
        ),
        total_revenue=ExpressionWrapper(
            F('quantity') * (F('price') - F('discount')),
            output_field=FloatField()
        )
    )

    # Group by store & product
    summary = {}
    for txn in txns:
        key = (txn.store.name if txn.store else 'N/A', txn.product.name)
        if key not in summary:
            summary[key] = {
                'store': txn.store.name if txn.store else 'N/A',
                'product': txn.product.name,
                'quantity': 0,
                'unit_cost': float(txn.product.cost_price),
                'unit_price': float(txn.price),
                'final_price': float(txn.final_price),
                'total_cost': 0,
                'total_revenue': 0
            }

        summary[key]['quantity'] += txn.quantity
        summary[key]['total_cost'] += txn.quantity * float(txn.product.cost_price)
        summary[key]['total_revenue'] += txn.quantity * float(txn.final_price)

    # Create Excel workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Profit and Loss"

    # Compute grand totals
    total_cost = sum(item['total_cost'] for item in summary.values())
    total_revenue = sum(item['total_revenue'] for item in summary.values())
    total_profit = total_revenue - total_cost

    # Write summary at top
    ws.append([f"Total Revenue ₦: {total_revenue:.2f}"])
    ws.append([f"Total Cost ₦: {total_cost:.2f}"])
    ws.append([f"Profit ₦: {total_profit:.2f}"])
    ws.append([])  # empty row

    # Write table headers
    headers = [
        'S/NO.', 'Store', 'Product', 'Total Qty', 'Unit Cost', 'Unit Price',
        'Final Selling Price', 'Total Cost', 'Total Revenue', 'Total Profit'
    ]
    ws.append(headers)

    for idx, ((store, product), data) in enumerate(summary.items(), start=1):
        total_profit = data['total_revenue'] - data['total_cost']
        ws.append([
            idx,
            data['store'],
            data['product'],
            data['quantity'],
            f"{data['unit_cost']:.2f}",
            f"{data['unit_price']:.2f}",
            f"{data['final_price']:.2f}",
            f"{data['total_cost']:.2f}",
            f"{data['total_revenue']:.2f}",
            f"{total_profit:.2f}"
        ])

    # Auto-adjust column widths
    for col in ws.columns:
        max_len = max(len(str(cell.value)) if cell.value else 0 for cell in col)
        ws.column_dimensions[get_column_letter(col[0].column)].width = max_len + 2

    # Return response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = "profit_loss_summary.xlsx"
    response['Content-Disposition'] = f'attachment; filename={filename}'
    wb.save(response)
    return response



from django.shortcuts import render, redirect
from reports.models import PriceHistory
from reports.forms import PriceHistoryForm
from django.contrib.auth.decorators import login_required

@login_required
def price_history_view(request):
    history = PriceHistory.objects.select_related('product', 'changed_by').all().order_by('-date_changed')

    if request.method == 'POST':
        form = PriceHistoryForm(request.POST)
        if form.is_valid():
            price_history = form.save(commit=False)
            price_history.changed_by = request.user
            price_history.save()

            # Update Product prices here, after PriceHistory saved
            product = price_history.product
            if price_history.new_cp is not None:
                product.cost_price = price_history.new_cp
            if price_history.new_sp is not None:
                product.selling_price = price_history.new_sp
            product.save()

            return redirect('price_history')  # Replace with your URL name
    else:
        form = PriceHistoryForm()

    return render(request, 'reports/price_history.html', {
        'history': history,
        'form': form
    })


from django.http import JsonResponse
from store.models import Product  # Assuming your product model is here

def product_price_api(request):
    product_id = request.GET.get('product_id')
    data = {'old_cp': '', 'old_sp': ''}
    if product_id:
        try:
            product = Product.objects.get(id=product_id)
            # Assuming your Product model has fields for cost_price and selling_price
            data['old_cp'] = str(product.cost_price)  # or your actual cost price field name
            data['old_sp'] = str(product.selling_price)  # or your actual selling price field name
        except Product.DoesNotExist:
            pass
    return JsonResponse(data)
