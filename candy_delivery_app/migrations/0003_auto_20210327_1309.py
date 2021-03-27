# Generated by Django 3.1.7 on 2021-03-27 13:09

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candy_delivery_app', '0002_auto_20210325_2043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courier',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='order',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='order',
            name='region',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='region',
            name='number',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
