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
        search = self.request.GET.get('search') or self.request.GET.get('q')
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
        context['current_search'] = self.request.GET.get('search', '') or self.request.GET.get('q', '')
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
        
        # Productos relacionados por categoría
        related_by_category = Product.objects.filter(
            category=product.category, available=True
        ).exclude(id=product.id)[:4]
        
        # Productos similares por ingredientes (si el producto actual no llena los 4 espacios)
        similar_by_ingredients = Product.objects.none()
        if len(related_by_category) < 4 and product.ingredients:
            # Obtener palabras clave de los ingredientes
            ingredient_words = product.ingredients.lower().split()
            ingredient_queries = Q()
            
            for word in ingredient_words:
                if len(word) > 3:  # Solo palabras significativas
                    ingredient_queries |= Q(ingredients__icontains=word)
            
            similar_by_ingredients = Product.objects.filter(
                ingredient_queries, available=True
            ).exclude(
                id=product.id
            ).exclude(
                id__in=related_by_category.values_list('id', flat=True)
            )[:4-len(related_by_category)]
        
        # Combinar productos relacionados y similares
        context['related_products'] = list(related_by_category) + list(similar_by_ingredients)
        
        # Productos alternativos (de otras categorías pero con características similares)
        if len(context['related_products']) < 4:
            alternative_products = Product.objects.filter(
                available=True
            ).exclude(
                id=product.id
            ).exclude(
                id__in=[p.id for p in context['related_products']]
            ).order_by('?')[:4-len(context['related_products'])]
            
            context['related_products'].extend(list(alternative_products))
        
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
            # Búsqueda principal
            return Product.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(ingredients__icontains=query),
                available=True
            ).order_by('-created_at')
        return Product.objects.none()
    
    def get_similar_products(self, query, exclude_ids=None):
        """Obtener productos similares basados en categorías y palabras clave"""
        if not query:
            return Product.objects.none()
        
        # Palabras clave de la búsqueda
        query_words = query.lower().split()
        
        similar_products = Product.objects.filter(available=True)
        
        if exclude_ids:
            similar_products = similar_products.exclude(id__in=exclude_ids)
        
        # Buscar por categorías que contengan las palabras de búsqueda
        category_matches = Q()
        for word in query_words:
            category_matches |= Q(category__name__icontains=word)
        
        # Buscar productos en categorías similares
        similar_by_category = similar_products.filter(category_matches)
        
        # Buscar productos con ingredientes similares
        ingredient_matches = Q()
        for word in query_words:
            if len(word) > 2:  # Solo palabras de más de 2 caracteres
                ingredient_matches |= Q(ingredients__icontains=word)
        
        similar_by_ingredients = similar_products.filter(ingredient_matches)
        
        # Combinar resultados y eliminar duplicados
        similar_products = (similar_by_category | similar_by_ingredients).distinct()[:8]
        
        return similar_products
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        context['query'] = query
        
        # Si hay resultados, obtener productos similares
        if context['products'] and query:
            found_product_ids = list(context['products'].values_list('id', flat=True))
            context['similar_products'] = self.get_similar_products(query, found_product_ids)
        elif query:
            # Si no hay resultados exactos, mostrar productos similares
            context['similar_products'] = self.get_similar_products(query)
        
        return context
