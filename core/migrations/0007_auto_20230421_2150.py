# Generated by Django 3.2.18 on 2023-04-21 20:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0060_auto_20230418_2200'),
        ('core', '0006_cancelledorder'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cancelledorder',
            name='order',
        ),
        migrations.AddField(
            model_name='cancelledorder',
            name='orderitem',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.cartorderitem'),
        ),
    ]
