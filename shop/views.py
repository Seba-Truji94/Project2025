from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Product, Category


class HomeView(ListView):
    """Vista principal del sitio"""
    model = Product
    template_name = 'shop/home.html'
    context_object_name = 'featured_products'
    
    def get_queryset(self):
        return Product.objects.filter(featured=True, available=True)[:6]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bestsellers'] = Product.objects.filter(
            product_type='bestseller', available=True
        )[:4]
        context['categories'] = Category.objects.all()[:4]
        return context


class ProductListView(ListView):
    """Vista para listar productos"""
    model = Product
    template_name = 'shop/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(available=True)
        
        # Filtro por categoría
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(product_type=category)
        
        # Filtro por búsqueda
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) |
                Q(ingredients__icontains=search)
            )
        
        # Ordenamiento
        sort = self.request.GET.get('sort', '-created_at')
        if sort == 'price_low':
            queryset = queryset.order_by('price')
        elif sort == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort == 'name':
            queryset = queryset.order_by('name')
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category'] = None
        context['current_search'] = self.request.GET.get('search', '')
        context['current_sort'] = self.request.GET.get('sort', '-created_at')
        return context


class ProductDetailView(DetailView):
    """Vista de detalle del producto"""
    model = Product
    template_name = 'shop/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Productos relacionados
        context['related_products'] = Product.objects.filter(
            category=product.category, available=True
        ).exclude(id=product.id)[:4]
        
        # Reviews del producto
        context['reviews'] = product.reviews.all()[:5]
        context['reviews_count'] = product.reviews.count()
        
        # Promedio de rating
        if context['reviews_count'] > 0:
            total_rating = sum(review.rating for review in product.reviews.all())
            context['average_rating'] = total_rating / context['reviews_count']
        else:
            context['average_rating'] = 0
        
        return context


class CategoryDetailView(ListView):
    """Vista de detalle de categoría"""
    model = Product
    template_name = 'shop/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Product.objects.filter(category=self.category, available=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category'] = self.category
        return context


class SearchView(ListView):
    """Vista de búsqueda"""
    model = Product
    template_name = 'shop/search_results.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return Product.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(ingredients__icontains=query),
                available=True
            )
        return Product.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context
