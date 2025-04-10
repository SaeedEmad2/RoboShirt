from django.db import models
from store.models import Customer


class Design(models.Model):
    design_description = models.TextField()
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add= True)
    
    


# Create your models here.
