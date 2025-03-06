from django.shortcuts import render, redirect, get_object_or_404
from .models import Invoice, InvoiceItem, Product
from .forms import InvoiceForm
from accounts.decorators import role_required
from store.models import StoreProduct
from django.contrib import messages
from django.utils import timezone
from billing.models import CustomerInvoice, TransactionInvoice
from store.models import Product, Store
from accounts.models import UserProfile
from .models import Cart, CartItem, TransactionInvoice, CustomerInvoice
from .utils import get_total_transaction_value
from io import BytesIO
import base64
from django.urls import reverse

from decimal import Decimal



import uuid
# Example of how cart_id might be set in the session
def cart_view(request):
    cart_id = request.session.get('cart_id')
    if not cart_id:
        cart_id = str(uuid.uuid4())  # Generate a new cart_id if not set
        request.session['cart_id'] = cart_id  # Store cart_id in session

    # Now you can use cart_id in your queries



def invoice_receipt(request, invoice_id):
    # Retrieve the cart_id from the session
    cart_id = request.session.get('cart_id')
    print(f"Cart ID from session: {cart_id}")  # Debugging output

    # If cart_id is not available, redirect back to the sales page
    if not cart_id:
        messages.error(request, "Cart ID not found")
        return redirect('billing:sales_view')

    # Fetch the invoice and transaction items
    customer_invoice = get_object_or_404(CustomerInvoice, id=invoice_id)
    cart_items = TransactionInvoice.objects.filter(cart_id=cart_id)

    if not cart_items.exists():
        messages.error(request, "No items found for this invoice!")
        return redirect('billing:sales_view')

    # Get the first transaction (assuming all have the same customer_name & payment_method)
    transaction = cart_items.first()
    payment_method_display = transaction.get_payment_method_display() if transaction else "N/A"

    # Calculate subtotal
    subtotal = sum(item.subtotal for item in cart_items)

    # Fetch tax rate and discount rate from TaxAndDiscount model
    tax_discount_settings = TaxAndDiscount.objects.first()
    tax_rate = tax_discount_settings.tax if tax_discount_settings else Decimal('0.00')
    discount_rate = tax_discount_settings.discount if tax_discount_settings else Decimal('0.00')

    # Calculate discount and tax
    discount = subtotal * discount_rate / Decimal('100')
    tax = (subtotal - discount) * tax_rate / Decimal('100')

    # Calculate total
    total = subtotal - discount + tax

    username = request.user.username
    store = transaction.store
    store_info = {
        'name': store.name,
        'location': store.location,
        'manager_name': store.manager,
    }

    # QR Code Logic
    invoice_url = request.build_absolute_uri(reverse('billing:invoice_receipt', args=[invoice_id]))

    # Create QR code with the full URL
    local_ip = "192.168.74.238"  # Replace with your actual local IP
    qr = qrcode.make(f"http://{local_ip}:8000/billing/invoice_receipt/{invoice_id}")

    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        # Context for the template
    context = {
        "username": username,
        "store_info": store_info,
        "customer_invoice": customer_invoice,
        "cart_items": cart_items,
        "transaction": transaction,
        "subtotal": subtotal.quantize(Decimal('0.01')),
        "discount": discount.quantize(Decimal('0.01')),
        "tax": tax.quantize(Decimal('0.01')),
        "total": total.quantize(Decimal('0.01')),
        "payment_method_display": payment_method_display,
        "qr_code_base64": qr_base64  # Add Base64 QR Code to template
    }

    return render(request, 'billing/invoice_receipt.html', context)



from django.http import JsonResponse
from .models import Invoice, InvoiceItem
from store.models import Product
import json
import random
import string

# Utility function to generate unique invoice number
def generate_invoice_number():
    return "INV" + ''.join(random.choices(string.digits, k=6))

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from store.models import Product
from billing.models import Invoice, InvoiceItem
from accounts.models import UserProfile
import json


