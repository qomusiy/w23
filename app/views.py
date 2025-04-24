from methodism import METHODISM
from rest_framework import status, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import login, logout
from .models import OTP
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer
from app import methods
import datetime
import random
import uuid
from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings


class Main(METHODISM):
    file = methods
    token_key = "Token"
    not_auth_methods = ['register', 'login']


class RegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Muvaffaqiyatli"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                "message": "Muvaffaqiyatli",
                "token": token.key
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Muvaffaqiyatli"}, status=status.HTTP_200_OK)


class ProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)


class ProfileUpdateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Ma'lumotlar yangilandi"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Ma'lumotlar yangilandi"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response({"message": "Akkount o'chirildi"}, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        user = request.user
        old = request.data.get("old")
        new = request.data.get("new")
        confirm = request.data.get("confirm")

        if not user.check_password(old):
            return Response({"error": "Avvalgi parolda xatolik"}, status=status.HTTP_400_BAD_REQUEST)

        if new != confirm:
            return Response({"error": "Tasdiqlash paroli mos kelmadi."},
                            status=status.HTTP_400_BAD_REQUEST)

        if old == new:
            return Response({"error": "Avvalgi parol va yangi parol bir xil!"},
                            status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new)
        user.save()

        return Response({"success": "Muvaffaqiyatli o'zgartirildi."}, status=status.HTTP_200_OK)


class AuthOne(APIView):
    def post(self, request):
        data = request.data
        if not data['phone']:
            return Response({
                'error': "To'g'ri malumot kiritilmagan"
            })

        if len(str(data['phone'])) != 12 or not isinstance(data['phone'], int) or str(data['phone'])[:3] != '998':
            return Response({
                'error': "Raqam noto'g'ri kiritildi"
            })

        code = ''.join([str(random.randint(1, 9999))[-1] for i in range(4)])
        key = code + uuid.uuid4().__str__()
        otp = OTP.objects.create(phone=data['phone'], key=key)

        return Response({
            'otp': code,
            'token': otp.key
        })


class AuthTwo(APIView):
    def post(self, request):
        data = request.data
        if not data['code'] or not data['key']:
            return Response({
                "error": "Malumotlarni to'liq kiriting!"
            })
        otp = OTP.objects.filter(key=data['key']).first()

        if not otp:
            return Response({
                "Error": "Xato key"
            })

        now = datetime.datetime.now()
        return Response({
            "message": True
        })


def send_mail_page(request):
    context = {}

    if request.method == 'POST':
        address = request.POST.get('address')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if address and subject and message:
            try:
                if '@gmail.com' == address[-10:]:
                    send_mail(subject, message, settings.EMAIL_HOST_USER, [address])
                    print("email")
                    context['message'] = "Emailga jo'natildi"
                else:
                    print(message)
                    context['message'] = 'Raqamga kod yuborildi'
            except Exception as e:
                context['message'] = f'Xatolik: {e}'
        else:
            context['message'] = 'Hamma bolimlarni toldiring'

    return render(request, "index.html", context)
