from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from accounts.models import User


class Cluster(models.Model):
    name = models.CharField(max_length=100, unique=True)
    sdsa_owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': User.Role.SDSA},
        related_name='managed_clusters'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def clean(self):
        super().clean()
        if self.sdsa_owner and self.sdsa_owner.role != User.Role.SDSA:
            raise ValidationError('Only SDSA users can own clusters.')
    
    def get_collection_centre(self):
        """Get the FCP that serves as the collection centre for this cluster."""
        try:
            return self.fcps.get(is_collection_centre=True)
        except FCP.DoesNotExist:
            return None


class FCP(models.Model):
    code = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{2}\d{4}$',
                message='FCP code must be in format: XX0000 (e.g., UG0249)'
            )
        ]
    )
    name = models.CharField(max_length=200, blank=True)
    cluster = models.ForeignKey(
        Cluster, 
        on_delete=models.CASCADE, 
        related_name='fcps'
    )
    is_collection_centre = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['cluster', 'code']
        ordering = ['cluster', 'code']
    
    def __str__(self):
        return f"{self.code} - {self.name or 'Unnamed'}"
    
    def clean(self):
        super().clean()
        if self.is_collection_centre and self.cluster and self.cluster.pk:
            # Check if another FCP in the same cluster is already a collection centre
            existing_cc = FCP.objects.filter(
                cluster=self.cluster,
                is_collection_centre=True
            ).exclude(pk=self.pk)
            
            if existing_cc.exists():
                raise ValidationError(
                    f'Cluster {self.cluster.name} already has a collection centre: {existing_cc.first().code}'
                )
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class CollectionCentreUser(models.Model):
    """Links CC users to their collection centre FCP"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': User.Role.CC},
        related_name='collection_centre'
    )
    fcp = models.OneToOneField(
        FCP,
        on_delete=models.CASCADE,
        limit_choices_to={'is_collection_centre': True},
        related_name='cc_user'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Collection Centre User'
        verbose_name_plural = 'Collection Centre Users'
    
    def __str__(self):
        return f"{self.user.username} -> {self.fcp.code}"
    
    def clean(self):
        super().clean()
        if self.user.role != User.Role.CC:
            raise ValidationError('User must have CC role.')
        if not self.fcp.is_collection_centre:
            raise ValidationError('FCP must be a collection centre.')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
