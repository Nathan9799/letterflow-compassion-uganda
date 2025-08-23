from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        SDSA = 'SDSA', 'SDSA'
        CC = 'CC', 'Collection Centre'
    
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.ADMIN
    )
    must_change_password = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_admin(self):
        return self.role == self.Role.ADMIN
    
    def is_sdsa(self):
        return self.role == self.Role.SDSA
    
    def is_collection_centre(self):
        return self.role == self.Role.CC
    
    def clean(self):
        super().clean()
        if self.role == self.Role.CC and not hasattr(self, 'collection_centre'):
            # CC users must be linked to a collection centre FCP
            pass  # This will be handled in the view/form level