@login_required
def sales_view(request):
    # Fetch the most recent customer invoice or create one if no invoices exist
    customer_invoice = CustomerInvoice.objects.last()  # Fetch the latest invoice

    # If no invoice exists, create a new one
    if not customer_invoice:
        customer_invoice = CustomerInvoice.objects.create(
            invoice_number=generate_invoice_number(),  # Use your custom function for generating invoice number
            customer_name="Default Customer",  # You can dynamically set this later
            total_amount=0.0,  # Initialize with default values
            discount=0.0,
            tax=0.0,
            final_total=0.0,
            user=request.user  # Make sure to link the invoice to the current logged-in user
        )

    invoice_id = customer_invoice.id  # Get the invoice_id from the most recent or newly created invoice

    # Access the role via UserProfile
    try:
        user_profile = request.user.userprofile  # Fetch the UserProfile related to the user
        role = user_profile.role  # Get the role
    except UserProfile.DoesNotExist:
        role = None  # Handle the case where UserProfile is not set up

    # Fetch products based on user's store (cashiers will only see their store's products)
    if role == 'cashier':
        cashier_store = user_profile.store  # Assuming UserProfile has a 'store' field
        print(f"Cashier's Store: {cashier_store}")  # Check the store for this cashier
        
        # Filter products by the cashier's store and status
        products = Product.objects.filter(store=cashier_store, status=1)  
        
    else:
        # If not a cashier, show all products or based on other conditions
        products = Product.objects.all()

    # Check for low stock in the products
    low_stock_products = [product for product in products if product.is_stock_low]

    # Handle POST request to process sales and generate invoice
    if request.method == 'POST':
        # Handle the logic when the form is submitted
        customer_name = request.POST.get('customer_name')
        cart_data = request.POST.get('cart_data')
        amount_paid = request.POST.get('amount_paid')
        discount = float(request.POST.get('discount', 0))
        tax = float(request.POST.get('tax', 0))
        payment_method = request.POST.get('payment_method')  # Get the payment method from the form

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

        # Create CustomerInvoice (use CustomerInvoice model)
        invoice = CustomerInvoice.objects.create(
            invoice_number=invoice_number,
            customer_name=customer_name,
            total_amount=total_amount,
            discount=discount,
            tax=tax,
            final_total=final_total,
            user=request.user  # Link the invoice to the current user (this should resolve the NULL user issue)
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

    # Render the sales page with the dynamic invoice_id, filtered products, and low_stock_products
    return render(request, 'billing/sales.html', {
        'invoice_id': invoice_id,
        'products': products,
        'low_stock_products': low_stock_products  # Pass low stock products to the template
    })



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

        # Save Customer Invoice
        customer_invoice = CustomerInvoice.objects.create(
            customer_name=customer_name,
            total_amount=final_total,
            discount=discount,
            tax=tax_amount,
            payment_status="Paid"  # Modify based on your payment status
        )

        # Update Stock and Create Transaction Invoices
        for item in cart_items:
            product = item['product']
            if product.quantity >= item['quantity']:
                product.quantity -= item['quantity']
                product.save()

                # ✅ Proportionally distribute tax based on the product's contribution to subtotal
                item_tax = (item['total_price'] / subtotal) * tax_amount if subtotal > 0 else 0

                # Create Transaction Invoice for each item
                TransactionInvoice.objects.create(
                    product=product,
                    quantity=item['quantity'],
                    price=item['total_price'],
                    invoice=customer_invoice,
                    tax=item_tax  # ✅ Save tax for each transaction
                )
            else:
                # Handle out-of-stock scenario
                return render(request, 'billing/sales.html', {
                    'error': 'Not enough stock for product: ' + product.name
                })

        # Redirect to the invoice receipt page
        return redirect('billing:invoice_receipt', invoice_id=customer_invoice.id)

    else:
        # Fetch available products for sale
        products = Product.objects.filter(status=True)  # Only active products
        return render(request, 'billing/sales.html', {'products': products})







from decimal import Decimal
import json
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from billing.models import CustomerInvoice, TransactionInvoice
from store.models import Product
#from account.models import UserProfile

def generate_invoice(request, invoice_id=None):
    cart_id = request.session.get('cart_id')
    print(f"Cart ID from session: {cart_id}")

    if not cart_id:
        messages.error(request, "No cart found for this session.")
        return redirect('billing:sales_view')

    
    customer_invoice = None
    if invoice_id:
        customer_invoice = get_object_or_404(CustomerInvoice, id=invoice_id)

    if request.method == 'POST':
        cart_data = request.POST.get('cart_data')
        customer_name = request.POST.get('customer_name', '') or "Customer"
        payment_method = request.POST.get('payment_method', 'Cash')

        if not cart_data:
            messages.error(request, "Cart is empty!")
            return redirect('billing:sales_view')

        try:
            cart = json.loads(cart_data)
        except json.JSONDecodeError as e:
            messages.error(request, f"Invalid cart data: {e}")
            return redirect('billing:sales_view')

        try:
            user_profile = UserProfile.objects.get(user=request.user)
            cashier_name = request.user.username
        except UserProfile.DoesNotExist:
            cashier_name = request.user.username

        if not customer_invoice:
            customer_invoice = CustomerInvoice.objects.create(
                invoice_number=cart_id,
                customer_name=customer_name,
                total_amount=0,
                created_at=timezone.now(),
                user=request.user,
                payment_method=payment_method,
            )

        total_amount = 0

        for item in cart:
            try:
                product = Product.objects.get(id=item['id'])
            except Product.DoesNotExist:
                messages.error(request, f"Product with ID {item['id']} not found!")
                return redirect('billing:sales_view')

            discounted_price = product.discounted_price
            quantity = item['quantity']
            subtotal = discounted_price * quantity

            # Calculate tax
            product_tax = product.product_tax or 0
            tax_amount = subtotal * (Decimal(product_tax) / Decimal('100'))

            # Calculate prorated discount (based on discount %)
            prorated_discount = (product.discount / 100) * (product.discounted_price * quantity)

            # Prorated tax after discount
            prorated_tax = (Decimal(product_tax) / Decimal(100)) * (subtotal - prorated_discount)

            # Adjusted final price
            adjusted_final_price = (subtotal - prorated_discount) + prorated_tax

            total_amount += adjusted_final_price

            # Save the TransactionInvoice with new fields
            TransactionInvoice.objects.create(
                customer_invoice=customer_invoice,
                product=product,
                quantity=quantity,
                price=discounted_price,
                discount=product.discount,
                subtotal=subtotal,
                tax=tax_amount,
                prorated_discount=prorated_discount,
                prorated_tax=prorated_tax,
                adjusted_final_price=adjusted_final_price,
                store=product.store,
                cart_id=cart_id,
                user=request.user,
                payment_method=payment_method,
                customer_name=customer_name
            )

        customer_invoice.total_amount = total_amount
        customer_invoice.save()
        qr_code_path = generate_qr_code(cart_id)

        # 
        return JsonResponse({
            'invoice_id': customer_invoice.id,
             'qr_code_path': qr_code_path  # ✅ Include QR code in response
          
        })

    return redirect('billing:sales_view')










from store.models import TaxAndDiscount

def calculate_total(cart):
    settings = TaxAndDiscount.objects.first()  # Fetch the global settings
    print(f"Tax: {settings.tax}, Discount: {settings.discount}")  # Debugging line
    subtotal = sum(item['price'] * item['quantity'] for item in cart)
    tax = subtotal * (settings.tax / 100) if settings else 0
    discount = subtotal * (settings.discount / 100) if settings else 0
    total = subtotal - discount + tax
    print(f"Subtotal: {subtotal}, Discount: {discount}, Tax: {tax}, Total: {total}")  # Debugging line
    return total





from django.shortcuts import render, redirect
from .models import CustomerInvoice

def create_invoice(request):
    if request.method == "POST":
        customer_name = request.POST.get("customer_name")
        total_amount = request.POST.get("total_amount")
        payment_method = request.POST.get("payment_method")
        tax = request.POST.get("tax")
        discount = request.POST.get("discount")

        invoice = CustomerInvoice.objects.create(
            customer_name=customer_name,
            total_amount=total_amount,
            user=request.user,
            payment_method=payment_method,
            tax=tax,
            discount=discount,
        )

        # Redirect to Invoice Receipt
        return redirect("billing:invoice_receipt", invoice_id=invoice.id)

    return render(request, "billing/create_invoice.html")


# Example view to add to cart and set cart_id
from django.shortcuts import render, redirect
from django.contrib.sessions.models import Session

def add_to_cart(request):
    # Retrieve the cart_id from the session or create a new cart if none exists
    cart_id = request.session.get('cart_id')
    if not cart_id:
        # Create a new cart for the current session and store the cart_id in the session
        cart = create_cart(request, store_id=request.user.store.id)  # Assuming create_cart() returns a Cart object
        request.session['cart_id'] = cart.id  # Store the cart's id in session
        request.session.modified = True  # Mark the session as modified
    
    else:
        # If cart_id already exists, retrieve the Cart object
        cart = Cart.objects.get(id=cart_id)
    
    # Get the product details from the request
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        messages.error(request, f"Product with ID {product_id} not found!")
        return redirect('billing:sales_view')

    # Calculate the subtotal for the product
    subtotal = product.price * quantity

    # Create a new transaction for the cart
    transaction = TransactionInvoice.objects.create(
        product=product,
        quantity=quantity,
        price=product.price,
        subtotal=subtotal,
        cart=cart,  # Link to the Cart instance
        customer_invoice_id=request.POST.get('customer_invoice_id'),
        store=request.user.store  # Directly link to the store object (not store_id)
    )

    messages.success(request, f"{product.name} added to cart successfully!")
    return redirect('billing:sales_view')


def generate_new_cart_id():
    # Generate a unique cart ID (for example, using UUID)
    import uuid
    return str(uuid.uuid4())

import uuid
# Example of how cart_id might be set in the session
def cart_view(request):
    cart_id = request.session.get('cart_id')
    if not cart_id:
        cart_id = str(uuid.uuid4())  # Generate a new cart_id if not set
        request.session['cart_id'] = cart_id  # Store cart_id in session

    # Now you can use cart_id in your queries

# billing/views.py

from .forms import CartForm
from .models import Cart

@login_required
def add_cart(request):
    if request.method == "POST":
        form = CartForm(request.POST)
        if form.is_valid():
            cart = form.save(commit=False)
            cart.user = request.user  # Assign the logged-in user
            cart.save()
            messages.success(request, "Cart added successfully!")
            return redirect('billing:add_cart')  # Adjust to your desired redirect
    else:
        form = CartForm()

    return render(request, 'billing/add_cart.html', {'form': form})


from django.utils import timezone
from .models import Cart

def create_cart(request, store_id):
    user = request.user  # Get the logged-in user (cashier)
    
    # Create a new cart
    cart = Cart.objects.create(
        created_at=timezone.now(),
        is_paid=False,  # Initial status of the cart
        store_id=store_id,
        user=user  # Associate the cart with the cashier
    )
    
    # Save the cart ID to the session
    request.session['cart_id'] = cart.id
    print(f"New cart created with ID: {cart.id} and saved in the session.")

    return cart.id  # Return cart_id

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Cart, Product

@csrf_exempt  # Add this decorator if you're using a non-CSRF-checked endpoint
@require_POST  # Ensure the view only accepts POST requests
def save_cart(request):
    try:
        cart_data = json.loads(request.body)  # Parse the JSON from the request
        cart = cart_data.get('cart')
        cart_id = cart_data.get('cart_id')

        # You can now process the cart data here, e.g., saving to the database
        if cart_id:
            cart_instance = Cart.objects.get(id=cart_id)
            # You can filter or process the cart items based on cart_id

            # Example of processing the cart (saving transaction, etc.)
            for item in cart:
                product = Product.objects.get(id=item['id'])
                # Add logic to handle saving items in the cart
                # ...

            return JsonResponse({'success': True, 'message': 'Cart saved successfully.'})

        return JsonResponse({'success': False, 'error': 'Cart ID missing.'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})



#=======================================================
# SAVING CREATED CART_ID FROM JAVASCRIPT
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def save_cart_id(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart_id = int(data.get('cart_id', 0))  # Ensure cart_id is converted to an integer
            request.session['cart_id'] = cart_id
            return JsonResponse({'message': 'Cart ID saved successfully!'})
        except (ValueError, TypeError) as e:
            return JsonResponse({'error': 'Invalid cart ID format.'}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


from django.shortcuts import render

def cart_view(request):
    cart_id = request.session.get('cart_id', None)
    return render(request, 'billing/cart_template.html', {'cart_id': cart_id})

import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def clear_cart(request):
    # Clear the cart and cart_id from the session
    request.session.pop('cart', None)  # Removes cart from session if it exists
    request.session.pop('cart_id', None)  # Removes cart_id from session if it exists
    
    # Generate a new cart_id and store it
    cart_id = str(random.randint(1000000000, 9999999999))  # New 10-digit cart_id
    request.session['cart_id'] = cart_id
    
    return JsonResponse({'status': 'success', 'message': 'Cart cleared and new cart ID generated.', 'cart_id': cart_id})


from django.shortcuts import render
from django.utils.timezone import now, timedelta
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from .models import TransactionInvoice
from datetime import datetime

from django.db.models import Sum


from django.http import JsonResponse
from django.template.loader import render_to_string


def all_transactions(request):
    # Get filter parameters from the GET request
    filter_field = request.GET.get('filter', None)
    filter_value = request.GET.get('filter_value', None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)

    # Start with the base queryset
    transactions = TransactionInvoice.objects.all()

    # Apply filters based on the GET parameters
    if filter_field and filter_value:
        if filter_field == 'payment_method':
            transactions = transactions.filter(payment_method=filter_value)
        elif filter_field == 'store':
            transactions = transactions.filter(store__name=filter_value)
        elif filter_field == 'invoice_number':
            transactions = transactions.filter(invoice_number=filter_value)
        elif filter_field == 'customer_name':
            transactions = transactions.filter(customer_name__icontains=filter_value)
        elif filter_field == 'cashier_name':  # ✅ Add this condition
            transactions = transactions.filter(user__username=filter_value)  

    # Apply date filters if provided
    if start_date:
        transactions = transactions.filter(created_at__gte=start_date)
    if end_date:
        transactions = transactions.filter(created_at__lte=end_date)

    # Calculate the total sales (sum of the subtotal field)
    total_sales = transactions.aggregate(Sum('subtotal'))['subtotal__sum'] or 0

    # Pagination: Show 10 transactions per page
    paginator = Paginator(transactions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Return the filtered and paginated data to the template
    return render(request, 'billing/transactions.html', {
        'transactions': page_obj,
        'total_sales': total_sales,
    })




from django.shortcuts import render
from django.db.models import Sum, Q
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from billing.models import TransactionInvoice
from store.models import TaxAndDiscount


def transactions_list(request):
    transactions = TransactionInvoice.objects.select_related('customer_invoice', 'product', 'store')

    # Calculate total sales
    total_sales = transactions.aggregate(Sum('subtotal'))['subtotal__sum'] or 0

    # Debugging: Print to console
    print(f"Total Sales Value: {total_sales}")

    # Fetch global tax and discount
    global_tax_discount = TaxAndDiscount.objects.first()  # Assuming only one global setting
    global_discount = global_tax_discount.discount if global_tax_discount else 0
    global_tax = global_tax_discount.tax if global_tax_discount else 0

    # Apply calculated values
    for transaction in transactions:
        product_discount = transaction.discount or 0
        product_tax = transaction.tax or 0

        # Total discount and tax (both global + product-specific)
        total_discount = product_discount + global_discount
        total_tax = product_tax + global_tax

        # Prorated values
        transaction.prorated_discount = (transaction.subtotal * total_discount) / 100
        transaction.prorated_tax = (transaction.subtotal * total_tax) / 100

        # Adjusted final price
        transaction.adjusted_final_price = transaction.subtotal - transaction.prorated_discount + transaction.prorated_tax

    # Filters and other query handling
    search_query = request.GET.get('search', '')
    filter_period = request.GET.get('filter', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    filter_field = request.GET.get('filter_field', '')
    filter_value = request.GET.get('filter_value', '')

    if search_query:
        transactions = transactions.filter(
            Q(store__name__icontains=search_query) |
            Q(customer_invoice__customer_name__icontains=search_query) |
            Q(product__name__icontains=search_query)
        )

    if filter_field and filter_value:
        if filter_field == 'store':
            transactions = transactions.filter(store__name__icontains=filter_value)
        elif filter_field == 'invoice_number':
            transactions = transactions.filter(customer_invoice__invoice_number__icontains=filter_value)
        elif filter_field == 'customer_name':
            transactions = transactions.filter(customer_invoice__customer_name__icontains=filter_value)
        elif filter_field == 'payment_method':
            transactions = transactions.filter(customer_invoice__payment_method__icontains=filter_value)

    if filter_period:
        today = datetime.today()
        if filter_period == 'day':
            transactions = transactions.filter(created_at__date=today.date())
        elif filter_period == 'week':
            start_of_week = today - timedelta(days=today.weekday())
            transactions = transactions.filter(created_at__date__gte=start_of_week)
        elif filter_period == 'month':
            transactions = transactions.filter(created_at__month=today.month)
        elif filter_period == 'year':
            transactions = transactions.filter(created_at__year=today.year)

    try:
        if start_date and end_date:
            start_date_parsed = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_parsed = datetime.strptime(end_date, '%Y-%m-%d').date()
            transactions = transactions.filter(created_at__date__range=[start_date_parsed, end_date_parsed])
    except ValueError:
        pass  # Ignore invalid date filters

    # **Fix pagination issue by ordering the queryset**
    transactions = transactions.order_by('-created_at')

    # Pagination
    paginator = Paginator(transactions, 10)
    page_number = request.GET.get('page')
    transactions_page = paginator.get_page(page_number)

    return render(request, 'billing:transactions_list.html', {
        'transactions': transactions_page,
        'total_value': total_sales,
    })



from django.http import JsonResponse
from django.utils.dateparse import parse_date
from django.db.models import Sum
from .models import TransactionInvoice
import logging

# Set up a logger to log any issues in the view
logger = logging.getLogger(__name__)

def filter_transactions(request):
    try:
        # Get filter parameters
        filter_field = request.GET.get('filter_field')
        filter_value = request.GET.get('filter_value')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        # Start with all transactions
        transactions = TransactionInvoice.objects.all()

        # Apply date range filter if provided
        if start_date and end_date:
            start_date = parse_date(start_date)
            end_date = parse_date(end_date)
            if start_date and end_date:
                transactions = transactions.filter(created_at__date__range=[start_date, end_date])

        # Apply field-based filtering
        if filter_field and filter_value:
            filter_criteria = {}
            if filter_field == 'store':
                filter_criteria = {'store__name__icontains': filter_value}
            elif filter_field == 'invoice_number':  
                filter_criteria = {'cart_id__icontains': filter_value}  
            elif filter_field == 'customer_name':
                filter_criteria = {'customer_name__icontains': filter_value}
            elif filter_field == 'payment_method':
                filter_criteria = {'payment_method__icontains': filter_value}
            elif filter_field == 'cashier_name':
                filter_criteria = {'user__username__icontains': filter_value}

            transactions = transactions.filter(**filter_criteria)

        subtotal_sum = transactions.aggregate(Sum('subtotal'))['subtotal__sum'] or 0
        tax_sum = transactions.aggregate(Sum('tax'))['tax__sum'] or 0
        total_sales = subtotal_sum + tax_sum

        # Serialize transactions with 'Invoice Number' instead of 'cart_id'
        transaction_data = [
            {
                'cashier_name': transaction.user.username if transaction.user else 'Unknown',
                'cart_id': transaction.cart_id,  
                'customer_name': transaction.customer_name,
                'payment_method': transaction.payment_method,
                'product_name': transaction.product.name,
                'store_name': transaction.store.name,
                'quantity': transaction.quantity,
                'price': transaction.price,
                'discount': transaction.discount,
                'tax': transaction.tax if transaction.tax is not None else 0.00,
                'subtotal': transaction.subtotal,
                'prorated_discount': transaction.prorated_discount if hasattr(transaction, 'prorated_discount') else 0.00,
                'prorated_tax': transaction.prorated_tax if hasattr(transaction, 'prorated_tax') else 0.00,
                'adjusted_final_price': transaction.adjusted_final_price if hasattr(transaction, 'adjusted_final_price') else 0.00,
                'created_at': transaction.created_at.strftime('%d-%m-%Y') if transaction.created_at else 'N/A',
            }
            for transaction in transactions
        ]


        return JsonResponse({'transactions': transaction_data, 'total_sales': total_sales})

    except Exception as e:
        logger.error(f"Error in filter_transactions view: {str(e)}")
        return JsonResponse({'error': 'Internal Server Error'}, status=500)




from django.shortcuts import render
from .utils import get_total_transaction_value

def total_transaction_value(request):
    total_value = get_total_transaction_value()
    return render(request, 'billing/transaction_value.html', {'total_value': total_value})


#=====================================================
#  Working on refund



# Set up logging
import logging
from django.http import JsonResponse
from django.shortcuts import render
from .models import TransactionInvoice, CustomerInvoice, Product


def transaction_search(request):
    if request.method == "GET":
        bill_number = request.GET.get('bill_number')
        if bill_number:
            transactions = TransactionInvoice.objects.filter(cart_id__startswith=bill_number)
            if not transactions.exists():
                return JsonResponse({"error": "No transactions found for this bill number."}, status=404)

            cart_items = [
                {
                    "transaction_id": transaction.id,
                    "name": transaction.product.name,
                    "quantity": transaction.quantity,
                    "price": transaction.price,
                    "subtotal": transaction.subtotal,
                }
                for transaction in transactions
            ]
            return JsonResponse({"cart_items": cart_items})

        return render(request, 'billing/transaction_search.html')





# views.py

import qrcode
from io import BytesIO
import base64
from django.shortcuts import render
from .models import TransactionInvoice
import json

def re_print_invoice(request):
    if request.method == "POST":
        data = json.loads(request.body)
        cart_id = data.get('cart_id')
        print(f"Received cart_id: {cart_id}")  # Debug

        if cart_id:
            transactions = TransactionInvoice.objects.filter(cart_id=cart_id)
            print(f"Transactions found: {transactions.count()}")  # Debug

            if transactions.exists():
                subtotal = sum(item.subtotal for item in transactions)
                discount = sum(item.discount for item in transactions)
                tax = sum(item.tax for item in transactions) 
                total = subtotal - discount + tax

                # Generate QR code as done in the invoice_receipt view
                invoice_url = request.build_absolute_uri(reverse('billing:re_print_invoice'))
                local_ip = "192.168.74.238"  # Replace with your actual local IP
                qr = qrcode.make(f"http://{local_ip}:8000/billing/re_print_invoice/{cart_id}")

                buffer = BytesIO()
                qr.save(buffer, format="PNG")
                qr_base64 = base64.b64encode(buffer.getvalue()).decode()

                return render(request, 'billing/re_print_invoice.html', {
                    'cart_items': transactions,
                    'subtotal': subtotal,
                    'discount': discount,
                    'tax': tax,
                    'total': total,
                    'qr_code_base64': qr_base64,  # Pass the QR code to the template
                })
            else:
                return render(request, 'billing/re_print_invoice.html', {'error': 'No transactions found.'})
    return render(request, 'billing/re_print_invoice.html', {'error': 'No cart ID provided.'})



from django.shortcuts import render, redirect

def reset_sales_page(request):
    # Clear cart session
    if 'cart' in request.session:
        del request.session['cart']
    request.session.modified = True

    # Redirect to the sales page
    return redirect('billing:sales_view')  # Ensure 'sales' is the name of your URL pattern for sales.html


import qrcode
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from .models import TransactionInvoice
import os


def generate_qr_code(cart_id):
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)  # Ensure media folder exists

    file_name = f"qr_code_{cart_id}.png"
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)

    # Generate and save the QR code
    qr = qrcode.make(cart_id)
    qr.save(file_path)

    # Debugging: Check if file exists
    if os.path.exists(file_path):
        print(f"✅ QR Code successfully created: {file_path}")
        return file_name  # Return only file name, not full path
    else:
        print("❌ Failed to create QR Code!")
        return ""  # Return empty string to avoid issues

def transaction_receipt(request, transaction_id):
    from django.utils.safestring import mark_safe  # For safe URL handling

    # Get the transaction data
    transaction = get_object_or_404(TransactionInvoice, id=transaction_id)

    # Generate the QR code for this transaction
    cart_id = transaction.cart_id
    qr_code_file = generate_qr_code(cart_id)

    # Construct the correct URL for the QR code
    qr_code_url = settings.MEDIA_URL + os.path.basename(qr_code_file) if qr_code_file else ""

    # Debugging: Print values in terminal
    print(f"Transaction ID: {transaction_id}")
    print(f"Cart ID: {cart_id}")
    print(f"QR Code File Path: {qr_code_file}")
    print(f"Generated QR Code URL: {qr_code_url}")

    # Pass the QR code URL to the template
    return render(request, 'billing/invoice_receipt.html', {
        'transaction': transaction,
        'qr_code_url': mark_safe(qr_code_url),  # Prevent escaping of URL
        'media_url': settings.MEDIA_URL
    })
