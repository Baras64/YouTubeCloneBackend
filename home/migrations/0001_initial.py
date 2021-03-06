# Generated by Django 3.1.1 on 2020-09-22 17:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('content', models.TextField()),
                ('image', models.ImageField(null=True, upload_to='media')),
            ],
        ),
        migrations.CreateModel(
            name='Userss',
            fields=[
                ('user_id', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('email_id', models.EmailField(max_length=70, null=True, unique=True)),
                ('first_name', models.CharField(max_length=20)),
                ('last_name', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Videos',
            fields=[
                ('video_id', models.CharField(max_length=11, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('video_url', models.CharField(max_length=2048, unique=True)),
                ('description', models.CharField(max_length=500, null=True)),
                ('release_date', models.DateTimeField()),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.userss')),
            ],
        ),
    ]
