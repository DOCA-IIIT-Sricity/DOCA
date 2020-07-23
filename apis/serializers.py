from rest_framework import serializers
from .models import slots, slots_available, appointments

class slotsSerializers(serializers.ModelSerializer):
    class Meta:
        model = slots
        fields = '__all__'

class slots_availSerializers(serializers.ModelSerializer):
    class Meta:
        model = slots_available
        fields = '__all__'

class appointmentsSerializers(serializers.ModelSerializer):
    class Meta:
        model = appointments
        fields = '__all__'