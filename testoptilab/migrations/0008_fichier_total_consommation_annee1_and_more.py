# Generated by Django 4.2.5 on 2023-12-11 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testoptilab', '0007_rename_total_consomation1_fichier_total_consommation1_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='fichier',
            name='total_consommation_annee1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='fichier',
            name='total_consommation_annee2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='fichier',
            name='total_consommation_mois1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='fichier',
            name='total_consommation_mois2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='fichier',
            name='total_consommation_semaine1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='fichier',
            name='total_consommation_semaine2',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
