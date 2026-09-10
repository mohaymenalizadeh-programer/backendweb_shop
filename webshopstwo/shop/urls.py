from django.urls import path
from .views import (
    ProductListView, 
    BrandListView, 
    CategoryListView, 
    CartView, 
    AddToCartView, 
    UpdateCartItemView, 
    ShopView,          
    ProductDetailView, 
    verify,  
    send_request,
    user_orders_api ,
    ContactAPIView
)

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'),
    path('brands/', BrandListView.as_view(), name='brand-list'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('cart/', CartView.as_view(), name='cart-detail'),
    path('add-to-cart/', AddToCartView.as_view(), name='add-to-cart'),
    path('update-cart/', UpdateCartItemView.as_view(), name='update-cart'),
    path('firstdata/', ShopView.as_view(), name='views'),  
    path('product/<str:slug>/', ProductDetailView.as_view(), name='product-detail'),
    path('request/', send_request, name='request'),
    path('verify/', verify, name='verify'),
    path('orders/', user_orders_api, name='user-orders'),
    path('api/contact/', ContactAPIView.as_view(), name='contact-api'),
]