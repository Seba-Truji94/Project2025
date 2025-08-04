from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.CartDetailView.as_view(), name='cart_detail'),
    path('my-cart/', views.MyCartView.as_view(), name='my_cart'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('clear/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('migrate/', views.migrate_session_cart, name='migrate_session_cart'),
    path('summary/', views.cart_summary, name='cart_summary'),
    # URLs para cupones
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('remove-coupon/', views.remove_coupon, name='remove_coupon'),
]
