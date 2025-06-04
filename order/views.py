from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import OrderModel, OrderItemModel
from .serializers import OrderModelSerializer, OrderItemModelSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    methods=['POST'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['product', 'market', 'user_address'],
        properties={
            'product': openapi.Schema(type=openapi.TYPE_INTEGER, description='Product ID'),
            'market': openapi.Schema(type=openapi.TYPE_INTEGER, description='Market ID'),
            'user_address': openapi.Schema(type=openapi.TYPE_INTEGER, description='User Address ID'),
            'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Quantity of product', default=1)
        }
    ),
    responses={
        201: openapi.Response(
            description="Order created successfully",
            schema=OrderModelSerializer
        ),
        400: "Bad Request",
        401: "Unauthorized"
    },
    operation_description="Create a new order"
)
@api_view(['POST'])
def create_order(request):
    user = request.user
    if not user.is_authenticated:
        return Response({"error": "Avtorizatsiyadan o'ting"}, status=status.HTTP_401_UNAUTHORIZED)

    product_id = request.data.get('product')
    market_id = request.data.get('market')
    user_address_id = request.data.get('user_address')
    quantity = request.data.get('quantity', 1)

    if not all([product_id, market_id, user_address_id]):
        return Response({"error": "product, market, user_address kerak"}, status=status.HTTP_400_BAD_REQUEST)

    order = OrderModel.objects.create(
            product_id=product_id,
            user=user,
            market_id=market_id,
            user_address_id=user_address_id
    ) 
    if not order:
        return Response({"error": {"Invalid credentials"}}, status=status.HTTP_400_BAD_REQUEST)
    
    OrderItemModel.objects.create(
            order=order,
            product_id=product_id,
            quantity=quantity
    )
    serializer = OrderModelSerializer(order)
    return Response({"new_order": serializer.data}, status=status.HTTP_201_CREATED)

@swagger_auto_schema(
    methods=['GET'],
    responses={
        200: openapi.Response(
            description="List of user's orders",
            schema=OrderModelSerializer(many=True)
        ),
        401: "Unauthorized"
    },
    operation_description="Get list of all orders for the authenticated user"
)
@api_view(['GET'])
def list_orders(request):
    user = request.user
    if not user.is_authenticated:
        return Response({"error": "Avtorizatsiyadan o'ting"}, status=status.HTTP_401_UNAUTHORIZED)

    orders = OrderModel.objects.filter(user=user).order_by('-created_at')
    serializer = OrderModelSerializer(orders, many=True)
    return Response({"orders": serializer.data}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    methods=['GET'],
    responses={
        200: openapi.Response(
            description="Order details",
            schema=OrderModelSerializer
        ),
        401: "Unauthorized",
        404: "Order not found"
    },
    operation_description="Get detailed information about a specific order"
)
@api_view(['GET'])
def order_detail(request, pk):
    user = request.user
    if not user.is_authenticated:
        return Response({"error": "Avtorizatsiyadan o'ting"}, status=status.HTTP_401_UNAUTHORIZED)

    order = OrderModel.objects.get(id=pk, user=user)
    if not order:
        return Response({"error": "Order topilmadi"}, status=status.HTTP_404_NOT_FOUND)

    serializer = OrderModelSerializer(order)
    return Response({"order": serializer.data}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    methods=['PATCH'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'product': openapi.Schema(type=openapi.TYPE_INTEGER, description='Product ID'),
            'market': openapi.Schema(type=openapi.TYPE_INTEGER, description='Market ID'),
            'user_address': openapi.Schema(type=openapi.TYPE_INTEGER, description='User Address ID')
        }
    ),
    responses={
        200: openapi.Response(
            description="Order updated successfully",
            schema=OrderModelSerializer
        ),
        400: "Bad Request",
        401: "Unauthorized",
        404: "Order not found"
    },
    operation_description="Update an existing order"
)
@api_view(['PATCH'])
def update_order(request, pk):
    user = request.user
    if not user.is_authenticated:
        return Response({"error": "Avtorizatsiyadan o'ting"}, status=status.HTTP_401_UNAUTHORIZED)

    order = OrderModel.objects.get(id=pk, user=user)
    if not order:
        return Response({"error": "Order topilmadi"}, status=status.HTTP_404_NOT_FOUND)
    product_id = request.data.get('product')
    market_id = request.data.get('market')
    user_address_id = request.data.get('user_address')

    if product_id:
        order.product_id = product_id
    if market_id:
        order.market_id = market_id
    if user_address_id:
        order.user_address_id = user_address_id
    order.save()
    serializer = OrderModelSerializer(order)
    return Response({"message": "Order updated", "order": serializer.data}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    methods=['DELETE'],
    responses={
        200: "Order deleted successfully",
        401: "Unauthorized",
        404: "Order not found"
    },
    operation_description="Delete an order"
)
@api_view(['DELETE'])
def delete_order(request, pk):
    user = request.user
    if not user.is_authenticated:
        return Response({"error": "Avtorizatsiyadan o'ting"}, status=status.HTTP_401_UNAUTHORIZED)

    order = OrderModel.objects.get(id=pk, user=user)
    if not order:
        return Response({"error": "Order topilmadi"}, status=status.HTTP_404_NOT_FOUND)

    order.delete()
    return Response({"message": "Order deleted"}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    methods=['PATCH'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['quantity'],
        properties={
            'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='New quantity for the order item')
        }
    ),
    responses={
        200: openapi.Response(
            description="Order item updated successfully",
            schema=OrderItemModelSerializer
        ),
        400: "Bad Request",
        401: "Unauthorized",
        404: "Order item not found"
    },
    operation_description="Update quantity of an order item"
)
@api_view(['PATCH'])
def update_order_item(request, pk):
    user = request.user
    if not user.is_authenticated:
        return Response({"error": "Avtorizatsiyadan o'ting"}, status=status.HTTP_401_UNAUTHORIZED)

    order_item = OrderItemModel.objects.get(id=pk, order__user=user)
    if not order_item:
        return Response({"error": "Order Item topilmadi"}, status=status.HTTP_404_NOT_FOUND)

    quantity = request.data.get('quantity')
    if quantity:
        order_item.quantity = quantity
        order_item.save()

    serializer = OrderItemModelSerializer(order_item)
    return Response({"message": "Order Item updated", "order_item": serializer.data}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    methods=['DELETE'],
    responses={
        200: "Order item deleted successfully",
        401: "Unauthorized",
        404: "Order item not found"
    },
    operation_description="Delete an order item"
)
@api_view(['DELETE'])
def delete_order_item(request, pk):
    user = request.user
    if not user.is_authenticated:
        return Response({"error": "Avtorizatsiyadan o'ting"}, status=status.HTTP_401_UNAUTHORIZED)

    order_item = OrderItemModel.objects.get(id=pk, order__user=user)
    if not order_item:
        return Response({"error": "Order Item topilmadi"}, status=status.HTTP_404_NOT_FOUND)

    order_item.delete()
    return Response({"message": "Order Item deleted"}, status=status.HTTP_200_OK)
