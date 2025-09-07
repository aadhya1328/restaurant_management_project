# views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from orders.models import Order
from orders.serializers import OrderSerializer

class UpdateOrderStatusView(APIView):
    ALLOWED_TRANSITIONS = {
        'Pending': ['Preparing'],
        'Preparing': ['Ready'],
        'Ready': ['Served'],
        'Served': []
    }

    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found.'}, status=404)

        new_status = request.data.get('status')
        current_status = order.status

        if new_status not in self.ALLOWED_TRANSITIONS.get(current_status, []):
            return Response({'error': f'Invalid status transition from {current_status} to {new_status}.'}, status=400)

        order.status = new_status
        order.save()
        return Response(OrderSerializer(order).data, status=200)
