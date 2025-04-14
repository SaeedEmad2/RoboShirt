from django.db import models
from store.models import Customer


class Design(models.Model):
    design_description = models.TextField()
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add= True)

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

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='templates/')
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
    


