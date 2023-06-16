# Generated by Django 3.2.18 on 2023-04-21 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('addons', '0019_supportcontactinformation_working_days'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='admin_website_address',
            field=models.CharField(default=1, help_text='Add the admin address without the slash /', max_length=500),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='company',
            name='website_address',
            field=models.CharField(help_text='Add the website address without the slash /', max_length=500),
        ),
    ]