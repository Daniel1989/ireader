# Generated by Django 5.0.8 on 2024-08-25 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('knowledge', '0003_htmlpage_summary_htmlpage_text'),
    ]

    operations = [
        migrations.CreateModel(
            name='HNIdeas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(editable=False, verbose_name='创建时间')),
                ('modified', models.DateTimeField(editable=False, verbose_name='修改时间')),
                ('url', models.CharField(max_length=255)),
                ('story_id', models.CharField(max_length=64)),
                ('comment_id', models.CharField(max_length=64)),
                ('summary', models.TextField()),
            ],
            options={
                'verbose_name': 'ideas',
                'verbose_name_plural': 'ideas',
            },
        ),
    ]
