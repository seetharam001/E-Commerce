from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions
from .models import Category
from .serializers import CategorySerializer

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]  # only logged-in users can access
