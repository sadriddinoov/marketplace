from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import MarketModel
from .serializers import MarketModelSerializer
from django.db.models import Q, Avg
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    methods=['POST'],
    request_body=MarketModelSerializer,
    responses={
        201: openapi.Response(
            description="Market created successfully",
            schema=MarketModelSerializer
        ),
        400: "Bad Request",
        401: "Unauthorized"
    },
    operation_description="Create a new market"
)
@api_view(http_method_names=['POST'])
def create_market(request):
    user = request.user
    if not user.is_authenticated:
        return Response({"error": "Avtarizatsiyadan ot oldin"}, status=status.HTTP_401_UNAUTHORIZED)
    data = request.data
    serializer = MarketModelSerializer(data=data)
    if not serializer.is_valid():
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    market = serializer.save()
    return Response({"new_market": MarketModelSerializer(market).data}, status=status.HTTP_201_CREATED)

@swagger_auto_schema(
    methods=['GET'],
    manual_parameters=[
        openapi.Parameter(
            'name',
            openapi.IN_QUERY,
            description="Filter markets by name",
            type=openapi.TYPE_STRING,
            required=False
        )
    ],
    responses={
        200: openapi.Response(
            description="List of markets",
            schema=MarketModelSerializer(many=True)
        )
    },
    operation_description="Get list of all markets with optional name filter"
)
@api_view(http_method_names=['GET'])
def list_market(request):
    name = request.query_params.get('name')
    filters = Q()
    if name:
        filters &= Q(name__icontains=name)
        
    markets = MarketModel.objects.annotate(rate=Avg('rates__rate')).filter(filters) if filters else MarketModel.objects.annotate(rate=Avg("rates__rate"))
    markets = markets.order_by('-rate')
    serializer = MarketModelSerializer(markets, many=True)
    return Response({"markets": serializer.data}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    methods=['GET'],
    responses={
        200: openapi.Response(
            description="Market details",
            schema=MarketModelSerializer
        ),
        404: "Market not found"
    },
    operation_description="Get detailed information about a specific market"
)
@api_view(http_method_names=['GET'])
def market_detail(request, pk):
    market = MarketModel.objects.annotate(rate=Avg('rates__rate')).get(id=pk)
    if not market:
        return Response({"error": "Market not found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = MarketModelSerializer(market)
    return Response({"market": serializer.data}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    methods=['PATCH'],
    request_body=MarketModelSerializer,
    responses={
        200: openapi.Response(
            description="Market updated successfully",
            schema=MarketModelSerializer
        ),
        400: "Bad Request",
        401: "Unauthorized",
        404: "Market not found"
    },
    operation_description="Update market information"
)
@api_view(http_method_names=['PATCH'])
def update_market(request, pk):
    user = request.user
    if not user.is_authenticated:
        return Response({"error": "Avtarizatsiyadan ot oldin"}, status=status.HTTP_401_UNAUTHORIZED)
    if not pk:
        return Response({"error": "Market id yuborilmagan"}, status=status.HTTP_400_BAD_REQUEST)
    market = MarketModel.objects.get(id=pk)
    if not market:
        return ({"error": "market wrong"}, status.HTTP_400_BAD_REQUEST)
    serializer = MarketModelSerializer(instance=market, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    serializer.save()
    market.save()
    return Response({"message": "Market is updated", "market": serializer.data}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    methods=['DELETE'],
    responses={
        200: "Market deleted successfully",
        400: "Bad Request",
        401: "Unauthorized",
        404: "Market not found"
    },
    operation_description="Delete a market"
)
@api_view(http_method_names=['DELETE'])
def delete_market(request, pk):
    user = request.user
    if not user.is_authenticated:
        return Response({"error": "Avtarizatsiyadan ot oldin"}, status=status.HTTP_401_UNAUTHORIZED)
    if not pk:
        return Response({"error": "Market id yuborilmagan"}, status=status.HTTP_400_BAD_REQUEST)
    market = MarketModel.objects.get(id=pk)
    if not market:
        return ({"error": "Market is wrong"}, status.HTTP_400_BAD_REQUEST)
    market.delete()
    return Response({"message": "Market is deleted",}, status=status.HTTP_200_OK)
    