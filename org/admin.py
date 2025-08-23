from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import Cluster, FCP, CollectionCentreUser


class FCPInline(admin.TabularInline):
    model = FCP
    extra = 1
    fields = ('code', 'name', 'is_collection_centre')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('code')


@admin.register(Cluster)
class ClusterAdmin(admin.ModelAdmin):
    list_display = ('name', 'sdsa_owner', 'get_fcp_count', 'get_collection_centre', 'created_at')
    list_filter = ('sdsa_owner', 'created_at')
    search_fields = ('name', 'sdsa_owner__username', 'sdsa_owner__first_name', 'sdsa_owner__last_name')
    ordering = ('name',)
    inlines = [FCPInline]
    
    def get_fcp_count(self, obj):
        return obj.fcps.count()
    get_fcp_count.short_description = 'FCP Count'
    
    def get_collection_centre(self, obj):
        cc = obj.get_collection_centre()
        return cc.code if cc else 'No CC'
    get_collection_centre.short_description = 'Collection Centre'
    
    def save_formset(self, request, form, formset, change):
        """Save the formset and handle FCP validation properly."""
        instances = formset.save(commit=False)
        
        # First save the cluster if it's new
        if not change:  # New cluster
            form.instance.save()
        
        # Now save FCPs with proper cluster reference
        for instance in instances:
            if instance.cluster_id is None:
                instance.cluster = form.instance
            instance.save()
        
        # Handle deleted instances
        for obj in formset.deleted_objects:
            obj.delete()
        
        formset.save_m2m()


@admin.register(FCP)
class FCPAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'cluster', 'is_collection_centre', 'created_at')
    list_filter = ('cluster', 'is_collection_centre', 'created_at')
    search_fields = ('code', 'name', 'cluster__name')
    ordering = ('cluster', 'code')
    list_editable = ('is_collection_centre',)
    
    def save_model(self, request, obj, form, change):
        try:
            obj.save()
        except ValidationError as e:
            self.message_user(request, f'Error saving FCP: {e}', level='ERROR')
            return
        super().save_model(request, obj, form, change)


@admin.register(CollectionCentreUser)
class CollectionCentreUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'fcp', 'cluster', 'created_at')
    list_filter = ('fcp__cluster', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'fcp__code', 'fcp__name')
    ordering = ('fcp__cluster', 'user__username')
    
    def cluster(self, obj):
        return obj.fcp.cluster.name
    cluster.short_description = 'Cluster'
    
    def save_model(self, request, obj, form, change):
        try:
            obj.save()
        except ValidationError as e:
            self.message_user(request, f'Error saving Collection Centre User: {e}', level='ERROR')
            return
        super().save_model(request, obj, form, change)
