from django.shortcuts import render, redirect, get_object_or_404
from .models import Invoice, InvoiceItem, Product
from .forms import InvoiceForm
from accounts.decorators import role_required

def billing_page(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            # Generate invoice number (you could use a more complex logic here)
            invoice_number = "INV" + str(Invoice.objects.count() + 1)
            invoice = form.save(commit=False)
            invoice.invoice_number = invoice_number
            invoice.save()

            # Process invoice items (add products to invoice)
            product_ids = request.POST.getlist('product_ids')  # Get selected product IDs
            quantities = request.POST.getlist('quantities')  # Get quantities for the selected products
            for i, product_id in enumerate(product_ids):
                product = Product.objects.get(id=product_id)
                invoice_item = InvoiceItem(invoice=invoice, product=product, quantity=quantities[i], price=product.price)
                invoice_item.save()

            # Calculate the final total with tax and discount
            invoice.final_total = invoice.total_amount + invoice.tax - invoice.discount
            invoice.save()

            return redirect('store:invoice_receipt', invoice_id=invoice.id)
    else:
        form = InvoiceForm()

    products = Product.objects.all()
    context = {
        'form': form,
        'products': products
    }
    return render(request, 'store/billing_page.html', context)


from django.shortcuts import render, get_object_or_404
from billing.models import CustomerInvoice, TransactionInvoice

from decimal import Decimal

def invoice_receipt(request, invoice_id):
    # Retrieve the customer invoice
    customer_invoice = get_object_or_404(CustomerInvoice, id=invoice_id)
    
    # Retrieve all transaction items linked to this invoice
    transaction_items = TransactionInvoice.objects.filter(customer_invoice=customer_invoice)

    # Calculate the subtotal, discount, and tax
    subtotal = sum(item.subtotal for item in transaction_items)
    discount = sum((item.subtotal * Decimal(item.discount) / 100) for item in transaction_items)
    tax_rate = Decimal('0.1')  # Example: 10% tax as a Decimal
    tax = subtotal * tax_rate

    # Calculate the final total
    total = subtotal - discount + tax

    # Example store info (Replace with actual data from your Store model)
    store_info = {
        "name": "My Store",
        "address": "123 Main Street, City",
        "contact": "+1234567890"
    }

    # Pass all the data to the template
    context = {
        "store_info": store_info,
        "customer_invoice": customer_invoice,
        "transaction_items": transaction_items,
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": total,
    }

    return render(request, "billing/invoice_receipt.html", context)


from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Invoice, InvoiceItem
from store.models import Product
import json
import random
import string

# Utility function to generate unique invoice number
def generate_invoice_number():
    return "INV" + ''.join(random.choices(string.digits, k=6))

# @role_required(['cashier', 'staff'])
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Product, Invoice, InvoiceItem
import json

from django.shortcuts import render, redirect
from .models import Product, Invoice, InvoiceItem
from django.utils import timezone
import json

def sales_view(request):
    # Fetch the most recent invoice or create one if no invoices exist
    customer_invoice = Invoice.objects.last()  # Fetch the latest invoice
    
    # If no invoice exists, create a new one
    if not customer_invoice:
        customer_invoice = Invoice.objects.create(
            invoice_number=generate_invoice_number(),  # Use your custom function for generating invoice number
            customer_name="Default Customer",  # You can dynamically set this later
            total_amount=0.0,  # Initialize with default values
            discount=0.0,
            tax=0.0,
            final_total=0.0,
        )
    
    invoice_id = customer_invoice.id  # Get the invoice_id from the most recent or newly created invoice
    
    # Fetch all products for the page
    products = Product.objects.all()

    if request.method == 'POST':
        # Handle the logic when the form is submitted
        customer_name = request.POST.get('customer_name')
        cart_data = request.POST.get('cart_data')
        amount_paid = request.POST.get('amount_paid')
        discount = float(request.POST.get('discount', 0))
        tax = float(request.POST.get('tax', 0))

        # Parse cart data from the hidden input using JSON
        try:
            cart = json.loads(cart_data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid cart data format.'}, status=400)

        # Calculate total amount and final total after discount and tax
        total_amount = sum(item['price'] * item['quantity'] * (1 - item['discount'] / 100) for item in cart)
        final_total = total_amount + (total_amount * tax / 100) - discount

        # Generate unique invoice number (you can implement a custom logic for this)
        invoice_number = generate_invoice_number()

        # Create Invoice
        invoice = Invoice.objects.create(
            invoice_number=invoice_number,
            customer_name=customer_name,
            total_amount=total_amount,
            discount=discount,
            tax=tax,
            final_total=final_total
        )

        # Create Invoice Items (products in the cart)
        for item in cart:
            product = Product.objects.get(id=item['id'])
            InvoiceItem.objects.create(
                invoice=invoice,
                product=product,
                quantity=item['quantity'],
                price=item['price'],
                total_price=item['price'] * item['quantity'] * (1 - item['discount'] / 100)
            )

        # After creating the invoice, redirect to the invoice detail page
        return redirect('billing:generate_invoice', invoice_id=invoice.id)

    # Render the sales page with the dynamic invoice_id and list of products
    return render(request, 'billing/sales.html', {'invoice_id': invoice_id, 'products': products})


from .models import CustomerInvoice

def invoice_success(request):
    # You can query the last created invoice or whatever logic you need
    invoice = CustomerInvoice.objects.last()  # Example logic
    return render(request, 'store/invoice_success.html', {'invoice': invoice})


def create_invoice(request):
    # Add your logic for creating an invoice here
    return render(request, 'billing/create_invoice.html')

# billing/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Cart

def edit_quantity(request, cart_item_id):
    cart_item = get_object_or_404(Cart, id=cart_item_id)

    if request.method == 'POST':
        new_quantity = request.POST.get('quantity')

        # Validate the new quantity
        if new_quantity and int(new_quantity) > 0:
            cart_item.quantity = int(new_quantity)
            cart_item.save()
            return redirect('billing:sales')  # Redirect to the sales page after update

    return render(request, 'billing/edit_quantity.html', {
        'cart_item': cart_item,
    })

from django.http import JsonResponse
from .models import Cart


from django.http import JsonResponse
from .models import Cart
def delete_item(request, cart_item_id):
    print(f"Attempting to delete cart item with ID: {cart_item_id}")  # Log this to see if it's reached
    try:
        cart_item = Cart.objects.get(id=cart_item_id)
        cart_item.delete()

        # Optionally, update session data
        cart = request.session.get('cart', [])
        cart = [item for item in cart if item['id'] != cart_item_id]  # Remove item from session
        request.session['cart'] = cart

        return JsonResponse({'success': True})
    except Cart.DoesNotExist:
        print(f"Cart item with ID {cart_item_id} not found.")  # Log if not found
        return JsonResponse({'error': 'Cart item not found.'}, status=404)


from django.contrib.auth.decorators import login_required
from billing.models import TransactionInvoice

@login_required
def store_transactions(request):
    # Ensure that the user has a store associated with them (Either via profile or othe menas)
    store = request.user.store
    # Filter transactions based on the user's assigned store
    transactions = TransactionInvoice.objects.filter(store=store)
    return render(request, 'billing/transactions.html', {'transactions': transactions})


# billing/views.py (or where you're processing the sale)

from .models import TransactionInvoice
from store.models import Product  # Assuming this is the model tracking store products

from store.models import Product  # This is your Product model

def update_stock_after_sale(product_id, quantity_sold):
    try:
        # Fetch the product from the store
        product = Product.objects.get(id=product_id)

        # Reduce the stock by the quantity sold
        if product.quantity >= quantity_sold:
            product.quantity -= quantity_sold
            product.save()
        else:
            raise ValueError("Not enough stock available")
    except Product.DoesNotExist:
        raise ValueError("Product not found in the store")


# View for processing the sale (simplified)
# billing/views.py

from django.shortcuts import render, redirect
from .models import Product, TransactionInvoice, CustomerInvoice
from django.contrib.auth.decorators import login_required

@login_required
def process_sale(request):
    if request.method == "POST":
        customer_name = request.POST.get('customer_name')
        product_ids = request.POST.getlist('product_ids')
        quantities = request.POST.getlist('quantities')
        discount = float(request.POST.get('discount', 0))
        tax = float(request.POST.get('tax', 0))
        amount_paid = float(request.POST.get('amount_paid', 0))

        # Calculate final total
        subtotal = 0
        cart_items = []
        for product_id, quantity in zip(product_ids, quantities):
            product = Product.objects.get(id=product_id)
            quantity = int(quantity)
            total_price = product.selling_price * quantity
            discounted_price = total_price - (total_price * discount / 100)
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total_price': discounted_price
            })
            subtotal += discounted_price
        
        # Calculate Tax and Final Total
        tax_amount = subtotal * (tax / 100)
        final_total = subtotal + tax_amount

        # Save Transaction Invoice
        customer_invoice = CustomerInvoice.objects.create(
            customer_name=customer_name, 
            total_amount=final_total, 
            discount=discount, 
            tax=tax_amount,
            payment_status="Paid"  # Example, modify based on your payment status
        )

        # Update Stock and Create Transaction Invoices
        for item in cart_items:
            product = item['product']
            if product.quantity >= item['quantity']:
                product.quantity -= item['quantity']
                product.save()
                
                # Create Transaction Invoice for each item
                TransactionInvoice.objects.create(
                    product=product,
                    quantity=item['quantity'],
                    price=item['total_price'],
                    invoice=customer_invoice
                )
            else:
                # Handle out-of-stock or insufficient stock scenario
                return render(request, 'billing/sales.html', {'error': 'Not enough stock for product: ' + product.name})

        # Redirect to the invoice receipt page
        return redirect('billing:invoice_receipt', invoice_id=customer_invoice.id)

    else:
        # Fetch available products for sale
        products = Product.objects.filter(status=True)  # Only active products
        return render(request, 'billing/sales.html', {'products': products})


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from store.models import Product
from .models import CustomerInvoice, TransactionInvoice

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from billing.models import CustomerInvoice, TransactionInvoice
from store.models import Product  # Assuming Product is in the store app


