from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from django.core.exceptions import ValidationError
from .models import Shipment, ShipmentItem
from org.models import Cluster, FCP
from accounts.models import User


class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = ['cluster', 'estimated_delivery_date', 'notes']
        widgets = {
            'cluster': forms.Select(attrs={'class': 'form-select form-select-lg'}),
            'estimated_delivery_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-lg'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control form-control-lg'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            try:
                if self.user.role == User.Role.SDSA:
                    # SDSA can only select from assigned clusters
                    managed_clusters = self.user.managed_clusters.all()
                    print(f"DEBUG: SDSA managed clusters: {list(managed_clusters)}")
                    self.fields['cluster'].queryset = managed_clusters
                elif self.user.role == User.Role.CC:
                    # CC is restricted to their cluster
                    try:
                        cc_fcp = self.user.collection_centre.fcp
                        self.fields['cluster'].queryset = Cluster.objects.filter(pk=cc_fcp.cluster.pk)
                        self.fields['cluster'].initial = cc_fcp.cluster
                        self.fields['cluster'].widget.attrs['readonly'] = True
                    except Exception as e:
                        print(f"DEBUG: CC error: {e}")
                        pass
            except Exception as e:
                print(f"DEBUG: Form init error: {e}")
                # Fallback to all clusters if there's an error
                self.fields['cluster'].queryset = Cluster.objects.all()
    
    def clean_cluster(self):
        cluster = self.cleaned_data.get('cluster')
        if not cluster:
            raise ValidationError('Cluster is required.')
        
        # Check if cluster has a collection centre
        if not cluster.get_collection_centre():
            raise ValidationError(f'No collection centre defined for cluster {cluster.name}.')
        
        return cluster


class ShipmentItemForm(forms.ModelForm):
    class Meta:
        model = ShipmentItem
        fields = ['fcp', 'qty_planned']
        widgets = {
            'qty_planned': forms.NumberInput(attrs={'min': '1', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.cluster = kwargs.pop('cluster', None)
        self.direction = kwargs.pop('direction', None)
        super().__init__(*args, **kwargs)
        
        if self.cluster:
            # Filter FCPs by cluster
            fcp_queryset = FCP.objects.filter(cluster=self.cluster)
            
            # For outgoing shipments, exclude collection centre FCP
            if self.direction == Shipment.Direction.OUT:
                fcp_queryset = fcp_queryset.filter(is_collection_centre=False)
            
            self.fields['fcp'].queryset = fcp_queryset
            self.fields['fcp'].empty_label = "Select FCP"
    
    def clean_qty_planned(self):
        qty = self.cleaned_data.get('qty_planned')
        if qty <= 0:
            raise ValidationError('Quantity must be greater than 0.')
        return qty

    def clean_fcp(self):
        fcp = self.cleaned_data.get('fcp')
        if not fcp:
            raise ValidationError('FCP is required.')
        
        # Validate that FCP belongs to the selected cluster
        if self.cluster and fcp.cluster != self.cluster:
            raise ValidationError(f'FCP {fcp.code} does not belong to the selected cluster {self.cluster.name}.')
        
        return fcp


class ShipmentItemFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        
        # Check for duplicate FCPs
        fcps = []
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                fcp = form.cleaned_data.get('fcp')
                if fcp in fcps:
                    raise ValidationError(f'Duplicate FCP {fcp.code} found in shipment.')
                fcps.append(fcp)
        
        # Validate that all FCPs belong to the same cluster
        if fcps:
            first_cluster = fcps[0].cluster
            for fcp in fcps[1:]:
                if fcp.cluster != first_cluster:
                    raise ValidationError(f'All FCPs in a shipment must belong to the same cluster. FCP {fcp.code} belongs to {fcp.cluster.name}, but {fcps[0].code} belongs to {first_cluster.name}.')
        
        # Ensure at least one FCP is selected
        if not fcps:
            raise ValidationError('At least one FCP must be selected for the shipment.')


# Create formset for shipment items
ShipmentItemFormSet = inlineformset_factory(
    Shipment,
    ShipmentItem,
    form=ShipmentItemForm,
    formset=ShipmentItemFormSet,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class ConfirmReceiptForm(forms.Form):
    """Form for confirming receipt of shipments"""
    
    def __init__(self, *args, **kwargs):
        self.shipment = kwargs.pop('shipment', None)
        super().__init__(*args, **kwargs)
        
        if self.shipment:
            # Create fields for each shipment item
            for item in self.shipment.items.all():
                field_name = f'qty_received_{item.id}'
                field_note = f'discrepancy_note_{item.id}'
                
                self.fields[field_name] = forms.IntegerField(
                    label=f'Received for {item.fcp.code}',
                    min_value=0,
                    initial=item.qty_planned,
                    widget=forms.NumberInput(attrs={'class': 'form-control'})
                )
                
                self.fields[field_note] = forms.CharField(
                    label=f'Note for {item.fcp.code}',
                    required=False,
                    widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control'})
                )
    
    def clean(self):
        cleaned_data = super().clean()
        
        if self.shipment:
            for item in self.shipment.items.all():
                qty_field = f'qty_received_{item.id}'
                note_field = f'discrepancy_note_{item.id}'
                
                qty_received = cleaned_data.get(qty_field)
                note = cleaned_data.get(note_field)
                
                if qty_received is not None and qty_received != item.qty_planned:
                    # Require note for discrepancies
                    if not note:
                        self.add_error(
                            note_field, 
                            'Please provide a note explaining the quantity discrepancy.'
                        )
        
        return cleaned_data


class MarkDistributedForm(forms.Form):
    """Form for marking shipments as distributed"""
    
    def __init__(self, *args, **kwargs):
        self.shipment = kwargs.pop('shipment', None)
        super().__init__(*args, **kwargs)
        
        if self.shipment:
            # Create checkbox for each FCP
            for item in self.shipment.items.all():
                field_name = f'distributed_{item.id}'
                self.fields[field_name] = forms.BooleanField(
                    label=f'Distributed to {item.fcp.code}',
                    required=False,
                    initial=True
                )
    
    def clean(self):
        cleaned_data = super().clean()
        
        if self.shipment:
            # Ensure at least one FCP is marked as distributed
            distributed_count = 0
            for item in self.shipment.items.all():
                field_name = f'distributed_{item.id}'
                if cleaned_data.get(field_name):
                    distributed_count += 1
            
            if distributed_count == 0:
                raise ValidationError('At least one FCP must be marked as distributed.')
        
        return cleaned_data
