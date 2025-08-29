from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy, reverse
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
import csv
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import logout

from .models import Shipment, ShipmentItem
from .forms import (
    ShipmentForm, ShipmentItemFormSet, ConfirmReceiptForm, 
    MarkDistributedForm
)
from org.models import Cluster, FCP
from accounts.models import User
from .forms import BulkUserImportForm


def user_can_access_shipment(user, shipment):
    """Check if user can access a specific shipment"""
    if user.is_admin():
        return True
    
    if user.is_sdsa():
        return shipment.cluster in user.managed_clusters.all()
    
    if user.is_collection_centre():
        try:
            return shipment.cluster == user.collection_centre.fcp.cluster
        except:
            return False
    
    return False


class ShipmentListView(LoginRequiredMixin, ListView):
    model = Shipment
    template_name = 'shipping/shipment_list.html'
    context_object_name = 'shipments'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Shipment.objects.select_related(
            'cluster', 'collection_centre', 'created_by'
        ).prefetch_related('items')
        
        # Apply filters
        cluster = self.request.GET.get('cluster')
        direction = self.request.GET.get('direction')
        status = self.request.GET.get('status')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        if cluster:
            queryset = queryset.filter(cluster_id=cluster)
        
        if direction:
            queryset = queryset.filter(direction=direction)
        
        if status:
            queryset = queryset.filter(status=status)
        
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=date_from)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=date_to)
            except ValueError:
                pass
        
        # Apply role-based filtering
        user = self.request.user
        if user.is_sdsa():
            queryset = queryset.filter(cluster__in=user.managed_clusters.all())
        elif user.is_collection_centre():
            try:
                queryset = queryset.filter(cluster=user.collection_centre.fcp.cluster)
            except:
                queryset = queryset.none()
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Set current user on each shipment object for template permission checks
        for shipment in context['shipments']:
            shipment._current_user = user
        
        # Add filter options
        if user.is_admin():
            context['clusters'] = Cluster.objects.all()
        elif user.is_sdsa():
            context['clusters'] = user.managed_clusters.all()
        elif user.is_collection_centre():
            try:
                context['clusters'] = [user.collection_centre.fcp.cluster]
            except:
                context['clusters'] = []
        
        context['directions'] = Shipment.Direction.choices
        context['statuses'] = Shipment.Status.choices
        context['current_filters'] = self.request.GET
        
        return context


class ShipmentDetailView(LoginRequiredMixin, DetailView):
    model = Shipment
    template_name = 'shipping/shipment_detail.html'
    context_object_name = 'shipment'
    
    def get_queryset(self):
        return Shipment.objects.select_related(
            'cluster', 'collection_centre', 'created_by'
        ).prefetch_related('items__fcp')
    
    def dispatch(self, request, *args, **kwargs):
        shipment = self.get_object()
        if not user_can_access_shipment(request.user, shipment):
            messages.error(request, 'You do not have permission to view this shipment.')
            return redirect('shipment_list')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shipment = self.get_object()
        
        # Set current user on shipment object for template permission checks
        shipment._current_user = self.request.user
        
        # Add user to context for permission checks
        context['current_user'] = self.request.user
        
        # Add action forms
        if shipment.can_confirm_receipt_as_user(self.request.user):
            context['confirm_form'] = ConfirmReceiptForm(shipment=shipment)
        
        if shipment.can_mark_distributed():
            context['distribute_form'] = MarkDistributedForm(shipment=shipment)
        
        return context


