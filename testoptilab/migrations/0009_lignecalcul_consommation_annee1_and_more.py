# Generated by Django 4.2.5 on 2023-12-11 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testoptilab', '0008_fichier_total_consommation_annee1_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='lignecalcul',
            name='consommation_annee1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='lignecalcul',
            name='consommation_annee2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='lignecalcul',
            name='consommation_mois1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='lignecalcul',
            name='consommation_mois2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='lignecalcul',
            name='consommation_pas_heure1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='lignecalcul',
            name='consommation_semaine1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='lignecalcul',
            name='consommation_semaine2',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
