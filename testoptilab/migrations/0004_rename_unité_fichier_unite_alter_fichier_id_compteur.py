# Generated by Django 4.2.5 on 2023-12-10 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testoptilab', '0003_fichier_calibre_fichier_id_compteur_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fichier',
            old_name='unité',
            new_name='unite',
        ),
        migrations.AlterField(
            model_name='fichier',
            name='id_compteur',
            field=models.UUIDField(unique=True),
        ),
    ]
