# Generated by Django 5.1 on 2024-08-18 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aitask', '0002_summarytask_type_alter_summarytask_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aitask',
            name='target',
            field=models.CharField(max_length=255),
        ),
    ]
