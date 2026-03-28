from django.contrib import admin
from .models import UserProfile,Category,Product,CartItem,Coupon,OrderItem,Testimonial,Contact

# Register your models here.
admin.site.register(UserProfile)

admin.site.register(Category)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'is_featured']
    list_filter = ['is_featured', 'category']
    list_editable = ['is_featured']
admin.site.register(CartItem)
admin.site.register(Coupon)
admin.site.register(OrderItem)
admin.site.register(Testimonial)
admin.site.register(Contact)