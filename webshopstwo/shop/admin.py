from django.contrib import admin
from .models import Brand, Category, Product, Cart, CartItem, Order, OrderItem, Comment  ,ContactMessage

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'brand', 'category', 'price')
    fields = ('title', 'brand', 'category', 'price', 'description', 'image1', 'image2', 'image3', 'image4')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ('product', 'quantity', 'price', 'get_total_price')
    readonly_fields = ('product', 'price', 'get_total_price')
    extra = 0
    can_delete = False

    def get_total_price(self, obj):
        if obj.price is not None and obj.quantity is not None:
            return obj.price * obj.quantity
        return 0
    get_total_price.short_description = 'قیمت کل'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'first_name', 'last_name', 'total_price', 'status_text', 'is_paid', 'created_at')
    list_filter = ('is_paid', 'created_at')
    search_fields = ('order_number', 'first_name', 'last_name', 'phone_number')
    list_editable = ('status_text',)
    inlines = [OrderItemInline]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'product', 'is_approved')
    list_filter = ('is_approved',)



admin.site.register(ContactMessage) 