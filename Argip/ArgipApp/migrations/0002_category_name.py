# Generated by Django 3.0 on 2019-12-12 22:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ArgipApp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='name',
            field=models.CharField(default='1', max_length=100),
        ),
    ]
