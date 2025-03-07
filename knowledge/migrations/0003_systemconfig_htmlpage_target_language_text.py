# Generated by Django 5.0.8 on 2025-01-20 11:33

import knowledge.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("knowledge", "0002_add_status_field"),
    ]

    operations = [
        migrations.CreateModel(
            name="SystemConfig",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "key",
                    models.CharField(max_length=100, unique=True, verbose_name="配置键名"),
                ),
                ("value", models.JSONField(verbose_name="配置值")),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "系统配置",
                "verbose_name_plural": "系统配置",
                "ordering": ["-modified"],
            },
        ),
        migrations.AddField(
            model_name="htmlpage",
            name="target_language_text",
            field=knowledge.models.MediumTextField(default="", verbose_name="目标语言文本"),
        ),
    ]
