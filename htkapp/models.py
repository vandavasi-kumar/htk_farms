from django.db import models
from cloudinary.models import CloudinaryField

# Create your models here.
from django.contrib.auth.models import User
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    phone = models.CharField(max_length=15)
    country_code = models.CharField(max_length=5)
    email_verified = models.BooleanField(default=False)

    # 🔥 ADD THESE NEW FIELDS
    full_name = models.CharField(max_length=100, blank=True)

    address_line1 = models.CharField(max_length=200, blank=True)
    address_line2 = models.CharField(max_length=200, blank=True)

    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=6, blank=True)

    def __str__(self):
        return self.user.username
    
    


class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Product(models.Model):

    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # card_image = models.ImageField(upload_to="products/cards/")
    # detail_image = models.ImageField(upload_to="products/details/")
    card_image = CloudinaryField('image')
    detail_image = CloudinaryField('image')
    description = models.TextField()
    stock = models.IntegerField()
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    @property
    def total_price(self):
        return self.product.price * self.quantity
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
    

class Order(models.Model):

    STATUS_CHOICES = [
        ('placed', 'Placed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    total_price = models.FloatField()
    address = models.TextField()
    phone = models.CharField(max_length=15)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='placed'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Order {self.id} - {self.status}"
    @property
    def total(self):
        return self.quantity * self.price




#coupon code section
class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    min_order_amount = models.IntegerField(default=0)
    max_discount = models.IntegerField(default=0)
    discount_percent = models.IntegerField()  
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"
    @property
    def total(self):
        return self.quantity * self.price
    
from django.db import models

class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    message = models.TextField()
    rating = models.IntegerField(default=5)
    # image = models.ImageField(upload_to='testimonials/', null=True, blank=True)  # ✅ NEW
    image = CloudinaryField('image', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name