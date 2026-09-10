import json
import requests
from django.conf import settings
from django.db.models import Q
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Brand, Cart, CartItem, Category, Comment, Order, OrderItem, Product , ContactMessage
from .serializers import BrandSerializer, CartSerializer, CategorySerializer, ProductSerializer , ContactSerializer


class ShopView(APIView):
  def get(self, request):
    brands = Brand.objects.all()
    categories = Category.objects.all()

    return Response({
        'brands': BrandSerializer(brands, many=True, context={'request': request}).data,
        'categories': CategorySerializer(categories, many=True, context={'request': request}).data,
    })


class BrandListView(APIView):
  def get(self, request):
    brands = Brand.objects.all()
    serializer = BrandSerializer(brands, many=True)
    return Response(serializer.data)


class CategoryListView(APIView):
  def get(self, request):
    categories = Category.objects.all()
    serializer = CategorySerializer(
        categories, many=True, context={'request': request}
    )
    return Response(serializer.data)


class ProductListView(APIView):
  def get(self, request):
    products = Product.objects.all()
    search = request.query_params.get('search')
    if search:
      products = products.filter(
          Q(title__icontains=search) | Q(description__icontains=search)
      )

    brand_id = request.query_params.get('brand')
    if brand_id:
      products = products.filter(brand_id=brand_id)

    category_id = request.query_params.get('category')
    if category_id:
      products = products.filter(category_id=category_id)

    sort = request.query_params.get('sort')
    if sort == 'cheap':
      products = products.order_by('price')
    elif sort == 'expensive':
      products = products.order_by('-price')
    else:
      products = products.order_by('-id')

    serializer = ProductSerializer(
        products, many=True, context={'request': request}
    )
    return Response(serializer.data)


@method_decorator(csrf_exempt, name='dispatch')
class CartView(APIView):
  authentication_classes = [SessionAuthentication]
  permission_classes = [IsAuthenticated]

  def get(self, request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    serializer = CartSerializer(cart, context={'request': request})
    return Response(serializer.data)


@method_decorator(csrf_exempt, name='dispatch')
class AddToCartView(APIView):
  authentication_classes = [SessionAuthentication]
  permission_classes = [IsAuthenticated]

  def post(self, request):
    product_id = request.data.get('product_id')
    if not product_id:
      return Response({'error': 'شناسه محصول الزامی است'}, status=400)

    try:
      product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
      return Response({'error': 'محصول مورد نظر یافت نشد'}, status=404)

    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, product=product
    )

    if not created:
      cart_item.quantity += 1
      cart_item.save()

    return Response({'msg': 'محصول به سبد اضافه شد'})


@method_decorator(csrf_exempt, name='dispatch')
class UpdateCartItemView(APIView):
  authentication_classes = [SessionAuthentication]
  permission_classes = [IsAuthenticated]

  def post(self, request):
    item_id = request.data.get('item_id')
    action = request.data.get('action')

    try:
      cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
    except CartItem.DoesNotExist:
      return Response({'error': 'آیتم یافت نشد'}, status=404)

    if action == 'increase':
      cart_item.quantity += 1
      cart_item.save()
    elif action == 'decrease':
      if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
      else:
        cart_item.delete()
    elif action == 'remove':
      cart_item.delete()

    cart = Cart.objects.get(user=request.user)
    serializer = CartSerializer(cart, context={'request': request})
    return Response(serializer.data)


class ProductDetailView(APIView):
  def get(self, request, slug):
    try:
      product = Product.objects.get(slug=slug)
    except Product.DoesNotExist:
      return Response({'error': 'یافت نشد'}, status=404)

    comments = []
    for c in product.comments.filter(is_approved=True):
      avatar_url = (
          request.build_absolute_uri(c.avatar.url)
          if c.avatar and hasattr(c.avatar, 'url')
          else None
      )
      comments.append(
          {'name': c.name, 'text': c.text, 'avatar': avatar_url}
      )

    image1_url = None
    if product.image1 and hasattr(product.image1, 'url'):
      try:
        image1_url = request.build_absolute_uri(product.image1.url)
      except ValueError:
        image1_url = None

    data = {
        'id': product.id,
        'title': product.title,
        'slug': product.slug,
        'price': product.price,
        'description': product.description,
        'image1': image1_url,
        'comments': comments,
    }
    return Response(data)

  def post(self, request, slug):
    try:
      product = Product.objects.get(slug=slug)
    except Product.DoesNotExist:
      return Response({'error': 'یافت نشد'}, status=404)

    Comment.objects.create(
        product=product,
        name=request.data.get('name'),
        text=request.data.get('text'),
        avatar=request.FILES.get('avatar'),
        is_approved=False,
    )
    return Response({'msg': 'ثبت شد'})


