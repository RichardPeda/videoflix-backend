# Generated by Django 5.1.4 on 2025-01-13 21:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0003_verifycode_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='verifycode',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
