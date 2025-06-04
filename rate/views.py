from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import RateModel
from .serializers import RateModelSerializer
from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    methods=['POST'],
    request_body=RateModelSerializer,
    responses={
        201: openapi.Response(
            description="Rate created successfully",
            schema=RateModelSerializer
        ),
        400: "Bad Request",
        401: "Unauthorized"
    },
    operation_description="Create a new rate for a product or market"
)
@api_view(['POST'])
def create_rate(request):
    if not request.user.is_authenticated:
        return Response({"error": "Avtarizatsiyadan ot oldin"}, status=status.HTTP_401_UNAUTHORIZED)

    data = request.data.copy()
    serializer = RateModelSerializer(data=data)
    
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response({"rate": serializer.data}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    methods=['GET'],
    manual_parameters=[
        openapi.Parameter(
            'product',
            openapi.IN_QUERY,
            description="Filter rates by product ID",
            type=openapi.TYPE_INTEGER,
            required=False
        ),
        openapi.Parameter(
            'market',
            openapi.IN_QUERY,
            description="Filter rates by market ID",
            type=openapi.TYPE_INTEGER,
            required=False
        )
    ],
    responses={
        200: openapi.Response(
            description="List of rates",
            schema=RateModelSerializer(many=True)
        )
    },
    operation_description="Get list of all rates with optional product or market filters"
)
@api_view(['GET'])
def list_rates(request):
    product_id = request.query_params.get('product')
    market_id = request.query_params.get('market')
    filters = Q()

    if product_id:
        filters &= Q(product__id=product_id)
    
    if market_id:
        filters &= Q(market__id=market_id)

    rates = RateModel.objects.filter(filters)
    serializer = RateModelSerializer(rates, many=True)
    return Response({"rates": serializer.data}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    methods=['GET'],
    responses={
        200: openapi.Response(
            description="Rate details",
            schema=RateModelSerializer
        ),
        404: "Rate not found"
    },
    operation_description="Get detailed information about a specific rate"
)
@api_view(['GET'])
def get_rate(request, pk):
    rate = RateModel.objects.get(id=pk)
    if not rate:
        return Response({"error": "Rate not found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = RateModelSerializer(rate)
    return Response({"rate": serializer.data}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    methods=['PATCH'],
    request_body=RateModelSerializer,
    responses={
        200: openapi.Response(
            description="Rate updated successfully",
            schema=RateModelSerializer
        ),
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden - Can only update own rates",
        404: "Rate not found"
    },
    operation_description="Update a rate (only by the user who created it)"
)
@api_view(['PATCH'])
def update_rate(request, pk):
    if not request.user.is_authenticated:
        return Response({"error": "Avtarizatsiyadan ot oldin"}, status=status.HTTP_401_UNAUTHORIZED)

    rate = RateModel.objects.get(id=pk)
    if not rate:
        return Response({"error": "Rate not found"}, status=status.HTTP_404_NOT_FOUND)
    if rate.user != request.user:
        return Response({"error": "Faqat ozinikini ozgartirolisan"}, status=status.HTTP_403_FORBIDDEN)

    serializer = RateModelSerializer(rate, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Rate updated", "rate": serializer.data}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    methods=['DELETE'],
    responses={
        200: "Rate deleted successfully",
        401: "Unauthorized",
        403: "Forbidden - Can only delete own rates",
        404: "Rate not found"
    },
    operation_description="Delete a rate (only by the user who created it)"
)
@api_view(['DELETE'])
def delete_rate(request, pk):
    if not request.user.is_authenticated:
        return Response({"error": "Avtarizatsiyadan ot oldin"}, status=status.HTTP_401_UNAUTHORIZED)

    rate = RateModel.objects.get(id=pk)
    if not rate:
        return Response({"error": "Rate not found"}, status=status.HTTP_404_NOT_FOUND)
    if rate.user != request.user:
        return Response({"error": "Faqat ozinikini ochirolisan"}, status=status.HTTP_403_FORBIDDEN)
    rate.delete()
    return Response({"message": "Rate deleted"}, status=status.HTTP_200_OK)