# Generated by Django 3.2.8 on 2023-03-15 22:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_auto_20230224_2301'),
    ]

    operations = [
        migrations.AddField(
            model_name='equation',
            name='Instanses',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='description',
            name='Equation',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.equation'),
        ),
        migrations.AlterField(
            model_name='description',
            name='Votes',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='equationimagemodel',
            name='Equation',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.equation'),
        ),
    ]
