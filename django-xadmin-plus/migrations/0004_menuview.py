# Generated by Django 2.2.7 on 2020-01-20 21:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xadmin', '0003_auto_20160715_0100'),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuView',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app_label', models.CharField(max_length=256, verbose_name='应用名')),
                ('menu_label', models.CharField(max_length=256, verbose_name='页面名')),
            ],
            options={
                'verbose_name': '自定义页',
                'verbose_name_plural': '自定义页',
                'permissions': (('visit_menuview', 'can visit 自定义页'),),
            },
        ),
    ]