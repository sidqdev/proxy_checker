# Generated by Django 3.1.4 on 2022-09-28 14:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Protocol',
            fields=[
                ('id', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('value', models.TextField()),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Proxy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('host', models.CharField(max_length=50)),
                ('port', models.SmallIntegerField()),
                ('username', models.CharField(blank=True, max_length=256, null=True)),
                ('password', models.CharField(blank=True, max_length=256, null=True)),
                ('is_available', models.BooleanField(default=False)),
                ('protocol', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin_panel.protocol')),
            ],
        ),
    ]
