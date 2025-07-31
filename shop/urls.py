from django.urls import path
from . import views
from .views_placeholder import placeholder_image

app_name = 'shop'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('productos/', views.ProductListView.as_view(), name='product_list'),
    path('producto/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('categoria/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('buscar/', views.SearchView.as_view(), name='search'),
    
    # Placeholders locales
    path('placeholder/<int:width>x<int:height>/', placeholder_image, name='placeholder'),
]
