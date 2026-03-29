from django.contrib import admin
from django.utils.html import format_html
from .models import UserProfile,Category,Product,CartItem,Coupon,OrderItem,Testimonial,Contact

# Register your models here.
admin.site.register(UserProfile)

admin.site.register(Category)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'is_featured', 'card_image_preview']
    list_filter = ['is_featured', 'category']
    list_editable = ['is_featured']
    readonly_fields = ['card_image_preview', 'detail_image_preview']
    
    def card_image_preview(self, obj):
        if obj.card_image:
            return format_html(
                '<img src="{}" style="max-height:100px;max-width:100px;object-fit:cover;border-radius:4px"/>', 
                obj.card_image.url
            )
        return "No Image"
    card_image_preview.short_description = "Card Image"
    
    def detail_image_preview(self, obj):
        if obj.detail_image:
            return format_html(
                '<img src="{}" style="max-height:100px;max-width:100px;object-fit:cover;border-radius:4px"/>', 
                obj.detail_image.url
            )
        return "No Image"
    detail_image_preview.short_description = "Detail Image"
admin.site.register(CartItem)
admin.site.register(Coupon)
admin.site.register(OrderItem)
admin.site.register(Testimonial)
admin.site.register(Contact)