# Generated by Django 3.2.18 on 2023-04-01 01:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0014_auto_20230330_1809'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartorder',
            name='product',
        ),
        migrations.AddField(
            model_name='cartorder',
            name='stripe_payment_intent',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='cartorder',
            name='total',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=12),
        ),
        migrations.AlterField(
            model_name='cartorder',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='cartorder',
            name='email',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
