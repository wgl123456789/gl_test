# Generated by Django 2.2.3 on 2020-02-05 04:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='项目名称')),
                ('type', models.CharField(choices=[('web', 'web'), ('app', 'app')], max_length=50, verbose_name='项目类型')),
                ('description', models.CharField(blank=True, max_length=1024, null=True, verbose_name='描述')),
                ('last_update_time', models.DateTimeField(auto_now=True, verbose_name='最近修改时间')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='创建人')),
            ],
        ),
    ]
