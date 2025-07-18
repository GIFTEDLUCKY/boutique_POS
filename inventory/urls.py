from django.urls import path
from .views import add_stock_to_warehouse, update_stock, delete_stock_confirmation, delete_stock
from .views import create_stock_transfer, stockTransfer_table, create_requisition
from .views import requisition_details, requested_items_form, view_requisition

app_name = 'inventory'

urlpatterns = [
    path('add-stock/', add_stock_to_warehouse, name='add_stock'),
    path('update-stock/<int:stock_id>/', update_stock, name='update_stock'),
    path('delete-stock/<int:stock_id>/', delete_stock_confirmation, name='delete_stock_confirmation'),
    path('delete-stock/confirm/<int:stock_id>/', delete_stock, name='delete_stock'),


    path('stock-transfer-form/', create_stock_transfer, name='stock_transfer_form'),
    path('create-stock-transfer/', stockTransfer_table, name='stock_transfer_table'),
    path('requisition/new/', create_requisition, name='create_requisition'),

    path('requisition/form/', requested_items_form, name='requested_items_form'),  # ✅ Correct URL
    path('requisition/view/', view_requisition, name='view_requisition'),  # ✅ Correct URL
    path('requisition/<str:requisition_number>/', requisition_details, name='requisition_details'),
]
