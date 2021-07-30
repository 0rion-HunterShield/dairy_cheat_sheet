from django.db import models

# Create your models here.
class Products(models.Model):
    barcode=models.CharField(max_length=256,primary_key=True)
    name=models.CharField(max_length=256)
    price=models.DecimalField(decimal_places=2,max_digits=11)
    bar_img=models.CharField(max_length=8192)

