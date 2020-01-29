from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(default = '1', max_length = 50)
    argip_id = models.CharField(default = '1', max_length = 10)
    shop_id = models.CharField(default = '1', max_length = 10)
    parent_category_id_argip = models.CharField(default = '1', max_length = 10)
    parent_category_id_shop = models.CharField(default = '1', max_length = 10)

class Product(models.Model):
    shop_id = models.CharField(default = '1', max_length = 10)
    local_image_url = models.CharField(default = '1', max_length = 100)
    image_url = models.CharField(default = '1', max_length = 100)
    name = models.CharField(default = '1', max_length = 50)
    price = models.IntegerField(default = 0)
    argip_category_id = models.CharField(default = '1', max_length = 10)
    shop_category_id = models.CharField(default = '1', max_length = 10)
    summary = models.CharField(default = '1', max_length = 50)
    barcode = models.CharField(default = '1', max_length = 20)
    count = models.IntegerField(default = 0)
    purchase_price = models.IntegerField(default = 0)
    is_updated = models.CharField(default = '0', max_length = 2)
