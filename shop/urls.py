from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('productos/', views.ProductListView.as_view(), name='product_list'),
    path('producto/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('categoria/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('buscar/', views.SearchView.as_view(), name='search'),
]
