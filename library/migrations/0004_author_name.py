# Generated by Django 5.1.1 on 2024-10-04 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0003_alter_book_published_on'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='name',
            field=models.CharField(max_length=50, null=True),
        ),
    ]