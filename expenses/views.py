from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ExpenditureForm
from django.contrib.auth.decorators import login_required

@login_required
def add_expenditure(request):
    if request.method == 'POST':
        print("POST request received")
        print("Files received:", request.FILES)  # Debugging file uploads

        form = ExpenditureForm(request.POST, request.FILES)
        if form.is_valid():
            print("Form is valid")
            expenditure = form.save(commit=False)
            expenditure.added_by = request.user
            expenditure.save()
            
            print("Saved expenditure:", expenditure.receipt_attachment)  # Debugging file path

            messages.success(request, 'Expenditure added successfully!')
            return redirect('expenses:expense_list')
        else:
            print("Form errors:", form.errors)  # Debugging errors
            for field, error_list in form.errors.items():
                for error in error_list:
                    messages.error(request, f"{field.capitalize()}: {error}")

    else:
        form = ExpenditureForm()
        
    return render(request, 'expenses/add_expenditure.html', {'form': form})



from django.shortcuts import render
from django.db.models import Sum
from .models import Expenditure

def expense_list(request):
    expenditures = Expenditure.objects.all()  # Fetch all expenditures
    total_expenses = expenditures.aggregate(Sum('amount'))['amount__sum']  # Sum all amounts

    # Debugging: Print the total in the console
    print("Total Expenses:", total_expenses)

    return render(request, 'expenses/expense_list.html', {
        'expenditures': expenditures,
        'total_expenses': total_expenses or 0  # Ensure it defaults to 0 if None
    })




from django.http import FileResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Expenditure

def view_expenditure_receipt(request, expenditure_id):
    expenditure = get_object_or_404(Expenditure, id=expenditure_id)

    if not expenditure.receipt_attachment:
        messages.warning(request, "No receipt is available for this expenditure.")
        return redirect("expenses:expense_list")  # Redirect user to expense list

    try:
        return FileResponse(expenditure.receipt_attachment.open(), content_type="application/pdf")
    except FileNotFoundError:
        messages.error(request, "Receipt file not found on the server.")
        return redirect("expenses:expense_list")  # Redirect to avoid 404




def download_expenditure_receipt(request, expenditure_id):
    expenditure = get_object_or_404(Expenditure, id=expenditure_id)
    if expenditure.receipt_attachment:
        response = FileResponse(expenditure.receipt_attachment.open(), as_attachment=True)
        response['Content-Disposition'] = f'attachment; filename="{expenditure.receipt_attachment.name}"'
        return response
    return FileResponse(open('media/default.pdf', 'rb'), as_attachment=True)  # Default file

# expenses/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Expenditure
from .forms import ExpenditureForm


def edit_expenditure(request, pk):
    expenditure = get_object_or_404(Expenditure, pk=pk)
    
    if request.method == 'POST':
        form = ExpenditureForm(request.POST, request.FILES, instance=expenditure)
        if form.is_valid():
            form.save()
            messages.success(request, "Expenditure updated successfully!")
            return redirect('expenses:expense_list')
        else:
            messages.error(request, "Failed to update expenditure. Please check the form for errors.")

    else:
        form = ExpenditureForm(instance=expenditure)

    return render(request, 'expenses/edit_expenditure.html', {'form': form, 'expenditure': expenditure})

# expenses/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Expenditure

def delete_expenditure(request, pk):
    expenditure = get_object_or_404(Expenditure, pk=pk)
    if request.method == 'POST':
        expenditure.delete()
        return redirect('expenses:expense_list')  # Redirect to the list view after deletion
    return render(request, 'expenses/confirm_delete.html', {'expenditure': expenditure})




#==========================================================
# Views for Revenue generation

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum
from .models import Revenue
from .forms import RevenueForm

# View to list all revenue entries
def revenue_list(request):
    revenues = Revenue.objects.all()  # Fetch all revenue records
    total_revenue = revenues.aggregate(total=Sum('amount'))['total'] or 0  # Calculate total revenue
    return render(request, 'expenses/revenue_list.html', {'revenues': revenues, 'total_revenue': total_revenue})


from django.shortcuts import render, redirect
from .forms import RevenueForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import UserProfile

@login_required
def add_revenue(request):
    if request.method == 'POST':
        form = RevenueForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.added_by = request.user  # Assign logged-in user

            # Use the store selected in the form, if provided
            selected_store = form.cleaned_data.get('store')  

            if selected_store:
                form.instance.store = selected_store  # Save selected store
            else:
                try:
                    user_profile = UserProfile.objects.select_related('store').get(user=request.user)
                    if user_profile.store:
                        form.instance.store = user_profile.store  # Fallback to user's store
                    else:
                        messages.error(request, "Error: No store is assigned to your profile.")
                        return render(request, 'expenses/add_revenue.html', {'form': form})
                except UserProfile.DoesNotExist:
                    messages.error(request, "Error: Your profile is incomplete. Contact admin.")
                    return render(request, 'expenses/add_revenue.html', {'form': form})

            form.save()
            messages.success(request, "Revenue added successfully!")
            return redirect('expenses:revenue_list')

        else:
            messages.error(request, "Error: Please check the form fields.")

    else:
        form = RevenueForm()

    return render(request, 'expenses/add_revenue.html', {'form': form})





from django.shortcuts import render, get_object_or_404, redirect
from .models import Revenue
from .forms import RevenueForm

def edit_revenue(request, pk):
    revenue = get_object_or_404(Revenue, pk=pk)

    if request.method == 'POST':
        form = RevenueForm(request.POST, request.FILES, instance=revenue)
        if form.is_valid():
            form.save()
            messages.success(request, "Revenue entry updated successfully!")
            return redirect('expenses:revenue_list')
        else:
            messages.error(request, "Failed to update revenue entry. Please check the form for errors.")

    else:
        form = RevenueForm(instance=revenue)

    return render(request, 'expenses/edit_revenue.html', {'form': form, 'revenue': revenue})

# View to delete revenue entry
def delete_revenue(request, pk):
    revenue = get_object_or_404(Revenue, pk=pk)
    if request.method == 'POST':
        revenue.delete()
        return redirect('expenses:revenue_list')

    return render(request, 'expenses/delete_revenue.html', {'revenue': revenue})



# ===============================================
# Views for Revenue
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Revenue
from .forms import RevenueForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import UserProfile

@login_required
def view_receipt(request, revenue_id):
    revenue = get_object_or_404(Revenue, id=revenue_id)

    # Check if a receipt file is attached
    if not revenue.receipt_attachment:
        print("ERROR: No receipt file uploaded for this revenue record.")
        return render(request, "errors/404.html", status=404)  # Show a 404 page for missing receipts

    return render(request, "expenses/view_receipt.html", {"revenue": revenue})


from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
import os
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import Revenue

from django.http import HttpResponse
@login_required
def download_receipt(request, revenue_id):
    revenue = get_object_or_404(Revenue, id=revenue_id)

    # Ensure a receipt file exists
    if not revenue.receipt_attachment:
        return HttpResponse("No receipt attached to this revenue.", status=404)

    # Serve the file as an attachment
    file_path = revenue.receipt_attachment.path
    with open(file_path, 'rb') as file:
        response = HttpResponse(file.read(), content_type="application/octet-stream")
        response['Content-Disposition'] = f'attachment; filename="{revenue.receipt_attachment.name}"'
        return response

