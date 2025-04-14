from django.db import models
from store.models import Customer


class Design(models.Model):
    design_description = models.TextField()
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add= True)
    design_file = models.FileField(upload_to='design_uploads/',null=True, blank=True)
    file_type = models.CharField(max_length=10, choices=[
        ('jpeg', 'JPEG'), 
        ('png', 'PNG'), 
        ('svg', 'SVG')
    ], null=True, blank=True)
    
    def __str__(self):
        return f"Design {self.id} by {self.customer.first_name or 'Unknown'}"
    
class Template(models.Model):
    CATEGORY_CHOICES = [
        ('movies', 'Movies'),
        ('music', 'Music'),
        ('quotes', 'Quotes'),
        ('family', 'Family'),
        ('gamers', 'Gamers'),
        ('sports', 'Sports'),
        ('funny', 'Funny'),
        ('spooky', 'Spooky'),
    ]

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='templates/')
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
    



    


# Create your models here.
