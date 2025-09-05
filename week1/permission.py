from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework import serializers, viewsets
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from django.urls import path, include
from rest_framework.routers import DefaultRouter

class User(AbstractUser):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Manager', 'Manager'),
        ('Cashier', 'Cashier'),
        ('Waiter', 'Waiter'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Waiter')

    def __str__(self):
        return f"{self.username} ({self.role})"

class MenuItem(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class IsManagerOrAdmin(BasePermission):
    """
    Only Managers or Admins can add/edit menu items.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ['Manager', 'Admin']
        )


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'name']


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsManagerOrAdmin()]
        return [IsAuthenticated()]


router = DefaultRouter()
router.register(r'menu', MenuItemViewSet, basename='menu')

urlpatterns = [
    path('', include(router.urls)),
]