def generate_invoice(request, invoice_id=None):
    # Retrieve the existing invoice if provided, otherwise start with None
    customer_invoice = None
    if invoice_id:
        customer_invoice = get_object_or_404(CustomerInvoice, id=invoice_id)

    if request.method == 'POST':
        cart_data = request.POST.get('cart_data')
        customer_name = request.POST.get('customer_name', '')  # Optional
        tax = float(request.POST.get('tax', 0))  # Defaults to 0 if not provided
        discount = float(request.POST.get('discount', 0))  # Defaults to 0 if not provided
        payment_method = request.POST.get('payment_method', 'Cash')  # Default to 'Cash'

        # Ensure cart data is provided
        if not cart_data:
            messages.error(request, "Cart is empty!")
            return redirect('billing:sales_view')

        try:
            # Safely evaluate the cart data
            cart = eval(cart_data) if isinstance(cart_data, str) else cart_data
        except Exception as e:
            messages.error(request, f"Invalid cart data: {e}")
            return redirect('billing:sales_view')

        # Calculate the total amount and final total
        try:
            total_amount = sum(
                item['price'] * item['quantity'] * (1 - item.get('discount', 0) / 100) 
                for item in cart
            )
            final_total = total_amount + (total_amount * tax / 100) - discount
        except KeyError as e:
            messages.error(request, f"Missing key in cart data: {e}")
            return redirect('billing:sales_view')

        # If no existing invoice, create a new one
        if not customer_invoice:
            customer_invoice = CustomerInvoice.objects.create(
                invoice_number=f"INV{timezone.now().strftime('%Y%m%d%H%M%S')}",  # Unique invoice number
                customer_name=customer_name,  # Optional
                total_amount=total_amount,
                created_at=timezone.now(),
                user=request.user,
            )

        # Create transaction records for each item in the cart
        for item in cart:
            try:
                product = Product.objects.get(id=item['id'])  # Fetch product by ID
            except Product.DoesNotExist:
                messages.error(request, f"Product with ID {item['id']} not found!")
                return redirect('billing:sales_view')

            TransactionInvoice.objects.create(
                customer_invoice=customer_invoice,
                product=product,
                quantity=item['quantity'],
                price=item['price'],
                discount=item.get('discount', 0),  # Default to 0 if no discount
                subtotal=item['price'] * item['quantity'] * (1 - item.get('discount', 0) / 100),
                store=product.store  # Ensure the Product model has a store field
            )

        # Redirect to the invoice receipt view
        return redirect('billing:invoice_receipt', invoice_id=customer_invoice.id)

    # If it's not a POST request, redirect to the sales view
    return redirect('billing:sales_view')




def calculate_total(cart):
    subtotal = sum(item['price'] * item['quantity'] for item in cart)
    discount = sum(item.get('discount', 0) for item in cart)
    tax = subtotal * 0.1  # Example 10% tax calculation
    total = subtotal - discount + tax
    return total
