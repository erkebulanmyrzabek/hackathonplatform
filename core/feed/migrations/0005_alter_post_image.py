# Generated by Django 5.1.6 on 2025-02-28 08:39

import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0004_casecup_webinar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(location='/Users/erkebulanmyrzabek/Desktop/HackPlatform/core/static/img'), upload_to=''),
        ),
    ]
