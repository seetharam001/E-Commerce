from rest_framework import serializers
from .models import Category, Product, Variant, Review, Cart, CartItem, Order, OrderItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'image']

class VariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = ['id', 'variant_name', 'price', 'stock']

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'comment', 'created_at']

class ProductSerializer(serializers.ModelSerializer):
    variants = VariantSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'category', 'category_name', 'name', 'description', 'image', 'price', 'variants', 'reviews']

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    variant = VariantSerializer(read_only=True)  # Nested variant details

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'variant', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price']

    def get_total_price(self, obj):
        total = 0
        for item in obj.items.all():
            price = item.variant.price if item.variant else item.product.price
            total += price * item.quantity
        return total

class AddCartItemSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    variant = serializers.PrimaryKeyRelatedField(queryset=Variant.objects.all(), allow_null=True, required=False)
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, data):
        product = data['product']
        variant = data.get('variant')
        if variant and variant.product != product:
            raise serializers.ValidationError("Variant does not belong to the specified product.")
        return data

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value

from rest_framework import serializers

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    variant_name = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'variant_name', 'quantity', 'price']

    def get_variant_name(self, obj):
        # Avoid AttributeError by checking attribute existence
        variant = getattr(obj, 'variant', None)
        if variant and hasattr(variant, 'variant_name'):
            return variant.variant_name
        return None

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_cost = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'status', 'items','total_cost']
    def get_total_cost(self, obj):
        total = 0
        for item in obj.items.all():
            total += item.price * item.quantity
        return total

class PlaceOrderSerializer(serializers.Serializer):
    # No input fields; order created from user's cart

    def create(self, validated_data):
        user = self.context['request'].user
        cart = Cart.objects.filter(user=user).first()
        if not cart or not cart.items.exists():
            raise serializers.ValidationError("Cart is empty")

        order = Order.objects.create(user=user)
        for item in cart.items.all():
            price = item.variant.price if item.variant else item.product.price
            OrderItem.objects.create(
                order=order,
                product=item.product,
                variant=item.variant,
                quantity=item.quantity,
                price=price
            )
        cart.items.all().delete()  # Clear cart after order placed
        return order

class OrderItemInputSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    variant = serializers.PrimaryKeyRelatedField(queryset=Variant.objects.all(), allow_null=True, required=False)
    quantity = serializers.IntegerField(min_value=1)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price']

class DirectPlaceOrderSerializer(serializers.Serializer):
    items = OrderItemInputSerializer(many=True)

    def validate(self, data):
        # Optional: Validate that variant belongs to product
        for item in data['items']:
            variant = item.get('variant')
            product = item['product']
            if variant and variant.product.id != product.id:
                raise serializers.ValidationError("Variant does not belong to the specified product.")
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        order = Order.objects.create(user=user)
        for item in validated_data['items']:
            product = item['product']
            variant = item.get('variant')
            quantity = item['quantity']
            price = variant.price if variant else product.price
            OrderItem.objects.create(
                order=order,
                product=product,
                variant=variant,
                quantity=quantity,
                price=price
            )
        return order
