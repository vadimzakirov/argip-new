# Generated by Django 3.0 on 2019-12-13 01:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ArgipApp', '0004_product_shop_category_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image_url',
            field=models.CharField(default='1', max_length=100),
        ),
    ]
