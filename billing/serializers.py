from rest_framework import serializers
from billing.models import TransactionInvoice

class TransactionInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionInvoice
        fields = '__all__'
