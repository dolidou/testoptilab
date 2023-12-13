# models.py

from django.conf import settings
from django.db import models
import os


def upload_to(instance, filename):
    return os.path.join('file', filename)

class Fichier(models.Model):
    fichier_excel = models.FileField(upload_to='file', null=True, blank=True)
    nom = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    nom_bd = models.CharField(max_length=255)  # Add nom_bd field
    id_compteur = models.IntegerField()  
    num_compteur = models.CharField(max_length=50)  # Add num_compteur field
    lib_compteur = models.CharField(max_length=255)  # Add lib_compteur field
    source = models.CharField(max_length=255)  # Add source field
    unite = models.CharField(max_length=50)  # Add unité field
    calibre = models.CharField(max_length=50)  # Ajouter une valeur par défaut
    min = models.FloatField(null=True, blank=True)
    max = models.FloatField(null=True, blank=True)
    moyenne = models.FloatField(null=True, blank=True)
    pas_1 = models.IntegerField(null=True, blank=True)
    pas_2 = models.IntegerField(null=True, blank=True)
    nbre_case = models.IntegerField(null=True, blank=True)
    valeur_max = models.FloatField(null=True, blank=True)
    total_consommation1 = models.FloatField(null=True, blank=True)
    total_consommation2 = models.FloatField(null=True, blank=True)
    total_consommation_heure1 = models.FloatField(null=True, blank=True)
    total_consommation_jour1 = models.FloatField(null=True, blank=True)
    total_consommation_jour2 = models.FloatField(null=True, blank=True)
    total_consommation_semaine1 = models.FloatField(null=True, blank=True)
    total_consommation_semaine2 = models.FloatField(null=True, blank=True)
    total_consommation_mois1 = models.FloatField(null=True, blank=True)
    total_consommation_mois2 = models.FloatField(null=True, blank=True)
    total_consommation_annee1 = models.FloatField(null=True, blank=True)
    total_consommation_annee2 = models.FloatField(null=True, blank=True)
    filtered_data_json = models.JSONField(null=True, blank=True)


    def __str__(self):
        return self.nom
    def get_absolute_url(self):
        return os.path.join(settings.MEDIA_URL, str(self.fichier_excel))
    def get_filename(self):
        return os.path.basename(self.fichier_excel.name)

    
class Donnees(models.Model):
    fichier = models.ForeignKey(Fichier, on_delete=models.CASCADE)
    date = models.DateField()
    consommation = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.fichier.nom} - {self.date}"
    
class Calcul(models.Model):
    fichier = models.ForeignKey(Fichier, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Calcul for {self.fichier}"

class LigneCalcul(models.Model):
    calcul = models.ForeignKey(Calcul, on_delete=models.CASCADE)
    vecteur_pas1 = models.FloatField(null=True, blank=True)
    vecteur_pas2 = models.FloatField(null=True, blank=True)
    consommation_pas1 = models.FloatField(null=True, blank=True)
    consommation_pas2 = models.FloatField(null=True, blank=True)
    consommation_jour1 = models.FloatField(null=True, blank=True)
    consommation_jour2 = models.FloatField(null=True, blank=True)
    consommation_pas_heure1 = models.FloatField(null=True, blank=True)
    consommation_semaine1 = models.FloatField(null=True, blank=True)
    consommation_semaine2 = models.FloatField(null=True, blank=True)
    consommation_mois1 = models.FloatField(null=True, blank=True)
    consommation_mois2 = models.FloatField(null=True, blank=True)
    consommation_annee1 = models.FloatField(null=True, blank=True)
    consommation_annee2 = models.FloatField(null=True, blank=True)



    def __str__(self):
        return f"Ligne de calcul pour {self.calcul.fichier}"

