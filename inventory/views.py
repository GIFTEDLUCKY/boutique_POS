from django.shortcuts import render, redirect
from django.contrib import messages
from store.models import StoreProduct
from .models import WarehouseStock
from .forms import WarehouseStockForm

def add_stock_to_warehouse(request):
    if request.method == "POST":
        form = WarehouseStockForm(request.POST)
        if form.is_valid():
            selected_product = form.cleaned_data["product"]
            quantity = form.cleaned_data["quantity"]

            try:
                # Fetch the master product ID from StoreProduct
                store_product = StoreProduct.objects.filter(product=selected_product).first()
                master_product = store_product.master_product if store_product else selected_product
            except StoreProduct.DoesNotExist:
                master_product = selected_product  # Fallback to original product

            # Check if stock exists for the master product
            stock_items = WarehouseStock.objects.filter(product=master_product)

            if stock_items.exists():
                stock_item = stock_items.first()
                stock_item.quantity += quantity
                stock_item.save()
                stock_items.exclude(id=stock_item.id).delete()
                messages.success(request, f"Stock for {master_product} updated successfully!")
            else:
                WarehouseStock.objects.create(product=master_product, quantity=quantity)
                messages.success(request, f"New stock for {master_product} added successfully!")

            return redirect("inventory:add_stock")

        else:
            messages.error(request, "Invalid input. Please correct the errors below.")

    else:
        form = WarehouseStockForm()

    stocks = WarehouseStock.objects.all()
    return render(request, "inventory/add_stock.html", {"form": form, "stocks": stocks})


from django.shortcuts import render, redirect, get_object_or_404
from .models import WarehouseStock
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages  # ✅ For success messages

def update_stock(request, stock_id):
    stock = get_object_or_404(WarehouseStock, id=stock_id)

    if request.method == 'POST':
        new_quantity = request.POST.get('quantity')

        if new_quantity and new_quantity.isdigit() and int(new_quantity) >= 0:
            stock.quantity = int(new_quantity)
            stock.save()
            messages.success(request, "Stock updated successfully!")
            return redirect('inventory:add_stock')  # ✅ Redirect after saving
        else:
            messages.error(request, "Invalid quantity entered.")

    return render(request, 'inventory/update_stock.html', {'stock': stock})

from .models import WarehouseStock  # Correct import


from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from .models import WarehouseStock

def delete_stock_confirmation(request, stock_id):
    stock = get_object_or_404(WarehouseStock, id=stock_id)

    if request.method == "POST":
        stock_name = stock.product.name  # Save name before deleting
        stock.delete()
        messages.success(request, f"Stock '{stock_name}' deleted successfully.")
        return redirect(reverse_lazy("inventory:add_stock"))  # Redirect after deletion

    return render(request, "inventory/delete_confirmation.html", {"stock": stock})




from django.shortcuts import get_object_or_404, redirect
from .models import WarehouseStock

def delete_stock(request, stock_id):
    stock = get_object_or_404(WarehouseStock, id=stock_id)

    # Check if the request method is POST
    if request.method == 'POST':
        stock.delete()  # Delete the stock record
        return redirect('inventory:add_stock')  # Redirect to the "Add Stock" page or your preferred page

    # If not POST (i.e., GET), just redirect to the "Add Stock" page
    return redirect('inventory:add_stock')


#================================================
# Views to hand stock transfer from warehouse to store
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction  # ✅ Prevents partial updates
from .models import StockTransfer, WarehouseStock, StoreProduct, Requisition
from .forms import StockTransferForm

import json  # ✅ For better formatting of printed data

def create_stock_transfer(request, requisition_id=None):
    """Handles stock transfers and ensures requisition is properly assigned."""

    # ✅ Ensure we get an approved requisition
    requisition = None
    if requisition_id:
        requisition = get_object_or_404(Requisition, id=requisition_id, status="Approved")

    if request.method == 'POST':
        print("\n🔹 Raw Form Data Received:", request.POST.dict())  # ✅ Print raw data
        
        form = StockTransferForm(request.POST)  

        if form.is_valid():
            transfer = form.save(commit=False)

            # ✅ Ensure requisition is explicitly assigned here
            if requisition:
                transfer.requisition = requisition  
            else:
                messages.error(request, "❌ ERROR: Requisition is required but not found!")
                return render(request, 'inventory/stock_transferForm.html', {'form': form})

            # ✅ Validate product selection
            product_id = request.POST.get("product")
            store_product = get_object_or_404(StoreProduct, id=product_id)
            transfer.product = store_product

            # ✅ Check warehouse stock availability
            warehouse_stock = WarehouseStock.objects.filter(product=store_product.product).first()
            if not warehouse_stock or warehouse_stock.quantity < transfer.quantity:
                messages.error(request, f"❌ Not enough stock for {store_product.product.name} in warehouse!")
                return render(request, 'inventory/stock_transferForm.html', {'form': form})

            # ✅ Deduct from warehouse stock
            warehouse_stock.quantity -= transfer.quantity
            warehouse_stock.save()

            # ✅ Update destination store stock
            destination_store_product, _ = StoreProduct.objects.get_or_create(
                product=store_product.product,
                store=transfer.destination_store,
                defaults={"quantity": 0}
            )
            destination_store_product.quantity += transfer.quantity
            destination_store_product.save()

            # ✅ Print cleaned data before saving
            cleaned_data = {
                "requisition": transfer.requisition,
                "product": transfer.product,
                "quantity": transfer.quantity,
                "destination_store": transfer.destination_store,
            }
            print("\n✅ Cleaned Form Data:", json.dumps(cleaned_data, default=str, indent=4))  # ✅ Print formatted data

            # ✅ Save the transfer after debugging output
            transfer.save()

            messages.success(request, f"✅ {transfer.quantity} {store_product.product.name}(s) transferred successfully!")
            return redirect('inventory:stock_transfer_table')

    else:
        form = StockTransferForm()

    return render(request, 'inventory/stock_transferForm.html', {'form': form, 'requisition': requisition})



#=================================================
# Movement for requisition
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Requisition, RequisitionItem
from .forms import RequisitionForm, RequisitionItemForm
from store.models import Store, Product  # Import Store model

@login_required
def create_requisition(request):
    if request.method == "POST":
        requisition_form = RequisitionForm(request.POST)
        if requisition_form.is_valid():
            requisition = requisition_form.save(commit=False)
            requisition.requested_by = request.user  # Store the user making the request
            requisition.save()

            # Handle multiple items
            products = request.POST.getlist('product')
            quantities = request.POST.getlist('quantity_requested')

            for product_id, qty in zip(products, quantities):
                product = Product.objects.get(id=product_id)
                RequisitionItem.objects.create(
                    requisition=requisition,
                    product=product,
                    quantity_requested=int(qty)
                )

            return redirect('inventory:requisition_list')

    else:
        requisition_form = RequisitionForm()
        requisition_form.fields['store'].queryset = Store.objects.all()  # Show all stores
        requisition_item_form = RequisitionItemForm()

    return render(request, 'inventory/requisition_form.html', {
        'requisition_form': requisition_form,
        'requisition_item_form': requisition_item_form
    })




from django.shortcuts import render
from .models import StockTransfer

def stockTransfer_table(request):
    stock_transfers = StockTransfer.objects.all()  # Get all stock transfers
    return render(request, 'inventory/stockTransfer_table.html', {'stock_transfers': stock_transfers})
