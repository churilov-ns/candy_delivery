# Generated by Django 3.1.7 on 2021-03-25 20:43

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('candy_delivery_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='delivery',
            name='assign_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
