import uuid
import random
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Brand(models.Model):
    title = models.CharField(max_length=100)
    imagesbrand = models.ImageField(upload_to="images/", blank=True, null=True)
    slug = models.SlugField(max_length=120, unique=True, allow_unicode=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Category(models.Model):
    title = models.CharField(max_length=100)
    imgcategory = models.ImageField(upload_to="images/", blank=True, null=True)
    slug = models.SlugField(max_length=120, unique=True, allow_unicode=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=150, unique=True, blank=True, null=True, allow_unicode=True)
    description = models.TextField()
    price = models.IntegerField()
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    created_at = models.DateTimeField(auto_now_add=True)
    image1 = models.ImageField(upload_to="images/", blank=True, null=True)
    image2 = models.ImageField(upload_to="images/", blank=True, null=True)
    image3 = models.ImageField(upload_to="images/", blank=True, null=True)
    image4 = models.ImageField(upload_to="images/", blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = f"{slugify(self.brand.title, allow_unicode=True)}-{slugify(self.title[:30], allow_unicode=True)}"
            self.slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand.title} - {self.title}"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="کاربر")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    def __str__(self):
        return f"سبد خرید کاربر: {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="کاربر")
    order_number = models.CharField(max_length=5, unique=True, blank=True, verbose_name="شماره سفارش")
    first_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="نام")
    last_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="نام خانوادگی")
    national_code = models.CharField(max_length=10, verbose_name="کد ملی")
    phone_number = models.CharField(max_length=11, verbose_name="شماره تماس")
    province = models.CharField(max_length=100, verbose_name="استان")
    city = models.CharField(max_length=100, null=True, blank=True, verbose_name="شهر")
    postal_code = models.CharField(max_length=10, verbose_name="کد پستی")
    address_detail = models.TextField(null=True, blank=True, verbose_name="جزئیات آدرس")
    total_price = models.IntegerField(verbose_name="مبلغ کل (تومان)")
    is_paid = models.BooleanField(default=False, verbose_name="وضعیت پرداخت")
    status_text = models.CharField(max_length=100, default="در انتظار پردازش", verbose_name="وضعیت سفارش")
    ref_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="کد پیگیری تراکنش")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت سفارش")

    def save(self, *args, **kwargs):
        if not self.order_number:
            while True:
                num = str(random.randint(10000, 99999))
                if not Order.objects.filter(order_number=num).exists():
                    self.order_number = num
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"سفارش {self.order_number} - {self.first_name} {self.last_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.IntegerField()

    def __str__(self):
        return f"{self.quantity} عدد از {self.product.title}"


class Comment(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    text = models.TextField()
    is_approved = models.BooleanField(default=False)





class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    subject = models.CharField(max_length=50)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"