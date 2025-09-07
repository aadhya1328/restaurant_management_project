# views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from restaurant.models import Dish
from restaurant.serializers import DishSerializer

class MenuListView(APIView):
    def get(self, request):
        dishes = Dish.objects.select_related('category').all()
        serialized_data = DishSerializer(dishes, many=True)
        return Response(serialized_data.data)
