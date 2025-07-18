from django.urls import path
from . import views

urlpatterns = [
    path('profit-and-loss/', views.profit_and_loss_view, name='profit_and_loss'),
    path('price-history/', views.price_history_view, name='price_history'),

    path('profit-loss/export/', views.export_profit_loss_excel, name='export_profit_loss_excel'),

    path('product-price/', views.product_price_api, name='product_price_api'),
]
