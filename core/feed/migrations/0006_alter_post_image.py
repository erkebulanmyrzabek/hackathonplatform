# Generated by Django 5.1.6 on 2025-02-28 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0005_alter_post_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, null=True, storage='/Users/erkebulanmyrzabek/Desktop/HackPlatform/core/static/img', upload_to=''),
        ),
    ]
