from django.db import models
from django.contrib.auth.models import AbstractUser
from django.forms.models import model_to_dict
from django.utils import timezone
# Create your models here.
class Supplier(models.Model):
    name = models.TextField(null=False, max_length=255, unique=True)
    contact_person = models.TextField(null=False, max_length=255)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(unique=True, null=False)
    photo = models.ImageField(upload_to='supplier-photo/', null=True)
    supplied_item = models.IntegerField( default=0)
    def __str__(self):
        return f'{self.name} - {self.contact_person}'
    def to_dict(self):
        return model_to_dict(self)
    
class Category(models.Model):
    class CategoryStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'Inactive'
    name = models.TextField(max_length=100, unique=True, null=False)
    category_fav_icon = models.TextField(max_length=100, null=False, default='fa-solid fa-icons')
    image_name = models.TextField(max_length=150)
    status = models.CharField(max_length=30, choices=CategoryStatus.choices, default=CategoryStatus.INACTIVE)
    def __str__(self):
        return f'{self.name}'
    
class Product(models.Model):
    name = models.TextField(max_length=255, null=False)
    category = models.ForeignKey(Category, on_delete=models.PROTECT )
    stock = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=4, null=False, default=0.0000)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    product_image = models.ImageField(upload_to='product-image/')
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f"{self.name}" 
    

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile-images/', null=True, blank=True)
    emails_verified = models.BooleanField(default=True)
    USERNAME_FIELD = 'email'  #using email as the primary login field
    REQUIRED_FIELDS = ['username']  #'username' required when creating users

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_set",  # Prevents clashes
        blank=True
    )
    
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions_set",  # Prevents clashes
        blank=True
    )

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith("pbkdf2_"):
            self.set_password(self.password)
        return super().save(*args, **kwargs)
