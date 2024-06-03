# serializers.py in the first project
from rest_framework import serializers
from .models import Order, Skill

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['title', 'description', 'price', 'skills', 'client', 'status']

    def create(self, validated_data):
        skills_data = validated_data.pop('skills', [])
        order = Order.objects.create(**validated_data)
        order.skills.set(Skill.objects.filter(id__in=skills_data))
        return order
