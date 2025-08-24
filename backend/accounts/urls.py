from django.urls import path
from .views import RegisterView, LoginView , UserAddressListCreateView, UserAddressRetrieveUpdateDestroyView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('addresses/', UserAddressListCreateView.as_view(), name='user-addresses'),
    path('addresses/<int:pk>/', UserAddressRetrieveUpdateDestroyView.as_view(), name='user-address-detail'),
]
