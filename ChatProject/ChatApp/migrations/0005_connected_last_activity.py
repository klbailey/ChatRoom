# Generated by Django 5.0.4 on 2024-04-20 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ChatApp', '0004_connected_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='connected',
            name='last_activity',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
