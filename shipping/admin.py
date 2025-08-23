from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Shipment, ShipmentItem


class ShipmentItemInline(admin.TabularInline):
    model = ShipmentItem
    extra = 1
    fields = ('fcp', 'qty_planned', 'qty_received', 'discrepancy_note')
    readonly_fields = ('discrepancy_note',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('fcp__code')


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'direction', 'cluster', 'collection_centre', 'status', 
        'total_packages', 'estimated_delivery_date', 'created_by', 'created_at'
    )
    list_filter = ('direction', 'status', 'cluster', 'created_at', 'estimated_delivery_date')
    search_fields = ('cluster__name', 'collection_centre__code', 'collection_centre__name', 'notes')
    ordering = ('-created_at',)
    readonly_fields = ('direction', 'total_packages', 'total_received', 'created_at', 'sent_at')
    inlines = [ShipmentItemInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('direction', 'cluster', 'collection_centre', 'estimated_delivery_date', 'notes')
        }),
        ('Status & Tracking', {
            'fields': ('status', 'received_at', 'distributed_at', 'posted_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'sent_at'),
            'classes': ('collapse',)
        }),
        ('Summary', {
            'fields': ('total_packages', 'total_received'),
            'classes': ('collapse',)
        }),
    )
    
    def total_packages(self, obj):
        return obj.total_packages
    total_packages.short_description = 'Total Packages'
    
    def total_received(self, obj):
        return obj.total_received
    total_received.short_description = 'Total Received'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('cluster', 'collection_centre', 'created_by')
    
    def has_add_permission(self, request):
        # Only allow admins to create shipments from admin
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        # Allow admins and shipment creators to edit
        if request.user.is_superuser:
            return True
        if obj and obj.created_by == request.user:
            return True
        return False


@admin.register(ShipmentItem)
class ShipmentItemAdmin(admin.ModelAdmin):
    list_display = (
        'shipment', 'fcp', 'cluster', 'qty_planned', 'qty_received', 
        'has_discrepancy', 'discrepancy_note'
    )
    list_filter = ('shipment__direction', 'shipment__cluster', 'shipment__status')
    search_fields = ('fcp__code', 'fcp__name', 'shipment__cluster__name')
    ordering = ('shipment', 'fcp__code')
    readonly_fields = ('has_discrepancy',)
    
    def cluster(self, obj):
        return obj.shipment.cluster.name
    cluster.short_description = 'Cluster'
    
    def has_discrepancy(self, obj):
        if obj.has_discrepancy:
            return format_html('<span style="color: red;">⚠ Yes</span>')
        return format_html('<span style="color: green;">✓ No</span>')
    has_discrepancy.short_description = 'Has Discrepancy'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('shipment__cluster', 'fcp')
