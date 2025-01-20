from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('knowledge', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='htmlpage',
            name='status',
            field=models.CharField(
                choices=[
                    ('WAIT_PROCESS', '等待处理'),
                    ('PROCESSING', '处理中'),
                    ('FINISH', '处理完成')
                ],
                default='WAIT_PROCESS',
                max_length=20,
                verbose_name='处理状态'
            ),
        ),
    ] 