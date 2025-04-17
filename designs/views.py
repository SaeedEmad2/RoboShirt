from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.viewsets import ModelViewSet  # Import ModelViewSet
from rest_framework.decorators import action
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
from .serializers import DesignSerializer, TemplateSerializer, MockupSerializer, MockupPreviewSerializer
from store.models import Customer


# Design ViewSet
class DesignViewSet(viewsets.ModelViewSet):
    serializer_class = DesignSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return designs only for the logged-in user
        customer = Customer.objects.filter(user=self.request.user).first()
        if customer:
            return Design.objects.filter(customer=customer)
        return Design.objects.none()

    def perform_create(self, serializer):
        # Automatically set the customer based on the logged-in user
        customer = Customer.objects.filter(user=self.request.user).first()
        if not customer:
            raise ValidationError("User does not have an associated customer account")
        serializer.save(customer=customer)

    @action(detail=True, methods=['delete'], url_path='delete')
    def custom_delete(self, request, pk=None):
        design = self.get_object()
        design.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Template ViewSet
class TemplateViewSet(ModelViewSet):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category']  # Filter by category field
    search_fields = ['category']  # Search by category name


# Mockup ViewSet
class MockupViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MockupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        customer = Customer.objects.filter(user=self.request.user).first()
        if customer:
            return Mockup.objects.filter(design__customer=customer)
        return Mockup.objects.none()

    @action(detail=False, methods=['post'], url_path='preview')
    def preview(self, request):
        serializer = MockupPreviewSerializer(data=request.data)
        if serializer.is_valid():
            design_id = serializer.validated_data['design_id']
            color = serializer.validated_data['color']
            size = serializer.validated_data['size']

            design = get_object_or_404(Design, id=design_id)
            customer = Customer.objects.filter(user=request.user).first()

            if not customer or design.customer != customer:
                return Response(
                    {"error": "You don't have permission to access this design"},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Try to get existing mockup or generate a new one
            mockup, created = Mockup.objects.get_or_create(
                design=design, color=color, size=size,
                defaults={'mockup_image': generate_mockup(design, color, size)}
            )

            return Response(MockupSerializer(mockup).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Helper Function to Generate Mockups
def generate_mockup(design, color, size):
    """Generate a mockup image by overlaying the design on a t-shirt template."""
    tshirt_template_path = Path(settings.BASE_DIR) / 'static' / 'tshirt_templates' / f'{color}.png'

    # Use default white template if the specified color template doesn't exist
    if not tshirt_template_path.exists():
        tshirt_template_path = Path(settings.BASE_DIR) / 'static' / 'tshirt_templates' / 'default.png'

    try:
        tshirt = Image.open(tshirt_template_path)
    except FileNotFoundError:
        tshirt = Image.new('RGB', (800, 800), color)

    if design.design_file:
        try:
            design_image = Image.open(design.design_file.path)
            size_factor = {'xs': 0.5, 's': 0.6, 'm': 0.7, 'l': 0.8, 'xl': 0.9, 'xxl': 1.0}.get(size, 0.7)
            new_width, new_height = int(design_image.width * size_factor), int(design_image.height * size_factor)
            design_image = design_image.resize((new_width, new_height))

            position = ((tshirt.width - new_width) // 2, (tshirt.height - new_height) // 3)
            if design_image.mode == 'RGBA':
                tshirt.paste(design_image, position, design_image)
            else:
                tshirt.paste(design_image, position)
        except Exception:
            draw = ImageDraw.Draw(tshirt)
            font = ImageFont.load_default()
            draw.text((400, 400), design.design_description, fill="black", font=font)
    else:
        draw = ImageDraw.Draw(tshirt)
        font = ImageFont.load_default()
        draw.text((400, 400), design.design_description, fill="black", font=font)

    image_io = BytesIO()
    tshirt.save(image_io, format='PNG')

    mockup = Mockup(design=design, color=color, size=size)
    mockup.mockup_image.save(f'mockup_{design.id}_{color}_{size}.png', ContentFile(image_io.getvalue()))
    mockup.save()

    return mockup