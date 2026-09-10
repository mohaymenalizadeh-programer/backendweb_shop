from rest_framework import serializers
from .models import Brand, Category, Product, Cart, CartItem , ContactMessage

class BrandSerializer(serializers.ModelSerializer):
    imagesbrand = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = "__all__"

    def get_imagesbrand(self, obj):
        request = self.context.get('request')
        if obj.imagesbrand:
            if request is not None:
                return request.build_absolute_uri(obj.imagesbrand.url)
            return obj.imagesbrand.url
        return None


class CategorySerializer(serializers.ModelSerializer):
    imgcategory = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = "__all__"

    def get_imgcategory(self, obj):
        request = self.context.get('request')
        if obj.imgcategory:
            if request is not None:
                return request.build_absolute_uri(obj.imgcategory.url)
            return obj.imgcategory.url
        return None


class ProductSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source="brand.title", read_only=True)
    category_name = serializers.CharField(source="category.title", read_only=True)
    image1 = serializers.SerializerMethodField()
    image2 = serializers.SerializerMethodField()
    image3 = serializers.SerializerMethodField()
    image4 = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "title", "slug", "description", "price",
            "brand", "brand_name", "category", "category_name",
            "created_at", "image1", "image2", "image3", "image4"
        ]

    def get_image_url(self, image_field):
        request = self.context.get('request')
        if image_field:
            if request is not None:
                return request.build_absolute_uri(image_field.url)
            return image_field.url
        return None

    def get_image1(self, obj):
        return self.get_image_url(obj.image1)

    def get_image2(self, obj):
        return self.get_image_url(obj.image2)

    def get_image3(self, obj):
        return self.get_image_url(obj.image3)

    def get_image4(self, obj):
        return self.get_image_url(obj.image4)


class CartItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source="product.title", read_only=True)
    product_slug = serializers.CharField(source="product.slug", read_only=True)
    product_price = serializers.IntegerField(source="product.price", read_only=True)
    product_image = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_title", "product_slug", "product_price", "product_image", "quantity", "total_price"]

    def get_product_image(self, obj):
        request = self.context.get('request')
        if obj.product.image1:
            if request is not None:
                return request.build_absolute_uri(obj.product.image1.url)
            return obj.product.image1.url
        return None

    def get_total_price(self, obj):
        return obj.product.price * obj.quantity


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    grand_total = serializers.SerializerMethodField()
    total_items_count = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "user", "items", "grand_total", "total_items_count", "created_at"]

    def get_grand_total(self, obj):
        return sum(item.product.price * item.quantity for item in obj.items.all())

    def get_total_items_count(self, obj):
        return sum(item.quantity for item in obj.items.all())
    


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = '__all__'    