# Generated by Django 5.1.6 on 2025-02-25 11:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='updated_at',
        ),
    ]