@login_required
def create_outgoing_shipment(request):
    """Create outgoing shipment (SDSA only)"""
    if not request.user.is_sdsa():
        messages.error(request, 'Only SDSA users can create outgoing shipments.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ShipmentForm(request.POST, user=request.user)
        formset = ShipmentItemFormSet(request.POST, instance=Shipment())
        
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                # Create shipment with all required fields
                shipment = form.save(commit=False)
                shipment.created_by = request.user
                shipment.direction = Shipment.Direction.OUT
                
                # Set collection centre from cluster
                if shipment.cluster:
                    cc = shipment.cluster.get_collection_centre()
                    if cc:
                        shipment.collection_centre = cc
                
                shipment.save()
                
                # Create shipment items
                formset.instance = shipment
                formset.save()
                
                messages.success(request, 'Outgoing shipment created successfully.')
                return redirect('shipping:shipment_detail', pk=shipment.pk)
    else:
        form = ShipmentForm(user=request.user)
        # Create formset with proper parameters
        formset = ShipmentItemFormSet(
            instance=Shipment(),
            form_kwargs={'cluster': None, 'direction': Shipment.Direction.OUT}
        )
    
    # Pre-populate FCP dropdowns with available FCPs for the user's managed clusters
    if request.user.role == User.Role.SDSA:
        managed_clusters = request.user.managed_clusters.all()
        if managed_clusters:
            # Get all FCPs from managed clusters (including collection centres)
            # Collection centres can now receive packages for their own use
            available_fcps = FCP.objects.filter(
                cluster__in=managed_clusters
                # Removed is_collection_centre=False filter to allow collection centres
            )
            
            # Set the queryset for all FCP dropdowns
            for formset_form in formset.forms:
                formset_form.fields['fcp'].queryset = available_fcps
                formset_form.fields['fcp'].empty_label = "Select FCP"
                formset_form.fields['fcp'].widget.attrs.update({
                    'class': 'form-select fcp-select'
                })
    else:
        # For other user types, start with empty queryset
        for formset_form in formset.forms:
            formset_form.fields['fcp'].queryset = FCP.objects.none()
            formset_form.fields['fcp'].widget.attrs.update({
                'class': 'form-select fcp-select'
            })
    
    context = {
        'form': form,
        'formset': formset,
        'direction': 'OUT',
        'title': 'Create Outgoing Shipment'
    }
    return render(request, 'shipping/shipment_form.html', context)


@login_required
def create_return_shipment(request):
    """Create return shipment (CC only)"""
    if not request.user.is_collection_centre():
        messages.error(request, 'Only Collection Centre users can create return shipments.')
        return redirect('dashboard')
    
    try:
        cc_fcp = request.user.collection_centre.fcp
        cluster = cc_fcp.cluster
    except:
        messages.error(request, 'Your collection centre is not properly configured.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ShipmentForm(request.POST, user=request.user)
        formset = ShipmentItemFormSet(request.POST, instance=Shipment())
        
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                # Create shipment
                shipment = form.save(commit=False)
                shipment.created_by = request.user
                shipment.direction = Shipment.Direction.RET
                shipment.cluster = cluster
                shipment.collection_centre = cc_fcp
                shipment.save()
                
                # Create shipment items
                formset.instance = shipment
                formset.save()
                
                messages.success(request, 'Return shipment created successfully.')
                return redirect('shipping:shipment_detail', pk=shipment.pk)
    else:
        form = ShipmentForm(user=request.user)
        # Create formset with proper parameters
        formset = ShipmentItemFormSet(
            instance=Shipment(),
            form_kwargs={'cluster': cluster, 'direction': Shipment.Direction.RET}
        )
    
    # Set cluster and direction for formset
    for formset_form in formset.forms:
        formset_form.fields['fcp'].queryset = FCP.objects.filter(
            cluster=cluster, 
            is_collection_centre=False
        )
    
    context = {
        'form': form,
        'formset': formset,
        'direction': 'RET',
        'title': 'Create Return Shipment'
    }
    return render(request, 'shipping/shipment_form.html', context)


@login_required
@require_POST
def confirm_receipt(request, pk):
    """Confirm receipt of shipment"""
    shipment = get_object_or_404(Shipment, pk=pk)
    
    if not shipment.can_confirm_receipt_as_user(request.user):
        messages.error(request, 'You do not have permission to confirm this shipment.')
        return redirect('shipping:shipment_detail', pk=pk)
    
    form = ConfirmReceiptForm(request.POST, shipment=shipment)
    if form.is_valid():
        with transaction.atomic():
            # Update shipment status
            if shipment.direction == Shipment.Direction.OUT:
                shipment.status = Shipment.Status.RECEIVED_CC
            else:  # RET
                shipment.status = Shipment.Status.RECEIVED_NO
            
            shipment.received_at = timezone.now()
            shipment.save()
            
            # Update shipment items
            for item in shipment.items.all():
                qty_field = f'qty_received_{item.id}'
                note_field = f'discrepancy_note_{item.id}'
                
                if qty_field in form.cleaned_data:
                    item.qty_received = form.cleaned_data[qty_field]
                    item.discrepancy_note = form.cleaned_data.get(note_field, '')
                    item.save()
            
            messages.success(request, 'Shipment receipt confirmed successfully.')
    else:
        messages.error(request, 'Please correct the errors below.')
    
    return redirect('shipping:shipment_detail', pk=pk)


@login_required
@require_POST
def mark_distributed(request, pk):
    """Mark shipment as distributed to FCPs (OUT only)"""
    shipment = get_object_or_404(Shipment, pk=pk)
    
    if not user_can_access_shipment(request.user, shipment):
        messages.error(request, 'You do not have permission to mark this shipment as distributed.')
        return redirect('shipping:shipment_detail', pk=pk)
    
    if not shipment.can_mark_distributed():
        messages.error(request, 'This shipment cannot be marked as distributed.')
        return redirect('shipping:shipment_detail', pk=pk)
    
    form = MarkDistributedForm(request.POST, shipment=shipment)
    if form.is_valid():
        shipment.status = Shipment.Status.DISTRIBUTED
        shipment.distributed_at = timezone.now()
        shipment.save()
        
        messages.success(request, 'Shipment marked as distributed successfully.')
    else:
        messages.error(request, 'Please correct the errors below.')
    
    return redirect('shipping:shipment_detail', pk=pk)


@login_required
@require_POST
def mark_posted(request, pk):
    """Mark return shipment as posted (SDSA only)"""
    shipment = get_object_or_404(Shipment, pk=pk)
    
    if not request.user.is_sdsa():
        messages.error(request, 'Only SDSA users can mark shipments as posted.')
        return redirect('shipping:shipment_detail', pk=pk)
    
    if not user_can_access_shipment(request.user, shipment):
        messages.error(request, 'You do not have permission to mark this shipment as posted.')
        return redirect('shipping:shipment_detail', pk=pk)
    
    if not shipment.can_mark_posted():
        messages.error(request, 'This shipment cannot be marked as posted.')
        return redirect('shipping:shipment_detail', pk=pk)
    
    shipment.status = Shipment.Status.POSTED
    shipment.posted_at = timezone.now()
    shipment.save()
    
    messages.success(request, 'Shipment marked as posted successfully.')
    return redirect('shipping:shipment_detail', pk=pk)


@login_required
def export_shipments_csv(request):
    """Export shipments to CSV"""
    if not request.user.is_admin() and not request.user.is_sdsa():
        messages.error(request, 'You do not have permission to export shipments.')
        return redirect('shipping:shipment_list')
    
    # Get filtered queryset
    shipments = ShipmentListView.as_view()(request).context_data['shipments']
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="shipments.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Direction', 'Cluster', 'Collection Centre', 'Status', 
        'ETA', 'Total Packages', 'Total Received', 'Created By', 'Created At'
    ])
    
    for shipment in shipments:
        writer.writerow([
            shipment.id,
            shipment.get_direction_display(),
            shipment.cluster.name,
            shipment.collection_centre.code,
            shipment.get_status_display(),
            shipment.estimated_delivery_date,
            shipment.total_packages,
            shipment.total_received,
            shipment.created_by.username,
            shipment.created_at.strftime('%Y-%m-%d %H:%M')
        ])
    
    return response


