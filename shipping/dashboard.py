from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Count, Q, Sum, Avg, F
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Shipment, ShipmentItem
from org.models import Cluster, FCP
from accounts.models import User


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'shipping/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.is_admin():
            context.update(self.get_admin_dashboard_data())
        elif user.is_sdsa():
            context.update(self.get_sdsa_dashboard_data(user))
        elif user.is_collection_centre():
            context.update(self.get_cc_dashboard_data(user))
        
        return context
    
    def get_admin_dashboard_data(self):
        """Get data for admin dashboard"""
        # Counts
        total_clusters = Cluster.objects.count()
        total_fcps = FCP.objects.count()
        total_shipments = Shipment.objects.count()
        total_users = User.objects.count()
        
        # Recent shipments
        recent_shipments = Shipment.objects.select_related(
            'cluster', 'collection_centre', 'created_by'
        ).order_by('-created_at')[:10]
        
        # Pending confirmations
        pending_outgoing = Shipment.objects.filter(
            direction=Shipment.Direction.OUT,
            status=Shipment.Status.CREATED
        ).count()
        
        pending_returns = Shipment.objects.filter(
            direction=Shipment.Direction.RET,
            status=Shipment.Status.CREATED
        ).count()
        
        # Monthly statistics
        current_month = timezone.now().month
        current_year = timezone.now().year
        
        monthly_stats = Shipment.objects.filter(
            created_at__year=current_year,
            created_at__month=current_month
        ).aggregate(
            outgoing_created=Count('id', filter=Q(direction=Shipment.Direction.OUT)),
            outgoing_received=Count('id', filter=Q(
                direction=Shipment.Direction.OUT,
                status__in=[Shipment.Status.RECEIVED_CC, Shipment.Status.DISTRIBUTED]
            )),
            returns_created=Count('id', filter=Q(direction=Shipment.Direction.RET)),
            returns_received=Count('id', filter=Q(
                direction=Shipment.Direction.RET,
                status__in=[Shipment.Status.RECEIVED_NO, Shipment.Status.POSTED]
            )),
            returns_posted=Count('id', filter=Q(
                direction=Shipment.Direction.RET,
                status=Shipment.Status.POSTED
            ))
        )
        
        return {
            'dashboard_type': 'admin',
            'total_clusters': total_clusters,
            'total_fcps': total_fcps,
            'total_shipments': total_shipments,
            'total_users': total_users,
            'recent_shipments': recent_shipments,
            'pending_outgoing': pending_outgoing,
            'pending_returns': pending_returns,
            'monthly_stats': monthly_stats,
        }
    
    def get_sdsa_dashboard_data(self, user):
        """Get data for SDSA dashboard"""
        # Get managed clusters
        managed_clusters = user.managed_clusters.all()
        
        # Recent outgoing shipments
        recent_outgoing = Shipment.objects.filter(
            direction=Shipment.Direction.OUT,
            cluster__in=managed_clusters
        ).select_related('cluster', 'collection_centre').order_by('-created_at')[:10]
        
        # Incoming return shipments
        incoming_returns = Shipment.objects.filter(
            direction=Shipment.Direction.RET,
            cluster__in=managed_clusters,
            status__in=[Shipment.Status.CREATED, Shipment.Status.RECEIVED_NO]
        ).select_related('cluster', 'collection_centre').order_by('-created_at')
        
        # Pending confirmations
        pending_returns = incoming_returns.filter(status=Shipment.Status.CREATED).count()
        pending_posted = incoming_returns.filter(status=Shipment.Status.RECEIVED_NO).count()
        
        # Monthly statistics for managed clusters
        current_month = timezone.now().month
        current_year = timezone.now().year
        
        monthly_stats = Shipment.objects.filter(
            cluster__in=managed_clusters,
            created_at__year=current_year,
            created_at__month=current_month
        ).aggregate(
            outgoing_created=Count('id', filter=Q(direction=Shipment.Direction.OUT)),
            outgoing_received=Count('id', filter=Q(
                direction=Shipment.Direction.OUT,
                status__in=[Shipment.Status.RECEIVED_CC, Shipment.Status.DISTRIBUTED]
            )),
            returns_created=Count('id', filter=Q(direction=Shipment.Direction.RET)),
            returns_received=Count('id', filter=Q(
                direction=Shipment.Direction.RET,
                status__in=[Shipment.Status.RECEIVED_NO, Shipment.Status.POSTED]
            )),
            returns_posted=Count('id', filter=Q(
                direction=Shipment.Direction.RET,
                status=Shipment.Status.POSTED
            ))
        )
        
        return {
            'dashboard_type': 'sdsa',
            'managed_clusters': managed_clusters,
            'recent_outgoing': recent_outgoing,
            'incoming_returns': incoming_returns,
            'pending_returns': pending_returns,
            'pending_posted': pending_posted,
            'monthly_stats': monthly_stats,
        }
    
    def get_cc_dashboard_data(self, user):
        """Get data for Collection Centre dashboard"""
        try:
            cc_fcp = user.collection_centre.fcp
            cluster = cc_fcp.cluster
        except:
            return {'dashboard_type': 'cc', 'error': 'Collection centre not configured'}
        
        # Incoming outgoing shipments to confirm
        incoming_outgoing = Shipment.objects.filter(
            direction=Shipment.Direction.OUT,
            cluster=cluster,
            status=Shipment.Status.CREATED
        ).select_related('cluster', 'collection_centre').order_by('-created_at')
        
        # Recent outgoing shipments (already confirmed)
        recent_outgoing = Shipment.objects.filter(
            direction=Shipment.Direction.OUT,
            cluster=cluster,
            status__in=[Shipment.Status.RECEIVED_CC, Shipment.Status.DISTRIBUTED]
        ).select_related('cluster', 'collection_centre').order_by('-created_at')[:5]
        
        # Recent return shipments
        recent_returns = Shipment.objects.filter(
            direction=Shipment.Direction.RET,
            cluster=cluster
        ).select_related('cluster', 'collection_centre').order_by('-created_at')[:5]
        
        # Pending confirmations
        pending_outgoing = incoming_outgoing.count()
        
        # Monthly statistics
        current_month = timezone.now().month
        current_year = timezone.now().year
        
        monthly_stats = Shipment.objects.filter(
            cluster=cluster,
            created_at__year=current_year,
            created_at__month=current_month
        ).aggregate(
            outgoing_created=Count('id', filter=Q(direction=Shipment.Direction.OUT)),
            outgoing_received=Count('id', filter=Q(
                direction=Shipment.Direction.OUT,
                status__in=[Shipment.Status.RECEIVED_CC, Shipment.Status.DISTRIBUTED]
            )),
            returns_created=Count('id', filter=Q(direction=Shipment.Direction.RET)),
            returns_received=Count('id', filter=Q(
                direction=Shipment.Direction.RET,
                status__in=[Shipment.Status.RECEIVED_NO, Shipment.Status.POSTED]
            ))
        )
        
        return {
            'dashboard_type': 'cc',
            'cluster': cluster,
            'cc_fcp': cc_fcp,
            'incoming_outgoing': incoming_outgoing,
            'recent_outgoing': recent_outgoing,
            'recent_returns': recent_returns,
            'pending_outgoing': pending_outgoing,
            'monthly_stats': monthly_stats,
        }