if settings.SANDBOX:
  ZP_API_REQUEST = 'https://sandbox.zarinpal.com/pg/v4/payment/request.json'
  ZP_API_VERIFY = 'https://sandbox.zarinpal.com/pg/v4/payment/verify.json'
  ZP_API_STARTPAY = 'https://sandbox.zarinpal.com/pg/StartPay/'
else:
  ZP_API_REQUEST = 'https://api.zarinpal.com/pg/v4/payment/request.json'
  ZP_API_VERIFY = 'https://api.zarinpal.com/pg/v4/payment/verify.json'
  ZP_API_STARTPAY = 'https://www.zarinpal.com/pg/StartPay/'


@api_view(['POST'])
def send_request(request):
  data = request.data
  amount = int(data.get('amount', 0))
  items_data = data.get('items', [])

  if not items_data or amount <= 0:
    return Response(
        {'status': False, 'code': 'سبد خرید خالی است یا مبلغ نامعتبر است'}
    )

  order = Order.objects.create(
      user=request.user if request.user.is_authenticated else None,
      first_name=data.get('first_name', ''),
      last_name=data.get('last_name', ''),
      national_code=data.get('national_code', ''),
      phone_number=data.get('phone_number', ''),
      province=data.get('province', ''),
      city=data.get('city', ''),
      postal_code=data.get('postal_code', ''),
      address_detail=data.get('address_detail', ''),
      total_price=amount,
      is_paid=False,
  )

  for item in items_data:
    product_id = item.get('product') or item.get('product_id') or item.get('id')
    quantity = item.get('quantity', 1)

    try:
      product = Product.objects.get(id=product_id)
      OrderItem.objects.create(
          order=order, product=product, quantity=quantity, price=product.price
      )
    except Product.DoesNotExist:
      continue

  request.session['pending_order_id'] = order.id
  CallbackURL = f'http://127.0.0.1:8000/api/verify/?order_id={order.id}'

  z_data = {
      'merchant_id': settings.MERCHANT,
      'amount': amount,
      'description': f'خرید از فروشگاه - سفارش {order.order_number}',
      'callback_url': CallbackURL,
  }
  z_data = json.dumps(z_data)
  headers = {
      'content-type': 'application/json',
      'content-length': str(len(z_data)),
  }

  try:
    response = requests.post(
        ZP_API_REQUEST, data=z_data, headers=headers, timeout=10
    )
    if response.status_code == 200:
      res_data = response.json()
      if res_data.get('data') and res_data['data'].get('code') == 100:
        authority = res_data['data']['authority']
        payment_url = ZP_API_STARTPAY + str(authority)
        return Response({'status': True, 'url': payment_url})
      else:
        errors = res_data.get('errors', 'خطای ناشناخته')
        return Response({'status': False, 'code': str(errors)})
    return Response(
        {'status': False, 'code': f'invalid response: {response.status_code}'}
    )
  except requests.exceptions.RequestException:
    return Response({'status': False, 'code': 'connection error'})


@api_view(['GET', 'POST'])
def verify(request):
    authority = request.GET.get('Authority')
    status = request.GET.get('Status')
    order_id = request.GET.get('order_id') or request.session.get('pending_order_id')

    try:
        order = Order.objects.get(id=order_id)
    except (Order.DoesNotExist, ValueError, TypeError):
        return redirect('http://localhost:5173/payment-failed?code=notfound')

    if status == 'OK':
        data = {
            'merchant_id': settings.MERCHANT,
            'amount': int(order.total_price),
            'authority': authority,
        }
        data = json.dumps(data)
        headers = {
            'content-type': 'application/json',
            'content-length': str(len(data)),
        }
        response = requests.post(ZP_API_VERIFY, data=data, headers=headers)

        if response.status_code == 200:
            res_data = response.json()
            if res_data.get('data') and res_data['data'].get('code') in (100, 101):
                ref_id = res_data['data']['ref_id']

                order.is_paid = True
                order.ref_id = str(ref_id)
                order.save()

                target_user = order.user if order.user else request.user
                if target_user and target_user.is_authenticated:
                    carts = Cart.objects.filter(user=target_user)
                    for cart in carts:
                        cart.items.all().delete()
                    carts.delete()

                if 'pending_order_id' in request.session:
                    del request.session['pending_order_id']

                return redirect(f'http://localhost:5173/payment-success?ref_id={ref_id}')
            else:
                error_code = res_data.get('errors', {}).get('code', 'unknown')
                return redirect(f'http://localhost:5173/payment-failed?code={error_code}')

    return redirect('http://localhost:5173/payment-failed?code=cancelled')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_orders_api(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    data = []
    for order in orders:
        data.append({
            "id": order.id,
            "order_number": order.order_number,
            "created_at": order.created_at.strftime('%Y/%m/%d - %H:%M'),
            "total_price": order.total_price,
            "status": order.status_text if hasattr(order, 'status_text') else ("پرداخت شده" if order.is_paid else "در انتظار پرداخت")
        })
    return Response(data)




class ContactAPIView(APIView):
    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)