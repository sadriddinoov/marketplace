from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import ProductModel
from .serializers import ProductModelSerializer
from django.db.models import Q, Avg, Count
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    methods=['POST'],
    request_body=ProductModelSerializer,
    responses={
        201: openapi.Response(
            description="Product created successfully",
            schema=ProductModelSerializer
        ),
        400: "Bad Request",
        401: "Unauthorized"
    },
    operation_description="Create a new product"
)
@api_view(http_method_names=['POST'])
def create_product(request):
    user = request.user
    if not user.is_authenticated:
        return Response({"error": "Avtarizatsiyadan ot oldin"}, status=status.HTTP_401_UNAUTHORIZED)
    data = request.data
    serializer = ProductModelSerializer(data=data)
    if not serializer.is_valid():
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    product = serializer.save()
    return Response({"new_product": ProductModelSerializer(product).data}, status=status.HTTP_201_CREATED)

@swagger_auto_schema(
    methods=['GET'],
    manual_parameters=[
        openapi.Parameter(
            'name',
            openapi.IN_QUERY,
            description="Filter products by name",
            type=openapi.TYPE_STRING,
            required=False
        ),
        openapi.Parameter(
            'price_min',
            openapi.IN_QUERY,
            description="Minimum price filter",
            type=openapi.TYPE_INTEGER,
            required=False
        ),
        openapi.Parameter(
            'price_max',
            openapi.IN_QUERY,
            description="Maximum price filter",
            type=openapi.TYPE_INTEGER,
            required=False
        ),
        openapi.Parameter(
            'category',
            openapi.IN_QUERY,
            description="Filter by category",
            type=openapi.TYPE_STRING,
            required=False
        ),
        openapi.Parameter(
            'rate_min',
            openapi.IN_QUERY,
            description="Minimum rating filter",
            type=openapi.TYPE_NUMBER,
            required=False
        ),
        openapi.Parameter(
            'market',
            openapi.IN_QUERY,
            description="Filter by market ID",
            type=openapi.TYPE_INTEGER,
            required=False
        )
    ],
    responses={
        200: openapi.Response(
            description="List of products",
            schema=ProductModelSerializer(many=True)
        )
    },
    operation_description="Get list of all products with various filters"
)
@api_view(['GET'])  
def list_products(request):
    name = request.query_params.get('name')
    price_min = request.query_params.get('price_min')
    price_max = request.query_params.get('price_max')
    category = request.query_params.get('category')
    rate_min = request.query_params.get('rate_min')
    market = request.query_params.get('market')

    products = ProductModel.objects.annotate(
        avg_rate=Avg('rates__rate'), 
        clients_count=Count('rates')
    )

    filters = Q()

    if name:
        filters &= Q(name__icontains=name)

    if price_min:
        filters &= Q(price__gte=price_min)

    if price_max:
        filters &= Q(price__lte=price_max)

    if category:
        filters &= Q(category__iexact=category)

    if rate_min:
        filters &= Q(avg_rate_gte=rate_min)

    if market:
        filters &= Q(market_id=market)

    if filters:
        products = products.filter(filters)

    products = products.order_by('-avg_rate', '-clients_count')

    serializer = ProductModelSerializer(products, many=True)
    return Response({"products": serializer.data}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    methods=['GET'],
    responses={
        200: openapi.Response(
            description="Product details",
            schema=ProductModelSerializer
        ),
        404: "Product not found"
    },
    operation_description="Get detailed information about a specific product"
)
@api_view(['GET'])
def get_product(request, pk):
    try:
        product = ProductModel.objects.annotate(rate=Avg("rates__rate")).get(id=pk)
    except ProductModel.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = ProductModelSerializer(product)
    return Response({"product": serializer.data}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    methods=['PATCH'],
    request_body=ProductModelSerializer,
    responses={
        200: openapi.Response(
            description="Product updated successfully",
            schema=ProductModelSerializer
        ),
        400: "Bad Request",
        401: "Unauthorized",
        404: "Product not found"
    },
    operation_description="Update product information"
)
@api_view(http_method_names=['PATCH'])
def update_product(request, pk):
    user = request.user
    if not user.is_authenticated:
        return Response({"error": "Avtarizatsiyadan ot oldin"}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        product = ProductModel.objects.get(id=pk)
    except ProductModel.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = ProductModelSerializer(instance=product, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    serializer.save()
    return Response({"message": "Product is updated", "product": serializer.data}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    methods=['DELETE'],
    responses={
        200: "Product deleted successfully",
        401: "Unauthorized",
        404: "Product not found"
    },
    operation_description="Delete a product"
)
@api_view(http_method_names=['DELETE'])
def delete_product(request, pk):
    user = request.user
    if not user.is_authenticated:
        return Response({"error": "Avtarizatsiyadan ot oldin"}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        product = ProductModel.objects.get(id=pk)
    except ProductModel.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
    product.delete()
    return Response({"message": "Product is deleted"}, status=status.HTTP_200_OK)
