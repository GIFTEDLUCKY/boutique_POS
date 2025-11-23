from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from billing.models import TransactionInvoice
from billing.serializers import TransactionInvoiceSerializer

class SyncSalesAPIView(APIView):
    def post(self, request):
        """Receive offline sales from local system"""
        data = request.data.get("sales", [])
        saved = []
        for sale_data in data:
            serializer = TransactionInvoiceSerializer(data=sale_data)
            if serializer.is_valid():
                serializer.save()
                saved.append(serializer.data)
        return Response({"synced": saved}, status=status.HTTP_201_CREATED)

    def get(self, request):
        """Send updates from cloud to local (e.g. products, prices)"""
        invoices = TransactionInvoice.objects.all()
        serializer = TransactionInvoiceSerializer(invoices, many=True)
        return Response(serializer.data)
