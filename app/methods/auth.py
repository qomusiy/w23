from rest_framework import status, permissions
from methodism import custom_response, error_messages, MESSAGE

from app.models import CustomUser
from app.serializers import RegisterSerializer, UserSerializer
from rest_framework.authtoken.models import Token


def register(request, params):
    # serializer = RegisterSerializer(data=params)
    # if serializer.is_valid():
    #     serializer.save()
    #     return custom_response({"message": "Muvaffaqiyatli"}, status=status.HTTP_201_CREATED)
    # return custom_response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return {"message": "Muvaffaqiyatli"} 


def login(request, params):
    if 'phone' not in params:
        return custom_response(False, error_messages.error_params_unfilled('phone'))
    user = CustomUser.objects.filter(phone=params['phone']).first()
    token, created = Token.objects.get_or_create(user=user)
    
    if not user:
        return custom_response(status=False, message=MESSAGE['UserPasswordError'])
    return custom_response(status=True, data={"token": token.key}, message={"nimadur":'karoche oxshadi'})


def logout(request, params):
    permission_classes = [permissions.IsAuthenticated]
    logout(request)
    return custom_response({"message": "Muvaffaqiyatli"}, status=status.HTTP_200_OK)


def profil(request, params):
    user = request.user
    serializer = UserSerializer(user)
    return custom_response(serializer.data)


def profil_update(request, params):
    user = request.user
    serializer = UserSerializer(user, data=params)
    if serializer.is_valid():
        serializer.save()
        return custom_response({"message": "Ma'lumotlar yangilandi"}, status=status.HTTP_200_OK)
    return custom_response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def profil_delete(request, params):
    user = request.user
    user.delete()
    return custom_response({"message": "Akkount o'chirildi"}, status=status.HTTP_200_OK)


def change_password(request, params):
    user = request.user
    old = params.get("old")
    new = params.get("new")
    confirm = params.get("confirm")

    if not user.check_password(old):
        return custom_response({"error": "Avvalgi parolda xatolik"}, status=status.HTTP_400_BAD_REQUEST)

    if new != confirm:
        return custom_response({"error": "Tasdiqlash paroli mos kelmadi."},
                               status=status.HTTP_400_BAD_REQUEST)

    if old == new:
        return custom_response({"error": "Avvalgi parol va yangi parol bir xil!"},
                               status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new)
    user.save()

    return custom_response({"success": "Muvaffaqiyatli o'zgartirildi."}, status=status.HTTP_200_OK)
