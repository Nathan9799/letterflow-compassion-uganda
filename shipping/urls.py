from django.urls import path
from . import views, dashboard

app_name = 'shipping'

urlpatterns = [
    # Dashboard
    path('', dashboard.DashboardView.as_view(), name='dashboard'),
    path('reports/', dashboard.reports_view, name='reports'),
    
    # Authentication
    path('logout/', views.custom_logout, name='logout'),
    
    # Shipments
    path('shipments/', views.ShipmentListView.as_view(), name='shipment_list'),
    path('shipments/<int:pk>/', views.ShipmentDetailView.as_view(), name='shipment_detail'),
    
    # Create shipments
    path('shipments/outgoing/create/', views.create_outgoing_shipment, name='create_outgoing_shipment'),
    path('shipments/return/create/', views.create_return_shipment, name='create_return_shipment'),
    
    # Shipment actions
    path('shipments/<int:pk>/confirm-receipt/', views.confirm_receipt, name='confirm_receipt'),
    path('shipments/<int:pk>/mark-distributed/', views.mark_distributed, name='mark_distributed'),
    path('shipments/<int:pk>/mark-posted/', views.mark_posted, name='mark_posted'),
    
    # Export
    path('shipments/export/', views.export_shipments_csv, name='export_shipments_csv'),
    
    # AJAX
    path('ajax/get-fcps/', views.get_fcps_for_cluster, name='get_fcps_for_cluster'),

    # Bulk operations
    path('users/bulk-import/', views.bulk_user_import, name='bulk_user_import'),
    path('users/download-template/', views.download_csv_template, name='download_csv_template'),
]
