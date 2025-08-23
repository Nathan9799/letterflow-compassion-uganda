from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum
from accounts.models import User
from org.models import Cluster, FCP


class Shipment(models.Model):
    class Direction(models.TextChoices):
        OUT = 'OUT', 'Outgoing (SDSA → Collection Centre)'
        RET = 'RET', 'Return (Collection Centre → SDSA)'
    
    class Status(models.TextChoices):
        CREATED = 'CREATED', 'Created/Sent'
        RECEIVED_CC = 'RECEIVED_CC', 'Received at Collection Centre'
        DISTRIBUTED = 'DISTRIBUTED', 'Distributed to FCPs'
        RECEIVED_NO = 'RECEIVED_NO', 'Received at National Office'
        POSTED = 'POSTED', 'Posted'
    
    direction = models.CharField(
        max_length=3,
        choices=Direction.choices,
        editable=False  # Auto-set based on creator role
    )
    cluster = models.ForeignKey(
        Cluster,
        on_delete=models.CASCADE,
        related_name='shipments'
    )
    collection_centre = models.ForeignKey(
        FCP,
        on_delete=models.CASCADE,
        limit_choices_to={'is_collection_centre': True},
        related_name='shipments'
    )
    estimated_delivery_date = models.DateField()
    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CREATED
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    received_at = models.DateTimeField(null=True, blank=True)
    distributed_at = models.DateTimeField(null=True, blank=True)
    posted_at = models.DateTimeField(null=True, blank=True)
    
    # User tracking
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_shipments'
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_direction_display()} - {self.cluster.name} - {self.get_status_display()}"
    
    def clean(self):
        super().clean()
        # Basic validation only
        pass
    
    def save(self, *args, **kwargs):
        # Simple save without complex logic
        super().save(*args, **kwargs)
    
    @property
    def total_packages(self):
        """Auto-calculated total from shipment items"""
        return self.items.aggregate(total=Sum('qty_planned'))['total'] or 0
    
    @property
    def total_received(self):
        """Total received packages"""
        return self.items.aggregate(total=Sum('qty_received'))['total'] or 0
    
    def can_confirm_receipt(self):
        """Check if shipment can be confirmed as received"""
        # Only allow confirmation if status is CREATED
        if self.direction == self.Direction.OUT:
            return self.status == self.Status.CREATED
        else:  # RET
            return self.status == self.Status.CREATED
    
    def can_confirm_receipt_as_user(self, user):
        """Check if specific user can confirm receipt"""
        if not self.can_confirm_receipt():
            return False
        
        if self.direction == self.Direction.OUT:
            # For outgoing shipments, only Collection Centre users can confirm
            return user.is_collection_centre() and user.collection_centre.fcp.cluster == self.cluster
        else:  # RET
            # For return shipments, only SDSA users can confirm
            return user.is_sdsa() and self.cluster in user.managed_clusters.all()
    
    @property
    def can_confirm_receipt_for_current_user(self):
        """Property to check if current user can confirm receipt (for templates)"""
        # This will be set by the view context
        if hasattr(self, '_current_user'):
            return self.can_confirm_receipt_as_user(self._current_user)
        return False
    
    @property
    def can_mark_distributed_for_current_user(self):
        """Property to check if current user can mark as distributed (for templates)"""
        if hasattr(self, '_current_user'):
            user = self._current_user
            # Only SDSA users can mark as distributed for outgoing shipments
            return (user.is_sdsa() and 
                    self.direction == self.Direction.OUT and 
                    self.status == self.Status.RECEIVED_CC and
                    self.cluster in user.managed_clusters.all())
        return False
    
    @property
    def can_mark_posted_for_current_user(self):
        """Property to check if current user can mark as posted (for templates)"""
        if hasattr(self, '_current_user'):
            user = self._current_user
            # Only SDSA users can mark as posted for return shipments
            return (user.is_sdsa() and 
                    self.direction == self.Direction.RET and 
                    self.status == self.Status.RECEIVED_NO and
                    self.cluster in user.managed_clusters.all())
        return False
    
    def can_mark_distributed(self):
        """Check if shipment can be marked as distributed (OUT only)"""
        return (self.direction == self.Direction.OUT and 
                self.status == self.Status.RECEIVED_CC)
    
    def can_mark_posted(self):
        """Check if shipment can be marked as posted (RET only)"""
        return (self.direction == self.Direction.RET and 
                self.status == self.Status.RECEIVED_NO)


class ShipmentItem(models.Model):
    shipment = models.ForeignKey(
        Shipment,
        on_delete=models.CASCADE,
        related_name='items'
    )
    fcp = models.ForeignKey(
        FCP,
        on_delete=models.CASCADE,
        related_name='shipment_items'
    )
    qty_planned = models.PositiveIntegerField()
    qty_received = models.PositiveIntegerField(null=True, blank=True)
    discrepancy_note = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['shipment', 'fcp']
        ordering = ['fcp__code']
    
    def __str__(self):
        return f"{self.shipment} - {self.fcp.code}: {self.qty_planned} planned, {self.qty_received or 0} received"
    
    def clean(self):
        super().clean()
        # Basic validation only
        pass
    
    def save(self, *args, **kwargs):
        # Simple save without validation
        super().save(*args, **kwargs)
    
    @property
    def has_discrepancy(self):
        """Check if there's a discrepancy between planned and received"""
        if self.qty_received is None:
            return False
        return self.qty_received != self.qty_planned
