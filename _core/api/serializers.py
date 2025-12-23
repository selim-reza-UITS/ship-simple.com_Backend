# serializers.py
from rest_framework import serializers
from .models import ShippingRate, Category, ShippingConfig



class ShippingRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingRate
        fields = ['id', 'origin_country', 'min_weight', 'max_weight', 'price']

    def validate(self, data):
        origin = data.get('origin_country')
        new_min = data.get('min_weight')
        new_max = data.get('max_weight')

        if new_min >= new_max:
            raise serializers.ValidationError("Min weight must be less than Max weight.")

        # Check for overlaps: 
        # An overlap exists if: (Existing_Min < New_Max) AND (Existing_Max > New_Min)
        overlapping_query = ShippingRate.objects.filter(
            origin_country=origin,
            min_weight__lt=new_max, 
            max_weight__gt=new_min
        )

        # If we are updating an existing instance, exclude it from the overlap check
        if self.instance:
            overlapping_query = overlapping_query.exclude(pk=self.instance.pk)

        if overlapping_query.exists():
            conflicting_rate = overlapping_query.first()
            raise serializers.ValidationError(
                f"Weight range conflicts with existing band: {conflicting_rate.min_weight}kg - {conflicting_rate.max_weight}kg"
            )

        return data


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'duty_rate']

class ShippingConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingConfig
        fields = ['vat_rate', 'local_handling_fee', 'margin_rate']
