from django.urls import path,include
from .views import CategoryListView,ProductsByCategoryView
from .views import UserCartView, UserOrdersListView
from .views import AddToCartView, PlaceOrderView, UserOrdersListView,OrderAdminViewSet,CartItemUpdateDeleteView,DirectPlaceOrderView,OrderDeleteView
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'admin/orders', OrderAdminViewSet, basename='admin-orders')

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<int:category_id>/products/', ProductsByCategoryView.as_view(), name='products-by-category'),
    path('cart/', UserCartView.as_view(), name='user-cart'),
    path('orders/', UserOrdersListView.as_view(), name='user-orders'),
    path('cart/add/', AddToCartView.as_view(), name='add-to-cart'),
    path('orders/place/', PlaceOrderView.as_view(), name='place-order'),
    path('', include(router.urls)),
    path('orders/', UserOrdersListView.as_view(), name='user-orders'),
    path('cart/items/<int:pk>/', CartItemUpdateDeleteView.as_view(), name='cart-item-detail'),
    path('orders/direct-place/', DirectPlaceOrderView.as_view(), name='direct-place-order'),
    path('orders/<int:order_id>/delete/', OrderDeleteView.as_view(), name='order-delete'),
]
