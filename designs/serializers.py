# designs/serializers.py
from rest_framework import serializers
from .models import Design
from .models import Template

class DesignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Design
        fields = ['id', 'design_description', 'customer', 'created_at', 'design_file', 'file_type']
        read_only_fields = ['created_at']

class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = ['id', 'category', 'image', 'description']