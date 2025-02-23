from django.urls import path
from . import views

app_name = 'expenses'


urlpatterns = [
    # URLs for Expenses
    path('expenses/add/', views.add_expenditure, name='add_expenditure'),
    path('expenses/edit/<int:pk>/', views.edit_expenditure, name='edit_expenditure'),  
    path('expenses/list/', views.expense_list, name='expense_list'),
    path('expenses/delete/<int:pk>/', views.delete_expenditure, name='delete_expenditure'),  

    # Fix these URLs: Move them under expenses
    path('expenses/view-expenditure-receipt/<int:expenditure_id>/', views.view_expenditure_receipt, name='view_expenditure_receipt'),
    path('expenses/download-expenditure-receipt/<int:expenditure_id>/', views.download_expenditure_receipt, name='download_expenditure_receipt'),

    # URLs for Revenue (separated properly)
    path('revenue/list/', views.revenue_list, name='revenue_list'), 
    path('revenue/add/', views.add_revenue, name='add_revenue'),
    path("revenue/view-receipt/<int:revenue_id>/", views.view_receipt, name="view_receipt"),
    path("revenue/download-receipt/<int:revenue_id>/", views.download_receipt, name="download_receipt"),
    path("revenue/edit/<int:pk>/", views.edit_revenue, name="edit_revenue"),
    path("revenue/delete/<int:pk>/", views.delete_revenue, name="delete_revenue"),
]

