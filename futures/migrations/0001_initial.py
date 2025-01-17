# Generated by Django 5.0.8 on 2024-09-08 07:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Goods',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(editable=False, verbose_name='创建时间')),
                ('modified', models.DateTimeField(editable=False, verbose_name='修改时间')),
                ('name', models.CharField(max_length=255)),
                ('date', models.DateField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Market',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(editable=False, verbose_name='创建时间')),
                ('modified', models.DateTimeField(editable=False, verbose_name='修改时间')),
                ('market', models.CharField(max_length=255)),
                ('date', models.DateField()),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
