# Generated by Django 5.0.6 on 2024-06-06 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('omnipresence', '0004_alter_omnipresencemodel_charname_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='omnipresencemodel',
            name='last_active',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
