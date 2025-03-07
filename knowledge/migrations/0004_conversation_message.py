# Generated by Django 5.0.8 on 2025-01-20 12:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("knowledge", "0003_systemconfig_htmlpage_target_language_text"),
    ]

    operations = [
        migrations.CreateModel(
            name="Conversation",
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
                ("created", models.DateTimeField(editable=False, verbose_name="创建时间")),
                ("modified", models.DateTimeField(editable=False, verbose_name="修改时间")),
                ("title", models.CharField(max_length=255, verbose_name="对话标题")),
                (
                    "status",
                    models.CharField(
                        choices=[("ACTIVE", "进行中"), ("ARCHIVED", "已归档")],
                        default="ACTIVE",
                        max_length=20,
                        verbose_name="状态",
                    ),
                ),
            ],
            options={
                "verbose_name": "对话",
                "verbose_name_plural": "对话",
                "ordering": ["-modified"],
            },
        ),
        migrations.CreateModel(
            name="Message",
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
                ("created", models.DateTimeField(editable=False, verbose_name="创建时间")),
                ("modified", models.DateTimeField(editable=False, verbose_name="修改时间")),
                (
                    "role",
                    models.CharField(
                        choices=[("USER", "用户"), ("ASSISTANT", "助手")],
                        max_length=20,
                        verbose_name="发送者",
                    ),
                ),
                ("content", models.TextField(verbose_name="消息内容")),
                (
                    "references",
                    models.JSONField(blank=True, default=list, verbose_name="引用来源"),
                ),
                (
                    "conversation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="messages",
                        to="knowledge.conversation",
                        verbose_name="所属对话",
                    ),
                ),
            ],
            options={
                "verbose_name": "消息",
                "verbose_name_plural": "消息",
                "ordering": ["created"],
            },
        ),
    ]
