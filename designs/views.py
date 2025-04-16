from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .models import Design, Template
from .serializers import DesignSerializer, TemplateSerializer,MockupSerializer, MockupPreviewSerializer
from store.models import Customer
#new imprts
from django.shortcuts import render, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os
from django.core.files.base import ContentFile
from django.conf import settings

from .models import Design, Template, Mockup
#from .serializers import DesignSerializer, TemplateSerializer, MockupSerializer, MockupPreviewSerializer
from store.models import Customer






class DesignViewSet(viewsets.ModelViewSet):
    serializer_class = DesignSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Return designs only for the logged-in user
        try:
            customer = Customer.objects.get(user=self.request.user)
            return Design.objects.filter(customer=customer)
        except Customer.DoesNotExist:
            return Design.objects.none()
    
    def perform_create(self, serializer):
        # Automatically set the customer based on the logged-in user
        try:
            customer = Customer.objects.get(user=self.request.user)
            serializer.save(customer=customer)
        except Customer.DoesNotExist:
            raise ValidationError("User does not have an associated customer account")
    
    @action(detail=True, methods=['delete'], url_path='delete')
    def custom_delete(self, request, pk=None):
        design = self.get_object()
        design.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


class TemplateViewSet(ModelViewSet):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    # Allow filtering by category
    filterset_fields = ['category']  # Filter by category field
    
    # Allow searching by category name
    search_fields = ['category']  # Search by category name

class MockupViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for retrieving mockups"""
    serializer_class = MockupSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        try:
            customer = Customer.objects.get(user=self.request.user)
            return Mockup.objects.filter(design__customer=customer)
        except Customer.DoesNotExist:
            return Mockup.objects.none()

    @action(detail=False, methods=['post'], url_path='preview')
    def preview(self, request):
        """Generate a preview mockup based on design, color, and size"""
        serializer = MockupPreviewSerializer(data=request.data)
        
        if serializer.is_valid():
            design_id = serializer.validated_data['design_id']
            color = serializer.validated_data['color']
            size = serializer.validated_data['size']
            
            try:
                design = Design.objects.get(id=design_id)
                
                # Check if user owns the design
                customer = Customer.objects.get(user=request.user)
                if design.customer != customer:
                    return Response(
                        {"error": "You don't have permission to access this design"},
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                # Try to get existing mockup or generate new one
                try:
                    mockup = Mockup.objects.get(design=design, color=color, size=size)
                except Mockup.DoesNotExist:
                    mockup = generate_mockup(design, color, size)
                
                return Response(
                    MockupSerializer(mockup).data,
                    status=status.HTTP_200_OK
                )
            
            except Design.DoesNotExist:
                return Response(
                    {"error": "Design not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            except Customer.DoesNotExist:
                return Response(
                    {"error": "User does not have a customer account"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def generate_mockup(design, color, size):
    """Generate a mockup image by overlaying the design on a t-shirt template"""
    # Get t-shirt base template based on color
    tshirt_template_path = os.path.join(settings.BASE_DIR, f'static/tshirt_templates/{color}.png')
    
    # If template doesn't exist, use default white
    if not os.path.exists(tshirt_template_path):
       # tshirt_template_path = os.path.join(settings.BASE_DIR, 'static/tshirt_templates/white.png')
       tshirt_template_path = Path(settings.BASE_DIR) / 'static' / 'tshirt_templates' / 't-shirt-on-transparent-background_48723599.png'
    
    # Create a base t-shirt image (this is a placeholder - normally you'd load an actual shirt template)
    try:
        tshirt = Image.open(tshirt_template_path)
    except FileNotFoundError:
        # Create a basic colored t-shirt shape if template is missing
        tshirt = Image.new('RGB', (800, 800), color)
    
    # Load the design image
    if design.design_file:
        try:
            design_image = Image.open(design.design_file.path)
            
            # Resize design based on shirt size (simple scaling factor)
            size_factor = {
                'xs': 0.5,
                's': 0.6,
                'm': 0.7,
                'l': 0.8,
                'xl': 0.9,
                'xxl': 1.0
            }.get(size, 0.7)
            
            # Calculate new dimensions while preserving aspect ratio
            width, height = design_image.size
            new_width = int(width * size_factor)
            new_height = int(height * size_factor)
            design_image = design_image.resize((new_width, new_height))
            
            # Calculate position to center the design on the shirt
            tshirt_width, tshirt_height = tshirt.size
            position = (
                (tshirt_width - new_width) // 2,
                (tshirt_height - new_height) // 3  # Position it on the upper chest area
            )
            
            # If design image has transparency (RGBA), paste with mask
            if design_image.mode == 'RGBA':
                tshirt.paste(design_image, position, design_image)
            else:
                tshirt.paste(design_image, position)
        except Exception as e:
            # If there's any error processing the design image, add text instead
            draw = ImageDraw.Draw(tshirt)
            # Use default font
            # try:
            #     font = ImageFont.truetype("arial.ttf", 24)
            # except:
            font = ImageFont.load_default()
            
            draw.text((400, 400), design.design_description, fill="black")
    else:
        # If no design file, just add the description text
        draw = ImageDraw.Draw(tshirt)
        # try:
        #     font = ImageFont.truetype("arial.ttf", 24)
        # except:
        font = ImageFont.load_default()
        
        draw.text((400, 400), design.design_description, fill="black")
    
    # Save the mockup image
    image_io = BytesIO()
    tshirt.save(image_io, format='PNG')
    
    # Create a new mockup instance
    mockup = Mockup(
        design=design,
        color=color,
        size=size
    )
    
    # Save the image to the mockup instance
    mockup.mockup_image.save(
        f'mockup_{design.id}_{color}_{size}.png',
        ContentFile(image_io.getvalue())
    )
    mockup.save()
    
    return mockup