# Generated by Django 3.2.8 on 2023-02-24 23:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_characterimage_equationimagemodel'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='characterimage',
            name='Verified',
        ),
        migrations.AddField(
            model_name='equationimagemodel',
            name='Verified',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
