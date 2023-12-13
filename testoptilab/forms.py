# importation/forms.py
from django.utils import timezone  # Ajoutez cette ligne
from django import forms
from .models import Fichier

class FichierUploadForm(forms.ModelForm):
    class Meta:
        model = Fichier
        fields = ['fichier_excel']  # Utilisez 'fichier_excel' comme champ de fichier

    # Ajoutez ces champs au formulaire
    nom = forms.CharField(widget=forms.HiddenInput(), required=False)
    date = forms.DateTimeField(widget=forms.HiddenInput(), initial=timezone.now(), required=False)

    def clean_fichier_excel(self):
        fichier_excel = self.cleaned_data.get('fichier_excel')
        if not fichier_excel:
            raise forms.ValidationError("Vous devez sélectionner un fichier.")
        return fichier_excel

    def save(self, commit=True):
        # Obtenez le nom du fichier Excel et mettez-le dans le champ 'nom'
        self.cleaned_data['nom'] = self.cleaned_data['fichier_excel'].name

        # Appelez la méthode save() de la classe parente pour effectuer la sauvegarde
        instance = super(FichierUploadForm, self).save(commit=False)

        # Si commit est True, enregistrez l'instance dans la base de données
        if commit:
            instance.save()

        return instance


class ExcelUploadForm(forms.Form):
    fichier_excel = forms.FileField()

class ParametresForm(forms.Form):
    valeur_maximale = forms.FloatField()
    nbre_case = forms.IntegerField()
    coef = forms.FloatField()
