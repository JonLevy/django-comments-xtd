# Generated by Django 2.2.2 on 2020-05-28 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_comments_xtd', '0006_auto_20181204_0948'),
    ]

    operations = [
        migrations.AddField(
            model_name='xtdcomment',
            name='edited',
            field=models.BooleanField(default=False),
        ),
    ]
