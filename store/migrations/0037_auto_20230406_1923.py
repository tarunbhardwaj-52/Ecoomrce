# Generated by Django 3.2.18 on 2023-04-07 02:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0036_alter_cartorder_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartorderitem',
            name='delivery_status',
            field=models.CharField(choices=[('shipping_processing', 'Shipping_processing'), ('shipped', 'Shipped'), ('arrived', 'Arrived'), ('collected', 'Collected'), ('completed', 'Collected'), ('returning', 'Returning'), ('returned', 'Returned')], default='initiated', max_length=100),
        ),
        migrations.AlterField(
            model_name='cartorder',
            name='delivery_status',
            field=models.CharField(choices=[('shipping_processing', 'Shipping_processing'), ('shipped', 'Shipped'), ('arrived', 'Arrived'), ('collected', 'Collected'), ('completed', 'Collected'), ('returning', 'Returning'), ('returned', 'Returned')], default='initiated', max_length=100),
        ),
    ]