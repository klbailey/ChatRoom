# Generated by Django 5.0.4 on 2024-04-26 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ChatApp', '0007_alter_userprofilemodel_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofilemodel',
            name='name',
            field=models.CharField(default='', max_length=100),
        ),
    ]