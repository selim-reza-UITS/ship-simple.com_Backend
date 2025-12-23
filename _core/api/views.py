from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ShippingRate, Category, ShippingConfig
from .serializers import (
    ShippingRateSerializer,
    CategorySerializer,
    ShippingConfigSerializer,
)
from rest_framework_simplejwt.views import TokenObtainPairView


class AdminLoginView(TokenObtainPairView):
    pass


class ShippingConfigViewSet(viewsets.ModelViewSet):
    queryset = ShippingConfig.objects.all()
    serializer_class = ShippingConfigSerializer

    # Helper to get the first config or create default
    def get_object(self):
        obj, created = ShippingConfig.objects.get_or_create(id=1)
        return obj


class ShippingRateViewSet(viewsets.ModelViewSet):
    queryset = ShippingRate.objects.all()
    serializer_class = ShippingRateSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CalculatorViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["post"])
    def calculate(self, request):
        data = request.data
        try:
            # 1. Inputs
            weight = float(data.get("weight", 0))
            length = float(data.get("length", 0))
            width = float(data.get("width", 0))
            height = float(data.get("height", 0))
            item_value = float(data.get("item_value", 0))
            category_name = data.get("category")
            origin = data.get("origin")

            # 2. Volumetric Weight Calculation
            vol_weight = (length * width * height) / 5000
            billable_weight = max(weight, vol_weight)

            # 3. Fetch Config and Rates
            config = ShippingConfig.objects.first()  # Fetching the configuration
            category = Category.objects.get(name=category_name)

            # Find the rate band based on the billable weight
            rate_band = ShippingRate.objects.filter(
                origin_country=origin,
                min_weight__lte=billable_weight,
                max_weight__gte=billable_weight,
            ).first()

            if not rate_band:
                return Response(
                    {
                        "error": f"No rate band found for {billable_weight}kg from {origin}. Please contact support."
                    },
                    status=400,
                )

            base_shipping = rate_band.price

            # 4. CIF Calculation
            cif_value = item_value + base_shipping
            duty_amount = cif_value * category.duty_rate  # Calculating duty
            vat_amount = (cif_value + duty_amount) * (
                config.vat_rate / 100
            )  # VAT calculation

            # 5. Subtotal Calculation (Shipping + Duties + VAT + Local Handling Fees)
            subtotal = (
                base_shipping + duty_amount + vat_amount + config.local_handling_fee
            )

            # 6. Margin Calculation
            margin = subtotal * (config.margin_rate / 100)  # Applying margin

            # 7. Final Total (Subtotal + Margin)
            final_total = subtotal + margin

            # 8. Return the response
            return Response(
                {
                    "billable_weight": round(billable_weight, 2),
                    "breakdown": {
                        "shipping": round(base_shipping, 2),
                        "duties": round(duty_amount, 2),
                        "vat": round(vat_amount, 2),
                        "local_fees": round(config.local_handling_fee, 2),
                        "margin": round(margin, 2),  # Showing margin in the breakdown
                        "subtotal": round(subtotal, 2),  # Showing subtotal for clarity
                    },
                    "total": round(final_total, 2),  # Total including margin
                    "currency": "USD"
                    if origin == "USA"
                    else "GBP",  # Currency based on origin
                }
            )

        except Category.DoesNotExist:
            return Response({"error": "Invalid Category"}, status=400)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