@login_required
def reports_view(request):
    """Reports and analytics view"""
    if not request.user.is_admin() and not request.user.is_sdsa():
        messages.error(request, 'You do not have permission to view reports.')
        return redirect('dashboard')
    
    # Get date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if not date_from:
        date_from = (timezone.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not date_to:
        date_to = timezone.now().strftime('%Y-%m-%d')
    
    # Parse dates
    try:
        start_date = datetime.strptime(date_from, '%Y-%m-%d').date()
        end_date = datetime.strptime(date_to, '%Y-%m-%d').date()
    except ValueError:
        start_date = (timezone.now() - timedelta(days=30)).date()
        end_date = timezone.now().date()
    
    # Base queryset
    shipments = Shipment.objects.filter(
        created_at__date__range=[start_date, end_date]
    )
    
    # Apply role-based filtering
    if request.user.is_sdsa():
        shipments = shipments.filter(cluster__in=request.user.managed_clusters.all())
    
    # Cluster statistics
    cluster_stats = shipments.values('cluster__name').annotate(
        outgoing_created=Count('id', filter=Q(direction=Shipment.Direction.OUT)),
        outgoing_received=Count('id', filter=Q(
            direction=Shipment.Direction.OUT,
            status__in=[Shipment.Status.RECEIVED_CC, Shipment.Status.DISTRIBUTED]
        )),
        returns_created=Count('id', filter=Q(direction=Shipment.Direction.RET)),
        returns_received=Count('id', filter=Q(
            direction=Shipment.Direction.RET,
            status__in=[Shipment.Status.RECEIVED_NO, Shipment.Status.POSTED]
        )),
        returns_posted=Count('id', filter=Q(
            direction=Shipment.Direction.RET,
            status=Shipment.Status.POSTED
        ))
    ).order_by('cluster__name')
    
    # Overall statistics
    overall_stats = shipments.aggregate(
        total_outgoing=Count('id', filter=Q(direction=Shipment.Direction.OUT)),
        total_returns=Count('id', filter=Q(direction=Shipment.Direction.RET)),
        outgoing_received=Count('id', filter=Q(
            direction=Shipment.Direction.OUT,
            status__in=[Shipment.Status.RECEIVED_CC, Shipment.Status.DISTRIBUTED]
        )),
        returns_received=Count('id', filter=Q(
            direction=Shipment.Direction.RET,
            status__in=[Shipment.Status.RECEIVED_NO, Shipment.Status.POSTED]
        )),
        returns_posted=Count('id', filter=Q(
            direction=Shipment.Direction.RET,
            status=Shipment.Status.POSTED
        ))
    )
    
    # Calculate turnaround times
    turnaround_stats = {}
    for direction in [Shipment.Direction.OUT, Shipment.Direction.RET]:
        direction_shipments = shipments.filter(direction=direction)
        
        if direction == Shipment.Direction.OUT:
            # OUT: created → received at CC → distributed
            received_shipments = direction_shipments.filter(
                status__in=[Shipment.Status.RECEIVED_CC, Shipment.Status.DISTRIBUTED]
            )
            
            if received_shipments.exists():
                avg_receipt_time = received_shipments.aggregate(
                    avg_time=Avg(F('received_at') - F('created_at'))
                )['avg_time']
                turnaround_stats['outgoing_receipt'] = avg_receipt_time
                
                distributed_shipments = direction_shipments.filter(status=Shipment.Status.DISTRIBUTED)
                if distributed_shipments.exists():
                    avg_distribution_time = distributed_shipments.aggregate(
                        avg_time=Avg(F('distributed_at') - F('received_at'))
                    )['avg_time']
                    turnaround_stats['outgoing_distribution'] = avg_distribution_time
        
        else:  # RET
            # RET: created → received at NO → posted
            received_shipments = direction_shipments.filter(
                status__in=[Shipment.Status.RECEIVED_NO, Shipment.Status.POSTED]
            )
            
            if received_shipments.exists():
                avg_receipt_time = received_shipments.aggregate(
                    avg_time=Avg(F('received_at') - F('created_at'))
                )['avg_time']
                turnaround_stats['returns_receipt'] = avg_receipt_time
                
                posted_shipments = direction_shipments.filter(status=Shipment.Status.POSTED)
                if posted_shipments.exists():
                    avg_posting_time = posted_shipments.aggregate(
                        avg_time=Avg(F('posted_at') - F('received_at'))
                    )['avg_time']
                    turnaround_stats['returns_posting'] = avg_posting_time
    
    context = {
        'date_from': date_from,
        'date_to': date_to,
        'cluster_stats': cluster_stats,
        'overall_stats': overall_stats,
        'turnaround_stats': turnaround_stats,
        'clusters': Cluster.objects.all() if request.user.is_admin() else request.user.managed_clusters.all(),
    }
    
    return render(request, 'shipping/reports.html', context)
