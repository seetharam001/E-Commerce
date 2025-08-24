from rest_framework import generics, permissions, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Category, Product, Cart, Order, CartItem
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    CartSerializer,
    OrderSerializer,
    CartItemSerializer,
    AddCartItemSerializer,
    PlaceOrderSerializer,
    DirectPlaceOrderSerializer,
)


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]  # only logged-in users can access


class ProductsByCategoryView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        return Product.objects.filter(category_id=category_id)


class UserCartView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart


class CartItemUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)


class UserOrdersListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class AddToCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data['product']
        variant = serializer.validated_data.get('variant', None)
        quantity = serializer.validated_data['quantity']

        cart, _ = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant
        )
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        variant_info = f" variant {variant.variant_name}" if variant else ""
        return Response(
            {"message": f"Added {quantity} of {product.name}{variant_info} to cart."},
            status=status.HTTP_200_OK,
        )


class PlaceOrderView(generics.CreateAPIView):
    serializer_class = PlaceOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}


class OrderAdminViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAdminUser]  # Only admins can access

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        status_value = request.data.get('status')
        if status_value not in dict(Order.STATUS_CHOICES):
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = status_value
        order.save()
        return Response(self.get_serializer(order).data)


class DirectPlaceOrderView(generics.CreateAPIView):
    serializer_class = DirectPlaceOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}


class OrderDeleteView(APIView):
    permission_classes = [IsAuthenticated]  # Or use IsAdminUser if only admins can delete

    def delete(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            # If you want only admins to delete any order, relax the user filter and add permission
        except Order.DoesNotExist:
            return Response({"detail": "Order not found or access denied"}, status=status.HTTP_404_NOT_FOUND)

        order.delete()
        return Response({"detail": "Order deleted successfully"}, status=status.HTTP_204_NO_CONTENT)