# AJAX views for dynamic form handling
@login_required
def get_fcps_for_cluster(request):
    """Get FCPs for a specific cluster (AJAX)"""
    cluster_id = request.GET.get('cluster_id') or request.GET.get('cluster')
    direction = request.GET.get('direction')
    
    if not cluster_id:
        return JsonResponse({'fcps': [], 'error': 'No cluster ID provided'})
    
    try:
        cluster = Cluster.objects.get(pk=cluster_id)
        fcps = FCP.objects.filter(cluster=cluster)
        
        # For outgoing shipments, we now allow collection centre FCPs
        # Collection centres can receive packages for their own use
        if direction == 'OUT':
            # Include all FCPs including collection centres
            pass
        
        fcp_data = [{'id': fcp.id, 'code': fcp.code, 'name': fcp.name or ''} for fcp in fcps]
        return JsonResponse({'fcps': fcp_data})
    except Cluster.DoesNotExist:
        return JsonResponse({'fcps': [], 'error': f'Cluster with ID {cluster_id} not found'})
    except Exception as e:
        return JsonResponse({'fcps': [], 'error': f'Unexpected error: {str(e)}'})


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def custom_logout(request):
    """Custom logout view that handles both GET and POST requests."""
    logout(request)
    return redirect('login')


@login_required
def bulk_user_import(request):
    """Bulk import users from CSV file"""
    if not request.user.is_admin():
        messages.error(request, 'Only admin users can import users in bulk.')
        return redirect('shipping:dashboard')
    
    if request.method == 'POST':
        form = BulkUserImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            default_password = form.cleaned_data['default_password']
            send_welcome_emails = form.cleaned_data['send_welcome_emails']
            
            try:
                import csv
                from django.contrib.auth import get_user_model
                from django.db import transaction
                
                User = get_user_model()
                results = {
                    'success': [],
                    'errors': [],
                    'total_processed': 0
                }
                
                # Read CSV file
                content = csv_file.read().decode('utf-8')
                reader = csv.DictReader(content.splitlines())
                
                with transaction.atomic():
                    for row_num, row in enumerate(reader, start=2):  # Start at 2 for row numbers
                        try:
                            # Clean and validate row data
                            username = row['username'].strip()
                            first_name = row['first_name'].strip()
                            last_name = row['last_name'].strip()
                            email = row['email'].strip()
                            role = row['role'].strip().upper()
                            
                            # Skip empty rows
                            if not username or not first_name or not last_name:
                                continue
                            
                            # Validate role
                            if role not in [User.Role.SDSA, User.Role.CC, User.Role.ADMIN]:
                                results['errors'].append(f'Row {row_num}: Invalid role "{role}". Must be SDSA, CC, or ADMIN.')
                                continue
                            
                            # Check if user already exists
                            if User.objects.filter(username=username).exists():
                                results['errors'].append(f'Row {row_num}: Username "{username}" already exists.')
                                continue
                            
                            if email and User.objects.filter(email=email).exists():
                                results['errors'].append(f'Row {row_num}: Email "{email}" already exists.')
                                continue
                            
                            # Create user
                            password = default_password or username
                            user = User.objects.create_user(
                                username=username,
                                email=email,
                                password=password,
                                first_name=first_name,
                                last_name=last_name,
                                role=role
                            )
                            
                            # Handle role-specific setup
                            if role == User.Role.SDSA:
                                # Handle cluster assignment if provided
                                cluster_name = row.get('cluster', '').strip()
                                if cluster_name:
                                    try:
                                        cluster = Cluster.objects.get(name__iexact=cluster_name)
                                        user.managed_clusters.add(cluster)
                                    except Cluster.DoesNotExist:
                                        results['errors'].append(f'Row {row_num}: Cluster "{cluster_name}" not found.')
                            
                            elif role == User.Role.CC:
                                # Handle collection centre FCP assignment if provided
                                fcp_code = row.get('fcp_code', '').strip()
                                if fcp_code:
                                    try:
                                        fcp = FCP.objects.get(code__iexact=fcp_code, is_collection_centre=True)
                                        # Create collection centre user link
                                        from accounts.models import CollectionCentreUser
                                        CollectionCentreUser.objects.create(user=user, fcp=fcp)
                                    except FCP.DoesNotExist:
                                        results['errors'].append(f'Row {row_num}: Collection Centre FCP "{fcp_code}" not found.')
                            
                            results['success'].append(f'Row {row_num}: User "{username}" created successfully.')
                            results['total_processed'] += 1
                            
                        except Exception as e:
                            results['errors'].append(f'Row {row_num}: Error creating user: {str(e)}')
                
                # Show results
                if results['success']:
                    messages.success(request, f'Successfully created {results["total_processed"]} users!')
                if results['errors']:
                    for error in results['errors']:
                        messages.warning(request, error)
                
                return redirect('shipping:bulk_user_import')
                
            except Exception as e:
                messages.error(request, f'Error processing CSV file: {str(e)}')
    else:
        form = BulkUserImportForm()
    
    context = {
        'form': form,
        'title': 'Bulk User Import'
    }
    return render(request, 'shipping/bulk_user_import.html', context)


@login_required
def download_csv_template(request):
    """Download CSV template for bulk user import"""
    if not request.user.is_admin():
        messages.error(request, 'Only admin users can download templates.')
        return redirect('shipping:dashboard')
    
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="bulk_user_import_template.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'username',
        'first_name', 
        'last_name',
        'email',
        'role',
        'cluster',
        'fcp_code'
    ])
    
    # Write example rows
    writer.writerow([
        'john_doe',
        'John',
        'Doe',
        'john@example.com',
        'SDSA',
        'Mbarara',
        ''
    ])
    
    writer.writerow([
        'jane_smith',
        'Jane',
        'Smith',
        'jane@example.com',
        'CC',
        '',
        'UG0249'
    ])
    
    writer.writerow([
        'admin_user',
        'Admin',
        'User',
        'admin@example.com',
        'ADMIN',
        '',
        ''
    ])
    
    return response
