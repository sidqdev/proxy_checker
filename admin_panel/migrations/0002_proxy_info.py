# Generated by Django 3.1.4 on 2022-09-28 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_panel', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='proxy',
            name='info',
            field=models.TextField(default=''),
        ),
    ]
