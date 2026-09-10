import random
import requests
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Verification, Profile

MELIPAYAMAK_USERNAME = "989115299739"
MELIPAYAMAK_APIKEY = "e6d24a13-b319-4037-996f-eb0c26c33ca7"
MELIPAYAMAK_BASE_URL = "https://rest.payamak-panel.com/api/SendSMS/BaseServiceNumber"
MELIPAYAMAK_BODY_ID = 523369


@method_decorator(csrf_exempt, name="dispatch")
class SendCodeView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get("phone")
        if not phone:
            return Response({"error": "شماره موبایل الزامی است"}, status=400)

        phone = str(phone).strip()

        if User.objects.filter(username=phone).exists():
            return Response({"error": "این شماره قبلاً ثبت‌نام شده است"}, status=400)

        code = str(random.randint(1000, 9999))

        payload = {
            "username": MELIPAYAMAK_USERNAME,
            "password": MELIPAYAMAK_APIKEY,
            "text": [code],
            "to": phone,
            "bodyId": MELIPAYAMAK_BODY_ID,
        }

        try:
            r = requests.post(MELIPAYAMAK_BASE_URL, json=payload, timeout=10)
            result = r.json()
        except Exception as e:
            return Response({"error": f"خطای شبکه: {str(e)}"}, status=500)

        if r.status_code != 200 or result.get("RetStatus") != 1:
            return Response(
                {"error": result.get("StrRetStatus", "خطا در ارسال پیامک")},
                status=500,
            )

        Verification.objects.update_or_create(phone=phone, defaults={"code": code})
        return Response({"msg": "کد تایید با موفقیت ارسال شد"})


@method_decorator(csrf_exempt, name="dispatch")
class VerifyCodeView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        phone = str(request.data.get("phone", "")).strip()
        code = str(request.data.get("code", "")).strip()

        if not phone or not code:
            return Response({"error": "شماره و کد الزامی است"}, status=400)

        pending = Verification.objects.filter(phone=phone).first()
        if not pending or pending.code != code:
            return Response({"error": "کد تایید اشتباه است"}, status=400)

        return Response({"msg": "کد تایید صحیح است"})


@method_decorator(csrf_exempt, name="dispatch")
class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get("phone")
        code = request.data.get("code")
        password = request.data.get("password")

        if not all([phone, code, password]):
            return Response({"error": "همه فیلدها الزامی هستند"}, status=400)

        phone = str(phone).strip()
        code = str(code).strip()

        pending = Verification.objects.filter(phone=phone).first()
        if not pending or pending.code != code:
            return Response({"error": "کد تایید نامعتبر یا اشتباه است"}, status=400)

        if User.objects.filter(username=phone).exists():
            pending.delete()
            return Response({"error": "این شماره قبلاً ثبت‌نام شده است"}, status=400)

        user = User.objects.create_user(username=phone, password=password)
        pending.delete()

        login(request, user)
        request.session.set_expiry(432000)
        return Response({"msg": "ثبت‌نام با موفقیت انجام شد", "phone": user.username})


@method_decorator(csrf_exempt, name="dispatch")
class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get("phone")
        password = request.data.get("password")

        if not phone or not password:
            return Response({"error": "شماره و رمز عبور الزامی است"}, status=400)

        user = authenticate(username=phone, password=password)
        if user:
            login(request, user)
            request.session.set_expiry(432000)
            return Response({"msg": "ورود موفقیت‌آمیز بود", "user": {"phone": user.username}})

        return Response({"error": "شماره موبایل یا رمز عبور اشتباه است"}, status=401)


@method_decorator(csrf_exempt, name="dispatch")
class LogoutView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"msg": "خروج با موفقیت انجام شد"})


@method_decorator(csrf_exempt, name="dispatch")
class UserProfileView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile, _ = Profile.objects.get_or_create(user=user)

        data = {
            "phone": user.username,
            "first_name": profile.first_name or "",
            "last_name": profile.last_name or "",
            "email": profile.email or "",
            "national_code": profile.national_code or "",
            "card_number": profile.card_number or "",
            "newsletter": profile.newsletter,
        }
        return Response(data)

    def post(self, request):
        user = request.user
        profile, _ = Profile.objects.get_or_create(user=user)

        profile.first_name = request.data.get("first_name", profile.first_name)
        profile.last_name = request.data.get("last_name", profile.last_name)
        profile.email = request.data.get("email", profile.email)
        profile.national_code = request.data.get("national_code", profile.national_code)
        profile.card_number = request.data.get("card_number", profile.card_number)
        profile.newsletter = request.data.get("newsletter", profile.newsletter)
        profile.save()

        return Response({"msg": "اطلاعات با موفقیت به‌روزرسانی شد"})