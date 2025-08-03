"""
URLs para el módulo de gestión empresarial
Solo accesible para superusuarios
"""
from django.urls import path
from . import views

app_name = 'management'

urlpatterns = [
    # Panel principal de gestión
    path('', views.ManagementDashboardView.as_view(), name='dashboard'),
    path('api/statistics/', views.APIStatisticsView.as_view(), name='api_statistics'),
    path('stock/alertas/', views.StockAlertsView.as_view(), name='stock_alerts'),
    
    # Gestión de impuestos
    path('impuestos/', views.TaxManagementView.as_view(), name='tax_management'),
    path('impuestos/crear/', views.TaxCreateView.as_view(), name='tax_create'),
    path('impuestos/<int:pk>/', views.TaxUpdateView.as_view(), name='tax_detail'),
    path('impuestos/<int:pk>/editar/', views.TaxUpdateView.as_view(), name='tax_update'),
    path('impuestos/<int:pk>/eliminar/', views.TaxDeleteView.as_view(), name='tax_delete'),
    path('impuestos/<int:pk>/toggle/', views.TaxToggleView.as_view(), name='tax_toggle'),
    
    # Gestión de cupones
    path('cupones/', views.CouponManagementView.as_view(), name='coupon_management'),
    path('cupones/crear/', views.CouponCreateView.as_view(), name='coupon_create'),
    path('cupones/<int:pk>/editar/', views.CouponUpdateView.as_view(), name='coupon_update'),
    path('cupones/<int:pk>/eliminar/', views.CouponDeleteView.as_view(), name='coupon_delete'),
    path('cupones/<int:pk>/toggle/', views.CouponToggleView.as_view(), name='coupon_toggle'),
    
    # Gestión de proveedores
    path('proveedores/', views.SupplierManagementView.as_view(), name='supplier_management'),
    path('proveedores/crear/', views.SupplierCreateView.as_view(), name='supplier_create'),
    path('proveedores/<int:pk>/editar/', views.SupplierUpdateView.as_view(), name='supplier_update'),
    path('proveedores/<int:pk>/eliminar/', views.SupplierDeleteView.as_view(), name='supplier_delete'),
    path('proveedores/<int:pk>/productos/', views.SupplierProductsView.as_view(), name='supplier_products'),
    
    # Gestión de stock
    path('stock/', views.StockManagementView.as_view(), name='stock_management'),
    path('stock/movimiento/', views.StockMovementCreateView.as_view(), name='stock_movement_create'),
    path('stock/reporte/', views.StockReportView.as_view(), name='stock_report'),
    path('stock/alertas/', views.StockAlertsView.as_view(), name='stock_alerts'),
    
    # Relaciones producto-proveedor
    path('relaciones/', views.ProductSupplierManagementView.as_view(), name='relations_management'),
    path('relaciones/crear/', views.ProductSupplierCreateView.as_view(), name='relation_create'),
    path('relaciones/<int:pk>/editar/', views.ProductSupplierUpdateView.as_view(), name='relation_update'),
    path('relaciones/<int:pk>/eliminar/', views.ProductSupplierDeleteView.as_view(), name='relation_delete'),
    
    # Reportes y estadísticas
    path('reportes/', views.ReportsView.as_view(), name='reports'),
    path('reportes/ventas/', views.SalesReportView.as_view(), name='sales_report'),
    path('reportes/productos/', views.ProductReportView.as_view(), name='product_report'),
    path('reportes/margenes/', views.MarginsReportView.as_view(), name='margins_report'),
    
    # APIs para AJAX
    path('api/productos/', views.ProductsAPIView.as_view(), name='api_products'),
    path('api/estadisticas/', views.StatisticsAPIView.as_view(), name='api_statistics'),
]
