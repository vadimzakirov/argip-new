# Generated by Django 3.0 on 2019-12-22 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ArgipApp', '0005_product_image_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='local_image_url',
            field=models.CharField(default='1', max_length=100),
        ),
        migrations.AddField(
            model_name='product',
            name='shop_id',
            field=models.CharField(default='1', max_length=10),
        ),
    ]
