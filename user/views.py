from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import UserAddress, OTP
from django.contrib.auth import get_user_model
from .serializer import UserSerializer, UserUpdateSerializer, UserAddressSerializer, OTPSerializer
from random import randint
from django.views.decorators.csrf import csrf_exempt
from random import randint
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg import openapi


User = get_user_model()

@swagger_auto_schema(
    methods=['POST'],
    request_body=UserSerializer,
    responses={
        201: openapi.Response(
            description="User created successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'otp_key': openapi.Schema(type=openapi.TYPE_STRING, description='OTP key for verification')
                }
            )
        ),
        400: "Bad Request"
    },
    operation_description="Register a new user"
)
@api_view(['POST'])
def signup(request):
    data = request.data
    serializer = UserSerializer(data=data)
    password = data.get('password')
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    user = serializer.save()
    otp_code_new = randint(1000, 9999)
    otp = OTP.objects.create(user=user, code=otp_code_new)
    user.set_password(password)
    user.save()
    print(f"Generated OTP Code: {otp_code_new}")
    return Response({"otp_key": str(otp.key)}, status=status.HTTP_201_CREATED)

@swagger_auto_schema(
    methods=['POST'],
    request_body=OTPSerializer,
    responses={
        200: openapi.Response(
            description="OTP verified successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message')
                }
            )
        ),
        400: "Bad Request",
        404: "OTP not found"
    },
    operation_description="Verify OTP code"
)
@api_view(http_method_names=['POST'])
def verify_otp(request):
    data = request.data
    serializer = OTPSerializer(data=data)
    if not serializer.is_valid():
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    otp = OTP.objects.filter(key=data['key']).first()
    if not otp:
        return Response({"error": "OTP not found"}, status=status.HTTP_404_NOT_FOUND)
    if int(otp.code) != int(data['otp_code']):
        return Response({"error": "OTP invalid"}, status=status.HTTP_400_BAD_REQUEST)
    if timezone.now() - otp.created_at > timedelta(seconds=60):
        return Response(data={"error": "Your OTP has expired, please request a new one!"}, status=status.HTTP_400_BAD_REQUEST)
    otp.user.is_verify = True
    otp.user.save()
    otp.delete()
    return Response({"message": "OTP verified"}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    methods=['PATCH'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['old_password', 'new_password', 'confirm_password'],
        properties={
            'old_password': openapi.Schema(type=openapi.TYPE_STRING, description='Current password'),
            'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='New password'),
            'confirm_password': openapi.Schema(type=openapi.TYPE_STRING, description='Confirm new password')
        }
    ),
    responses={
        200: "Password updated successfully",
        400: "Bad Request",
        401: "Unauthorized"
    },
    operation_description="Update user password"
)
@api_view(http_method_names=['PATCH'])
def update_password(request):
    user = request.user
    data = request.data
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    if not user.check_password(old_password):
        return Response({'error': 'Eski parol wron'}, status=status.HTTP_400_BAD_REQUEST)
    if new_password != confirm_password:
        return Response({'error': 'New password confirm password bilan tengmas'}, status=status.HTTP_400_BAD_REQUEST)
    user.set_password(new_password)
    user.save()
    return Response({'message': 'Successfully'}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    methods=['POST'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'password'],
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password')
        }
    ),
    responses={
        200: openapi.Response(
            description="Login successful",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
                    'access': openapi.Schema(type=openapi.TYPE_STRING, description='Access token')
                }
            )
        ),
        401: "Invalid credentials",
        403: "Account not verified"
    },
    operation_description="User login"
)
@api_view(http_method_names=['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if not user:
        return Response({'message': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)
    if not user.is_verify:
        return Response({'message': 'Account not verified. Please verify your OTP.'}, status=status.HTTP_403_FORBIDDEN)
    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token
    return Response({'refresh': str(refresh), 'access': str(access_token)}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    methods=['GET'],
    responses={
        200: openapi.Response(
            description="User profile retrieved successfully",
            schema=UserSerializer
        ),
        401: "Unauthorized"
    },
    operation_description="Get current user profile"
)
@api_view(['GET'])
def me(request):
    if not request.user.is_authenticated:
         return Response({"message": "Требуется авторизация"}, status=status.HTTP_401_UNAUTHORIZED)
    serializer = UserSerializer(request.user)
    return Response({"data": serializer.data}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    methods=['POST'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['phone'],
        properties={
            'phone': openapi.Schema(type=openapi.TYPE_STRING, description='Phone number')
        }
    ),
    responses={
        200: openapi.Response(
            description="Password reset OTP sent",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message'),
                    'otp': openapi.Schema(type=openapi.TYPE_INTEGER, description='OTP code')
                }
            )
        ),
        400: "Bad Request",
        401: "Unauthorized",
        404: "User not found"
    },
    operation_description="Request password reset OTP"
)
@api_view(['POST'])
def reset_password(request):
    if not request.user.is_authenticated:
         return Response({"message": "Требуется авторизация"}, status=status.HTTP_401_UNAUTHORIZED)
    phone = request.data.get('phone')
    if not phone:
        return Response({"message": "Phone shart"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(phone=phone)
    except User.DoesNotExist:
        return Response({"message": "Invalid credentials"}, status=status.HTTP_404_NOT_FOUND)
    otp_code = randint(100000, 999999)
    OTP.objects.create(user=user, code=otp_code)
    return Response({"message": "Parol reset uchun OTP yuborildi", "otp": otp_code}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    methods=['PATCH'],
    request_body=UserUpdateSerializer,
    responses={
        200: openapi.Response(
            description="User updated successfully",
            schema=UserSerializer
        ),
        400: "Bad Request",
        401: "Unauthorized"
    },
    operation_description="Update user profile"
)
@api_view(['PATCH'])
def update_user(request):
    if not request.user.is_authenticated:
         return Response({"message": "Требуется авторизация"}, status=status.HTTP_401_UNAUTHORIZED)
    serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        user = serializer.save()
        return Response({"message": "User is updated", "data": UserSerializer(user).data}, status=status.HTTP_200_OK)
    return Response({"message": "Invalid credentials", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



# UserAdress
@swagger_auto_schema(
    methods=['POST'],
    request_body=UserAddressSerializer,
    responses={
        201: openapi.Response(
            description="Address created successfully",
            schema=UserAddressSerializer
        ),
        400: "Bad Request",
        401: "Unauthorized"
    },
    operation_description="Create new user address"
)
@api_view(['POST'])
def create_address(request):
    if not request.user.is_authenticated:
         return Response({"message": "Требуется авторизация"}, status=status.HTTP_401_UNAUTHORIZED)
    serializer = UserAddressSerializer(data=request.data)
    if serializer.is_valid():
        addr = serializer.save(user=request.user)
        return Response({"message": "UserAdress is created", "data": UserAddressSerializer(addr).data}, status=status.HTTP_201_CREATED)
    return Response({"message": "Invalid credentials", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    methods=['GET'],
    responses={
        200: openapi.Response(
            description="List of user addresses",
            schema=UserAddressSerializer(many=True)
        ),
        401: "Unauthorized"
    },
    operation_description="Get list of user addresses"
)
@api_view(['GET'])
def list_addresses(request):
    qs = UserAddress.objects.filter(user=request.user)
    return Response({"data": UserAddressSerializer(qs, many=True).data}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    methods=['PUT'],
    request_body=UserAddressSerializer,
    responses={
        200: openapi.Response(
            description="Address updated successfully",
            schema=UserAddressSerializer
        ),
        400: "Bad Request",
        401: "Unauthorized",
        404: "Address not found"
    },
    operation_description="Update user address"
)
@api_view(['PUT'])
def update_address(request, pk):
    addr = get_object_or_404(UserAddress, pk=pk, user=request.user)
    serializer = UserAddressSerializer(addr, data=request.data, partial=True)
    if serializer.is_valid():
        addr = serializer.save()
        addr.save()
        return Response({"message": "UserAdress updated", "data": UserAddressSerializer(addr).data}, status=status.HTTP_200_OK)
    return Response({"message": "Invalid credentials", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    methods=['DELETE'],
    responses={
        204: "Address deleted successfully",
        401: "Unauthorized",
        404: "Address not found"
    },
    operation_description="Delete user address"
)
@api_view(['DELETE'])
def delete_address(request, pk):
    addr = get_object_or_404(UserAddress, pk=pk, user=request.user)
    addr.delete()
    addr.save()
    return Response({"message": "Deleted"}, status=status.HTTP_204_NO_CONTENT)
