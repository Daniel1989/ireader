# Generated by Django 5.0.8 on 2024-09-08 07:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('futures', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='goods',
            name='category',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='goods',
            name='categoryGoods',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='goods',
            name='currentBoxBottom',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='goods',
            name='currentBoxTop',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='goods',
            name='currentTrending',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='goods',
            name='last5DaysTrending',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='goods',
            name='predictTrending',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='goods',
            name='predictTrendingReason',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='goods',
            name='selectedGoodsInOtherMonth',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='goods',
            name='specialDaily',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='goods',
            name='stopLoss',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='goods',
            name='whatIfAgainstTrending',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='goods',
            name='name',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='market',
            name='date',
            field=models.DateField(unique=True),
        ),
        migrations.AlterField(
            model_name='market',
            name='market',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AlterUniqueTogether(
            name='goods',
            unique_together={('name', 'date')},
        ),
    ]
