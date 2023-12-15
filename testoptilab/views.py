import base64
import gzip
import json
import os
import re
import string
import dask.dataframe as dd
from django.forms import ValidationError
import pandas as pd
from django.shortcuts import get_object_or_404, render, redirect
from .forms import FichierUploadForm, ExcelUploadForm, ParametresForm
from .models import Calcul, Fichier, Donnees, LigneCalcul, upload_to
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from dask.distributed import Client



def affiche_fichier(request):
    fichier=Fichier.objects.all()

    return render(request,'testexcel/upload_excel.html',{'fichier':fichier})

def donnees_traite(request, fichier_id):
        fichier = get_object_or_404(Fichier, pk=fichier_id)
        encoded_data = fichier.filtered_data_json
        # Décodez les données base64
        decoded_data = base64.b64decode(encoded_data)

        # Décompressez les données
        decompressed_data = gzip.decompress(decoded_data)

        # Convertissez la chaîne JSON décompressée en une liste de dictionnaires
        filtered_data_list = json.loads(decompressed_data.decode('utf-8'))
        
        context = {
        'fichier': fichier,
        'filtered_data_list': filtered_data_list
         }    

        return render(request, 'testexcel/testdatatable.html', context)

    
def details_page(request, fichier_id):
    fichier = get_object_or_404(Fichier, pk=fichier_id)
    encoded_data = fichier.filtered_data_json
    # Décodez les données base64
    decoded_data = base64.b64decode(encoded_data)

    # Décompressez les données
    decompressed_data = gzip.decompress(decoded_data)

    # Convertissez la chaîne JSON décompressée en une liste de dictionnaires
    filtered_data_list = json.loads(decompressed_data.decode('utf-8'))

        # Afficher la liste nettoyée
    # print('filtered', filtered_data_list)
     # Récupérer tous les calculs liés à ce fichier
    calculs = Calcul.objects.filter(fichier=fichier)

    # Pour chaque calcul, récupérer les lignes de calcul associées
   
    lignes_calcul = LigneCalcul.objects.filter(calcul__in=calculs)
     # Convertir les vecteurs en JSON
    vecteur_consommation1_json = json.dumps([ligne.consommation_pas1 for ligne in lignes_calcul])
    vecteur_consommation2_json = json.dumps([ligne.consommation_pas2 for ligne in lignes_calcul])
    vecteur_pas1_json= json.dumps([ligne.vecteur_pas1 for ligne in lignes_calcul])
    vecteur_pas2_json= json.dumps([ligne.vecteur_pas2 for ligne in lignes_calcul])
    vecteur_consommation_jour1_json = json.dumps([ligne.consommation_jour1 for ligne in lignes_calcul])
    vecteur_consommation_jour2_json = json.dumps([ligne.consommation_jour2 for ligne in lignes_calcul])



    context = {
        'fichier': fichier,
        'lignes_calcul': lignes_calcul,
        'vecteur_consommation1_json':vecteur_consommation1_json,
        'vecteur_consommation2_json':vecteur_consommation2_json,
        'vecteur_pas1_json' : vecteur_pas1_json,
        'vecteur_pas2_json' : vecteur_pas2_json,
        'vecteur_consommation_jour1_json':vecteur_consommation_jour1_json,
        'vecteur_consommation_jour2_json':vecteur_consommation_jour2_json,
        'filtered_data_list': filtered_data_list



    }    

    return render(request, 'testexcel/details_page.html', context)


def import_donnees(request):
    print(f"Méthode de requête: {request.method}")

    filtered_data_list = None
    data = {}

    if request.method == 'POST':
        fichier_excel = request.FILES.get('fichier_excel')
        date_debut_str = request.POST.get('date_debut')  # Récupérer la date de début
        date_fin_str = request.POST.get('date_fin')  # Récupérer la date de fin

        if 'fichier_excel' in request.FILES:
            # Traitement du fichier Excel
            excel_file = request.FILES['fichier_excel']
            excel_data_pandas = pd.read_excel(excel_file, header=None)

            # Enregistrez les données dans la table Donnees
            # Supposons que la date est dans la première colonne et la consommation dans la deuxième
            excel_data_pandas.columns = ['Date', 'Consommation']  # Renommez les colonnes pour plus de clarté

            # Convertissez le DataFrame Pandas en DataFrame Dask
            excel_data_dask = dd.from_pandas(excel_data_pandas, npartitions=2)  # Choisissez le nombre de partitions approprié

            date_debut = pd.to_datetime(date_debut_str)
            date_fin = pd.to_datetime(date_fin_str)
            # Filtrer les données pour inclure uniquement celles entre le 20 octobre 2019 et le 10 novembre 2019
            filtered_data = excel_data_dask[
                (excel_data_dask['Date'] >= date_debut) & (excel_data_dask['Date'] <= date_fin)
            ]
            print(filtered_data)
            # Convertir les données filtrées en liste de dictionnaires
            filtered_data_list = filtered_data.compute().to_dict(orient='records')

            # paginator = Paginator(filtered_data_list, 10)  # 10 éléments par page (ajustez selon vos besoins)
            # page = request.GET.get('page')
            # try:
            #      filtered_data_list = paginator.page(page)
            # except PageNotAnInteger:
            #     # Si la page n'est pas un entier, fournissez la première page.
            #     filtered_data_list = paginator.page(1)
            # except EmptyPage:
            #     # Si la page est en dehors de la plage, fournissez la dernière page.
            #     filtered_data_list = paginator.page(paginator.num_pages)

            context = {
                'filtered_data_list': filtered_data_list,
            }

            return render(request, 'importation/import_donnees.html', context)

    # Si la méthode n'est pas 'POST', renvoyer une réponse par défaut ou rediriger l'utilisateur
    return HttpResponse("Méthode de requête non autorisée ou formulaire non soumis.")
    # Ou rediriger l'utilisateur vers une autre page
    # return redirect('nom_de_la_vue_ou_url')

def upload_excel(request):
    error_message = None

    if request.method == 'POST':
        excel_file = request.FILES['excel_file']
        valeur_maximale = float(request.POST.get('valeur_maximale'))
        nbre_case = int(request.POST.get('nbre_case'))
        coef = float(request.POST.get('coef'))
        date_debut_str = request.POST.get('date_debut')  # Récupérer la date de début
        date_fin_str = request.POST.get('date_fin')
       
        client = Client()

        try:
            # Lire le fichier Excel en mémoire sans sauvegarder dans la base de données
            df = pd.read_excel(excel_file)
            # print("df column",df.columns)
            df.columns = df.columns.str.replace(r'\s', '')

            # Vérifier si la colonne sélectionnée existe dans le DataFrame
            selected_column = request.POST.get('selected_column').strip()
            if selected_column not in df.columns:
                raise ValidationError(f"La colonne '{selected_column}' n'existe pas dans le fichier Excel.")
            
            nom_bd=df[selected_column].iloc[2]
            id_compteur=df[selected_column].iloc[3]
            source=df[selected_column].iloc[4]
            num_compteur=df[selected_column].iloc[6]
            lib_compteur=df[selected_column].iloc[7]
            unite=df[selected_column].iloc[8]
            calibre=df[selected_column].iloc[9]

            # print("nom_bd",nom_bd)
            # print("id_compteur",id_compteur)
            # print("source",source)
            # print("num_compteur",num_compteur)
            # print("lib_compteur",lib_compteur)
            # print("unite",unite)
            # print("calibre",calibre)
             # Créer un nouvel objet Fichier avec les valeurs extraites
            
            fichier_obj = Fichier(
                # fichier_excel=upload_to(None, excel_file.name),  # Utilisez la fonction upload_to pour générer le chemin
                nom_bd=nom_bd,
                id_compteur=id_compteur,
                source=source,
                num_compteur=num_compteur,
                lib_compteur=lib_compteur,
                unite=unite,
                calibre=calibre
            )
            fichier_obj.save()  # Sauvegarder l'objet dans la base de données
            selected_columns = ["date", selected_column]
            filtered_df = df[selected_columns]
            # Obtenez le chemin pour enregistrer le fichier
            # Répertoire de sauvegarde
            directory_path = 'media/file'

            # Vérifier si le répertoire existe, sinon le créer
            
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
            original_file_name = f"{selected_column}_processed_{excel_file.name}"
            # print("Nom du fichier original avant nettoyage :", original_file_name)
            # translation_table = str.maketrans("", "", string.punctuation + string.whitespace)
            # cleaned_file_name = original_file_name.translate(translation_table)
            new_excel_file_path =  "media/file/" + original_file_name

            print('fichier',new_excel_file_path)
            try:
                filtered_df.to_excel(new_excel_file_path, index=False, engine='openpyxl')
            except Exception as e:
                print(f"Erreur lors de l'enregistrement du fichier : {e}")

            # Mettez à jour le champ fichier_excel dans l'objet Fichier avec le nouveau fichier
            relative_path = os.path.relpath(new_excel_file_path, 'media/file/')

            fichier_obj.fichier_excel.name = 'file/' + relative_path
            fichier_obj.nom = relative_path

            # filtered_df
            fichier_obj.save()  # Sauvegarder à nouveau l'objet dans la base de données avec le nouveau fichier



            df = df.iloc[11:]

            # date_debut_str =    '01-04-2018'
            # date_fin_str = '31-12-2019'  # Récupérer la date de fin

            # Effectuer le calcul pour la colonne sélectionnée
            # df['calculated_column'] =''
            # # df[selected_column] * 4

            date_debut = pd.to_datetime(date_debut_str)
            date_fin = pd.to_datetime(date_fin_str)
            excel_data_dask = dd.from_pandas(df, npartitions=4)  # Choisissez le nombre de partitions approprié

            excel_data_dask['date'] = dd.to_datetime(excel_data_dask['date'])

            filtered_data = excel_data_dask[
                (excel_data_dask['date'] >= date_debut) & (excel_data_dask['date'] <= date_fin)
            ]
            # Calculer les résultats
            filtered_data = filtered_data.compute()

            # Sélectionner les colonnes spécifiques
            filtered_data_selected = filtered_data[selected_columns].fillna(0)
            filtered_data_selected['date'] = filtered_data_selected['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
            # Convertir le DataFrame en une liste de dictionnaires
            filtered_data_json = filtered_data_selected.to_json(orient='records', date_format='iso')


            # print('filtered_data', filtered_data_json)
            # Compresser la chaîne JSON
            compressed_data = gzip.compress(filtered_data_json.encode('utf-8'))

            # Encoder en base64
            encoded_data = base64.b64encode(compressed_data).decode('utf-8')


            # print("valeur",filtered_data)

            selected_column_data = filtered_data[selected_column]
            # print("Colonnes sélectionnées :", selected_column_data)

            min_consommation = filtered_data[selected_column].min()
            max_consommation = filtered_data[selected_column].max()
            moyenne_consommation = round(filtered_data[selected_column].mean(), 2)


            # Affichez les résultats
            # print(f"Min Consommation (20 octobre 2019 - 10 novembre 2019): {min_consommation}")
            # print(f"Max Consommation (20 octobre 2019 - 10 novembre 2019): {max_consommation}")
            # print(f"Moyenne Consommation (20 octobre 2019 - 10 novembre 2019): {moyenne_consommation}")

            pas_1 =  round(valeur_maximale / nbre_case)
            pas_2 = round(valeur_maximale * coef / nbre_case)
             # Initialisation des variables
            ancien_pas_1 = 0
            ancien_pas_2 = 0

            # Calculs des vecteurs
            vecteur_pas1 = [ancien_pas_1 + pas_1 * i for i in range(1, nbre_case + 1)]
            vecteur_pas2 = [ancien_pas_2 + pas_2 * i for i in range(1, nbre_case + 1)]
            longueur_vecteur_pas1 = len(vecteur_pas1)
            # Avant de rendre le modèle, calculez la liste des indices et des valeurs
            indices_et_valeurs_pas1 = [(i+1, valeur) for i, valeur in enumerate(vecteur_pas1)]

            vecteur_pas1.insert(0, 0)
            vecteur_pas2.insert(0, 0)
            # Affichez les résultats
            # print(f"Pas 1: {pas_1}")
            # print(f"Pas 2: {pas_2}")
            # print(f"Vecteur Pas 1: {vecteur_pas1}")
            # print(f"Vecteur Pas 2: {vecteur_pas2}")

            vecteur_consommation1 = [
                len(filtered_data[
                    (filtered_data[selected_column] > ancien_pas_1 + pas_1 * i) &
                    (filtered_data[selected_column] <= ancien_pas_1 + pas_1 * (i + 1))
                ])
                for i in range(nbre_case)
            ]
            # print("vecteur_pas_2:", vecteur_pas2[0])

            vecteur_consommation2 = [
                len(filtered_data[
                  (filtered_data[selected_column] * coef > ancien_pas_2 + pas_2 * i) &  # Ajustement ici
                    (filtered_data[selected_column] * coef <= ancien_pas_2 + pas_2 * (i + 1))  # Ajustement ici

                ])
                for i in range(nbre_case)
            ]


            
            vecteur_consommation1.insert(0, 0)
            vecteur_consommation2.insert(0, 0)

            
            vecteur_consommation_heure1 = [
                  round(len(filtered_data[
                (filtered_data[selected_column] > ancien_pas_1 + pas_1 * i) &
                (filtered_data[selected_column] <= ancien_pas_1 + pas_1 * (i + 1))
            ]) / 24 )
            for i in range(nbre_case)
            ]
            vecteur_consommation_heure1.insert(0, 0)

            vecteur_consommation_semaine1 = [
            round(len(filtered_data[
                 (filtered_data[selected_column] > ancien_pas_1 + pas_1 * i) &
                (filtered_data[selected_column] <= ancien_pas_1 + pas_1 * (i + 1))
            ]) / 168 )
            for i in range(nbre_case)
             ]
            vecteur_consommation_semaine1.insert(0, 0)
            vecteur_consommation_semaine2 = [
            round(len(filtered_data[
                 (filtered_data[selected_column] * coef > ancien_pas_2 + pas_2 * i) &
                (filtered_data[selected_column] * coef<= ancien_pas_2 + pas_2 * (i + 1))
            ]) / 168 )
            for i in range(nbre_case)
             ]
            vecteur_consommation_semaine2.insert(0, 0)

            vecteur_consommation_mois1 = [
            round(len(filtered_data[
                 (filtered_data[selected_column] > ancien_pas_1 + pas_1 * i) &
                (filtered_data[selected_column] <= ancien_pas_1 + pas_1 * (i + 1))
            ]) / (30 * 24) )
            for i in range(nbre_case)
             ]
            vecteur_consommation_mois1.insert(0, 0)

            vecteur_consommation_mois2 = [
            round(len(filtered_data[
                 (filtered_data[selected_column] * coef> ancien_pas_2 + pas_2 * i) &
                (filtered_data[selected_column] * coef<= ancien_pas_2 + pas_2 * (i + 1))
            ]) / (30 * 24) )
            for i in range(nbre_case)
             ]
            vecteur_consommation_mois2.insert(0, 0)

            vecteur_consommation_annee1 = [
            round(len(filtered_data[
                 (filtered_data[selected_column] > ancien_pas_1 + pas_1 * i) &
                (filtered_data[selected_column] <= ancien_pas_1 + pas_1 * (i + 1))
            ]) / (365 * 24) )
            for i in range(nbre_case)
             ]
            vecteur_consommation_annee1.insert(0, 0)

            vecteur_consommation_annee2 = [
            round(len(filtered_data[
                 (filtered_data[selected_column] * coef> ancien_pas_2 + pas_2 * i) &
                (filtered_data[selected_column] * coef<= ancien_pas_2 + pas_2 * (i + 1))
            ]) / (365 * 24) )
            for i in range(nbre_case)
             ]
            vecteur_consommation_annee2.insert(0, 0)


            # print('vecteur_heure',vecteur_consommation_heure1)
            # print('vecteur_semaine 1',vecteur_consommation_semaine1)
            # print('vecteur_mois 1',vecteur_consommation_mois1)
            # print('vecteur_annee 1',vecteur_consommation_annee1)
            # print('vecteur_semaine 2',vecteur_consommation_semaine2)
            # print('vecteur_mois 2',vecteur_consommation_mois2)
            # print('vecteur_annee 2',vecteur_consommation_annee2)

            vecteur_consommation_jour1 = [
                  round(len(filtered_data[
                (filtered_data[selected_column] > ancien_pas_1 + pas_1 * i) &
                (filtered_data[selected_column] <= ancien_pas_1 + pas_1 * (i + 1))
            ]) / 24 / 4)
            for i in range(nbre_case)
            ]

            # Calcul du vecteur_consommation_jour2
            vecteur_consommation_jour2 = [
                 round(len(filtered_data[
                (filtered_data[selected_column] * coef > ancien_pas_2 + pas_2 * i) &
                (filtered_data[selected_column] * coef <= ancien_pas_2 + pas_2 * (i + 1))
            ]) / 24 )
                for i in range(nbre_case)
            ]
            vecteur_consommation_jour1.insert(0, 0)
            vecteur_consommation_jour2.insert(0, 0)

            vecteur_consommation1_json = json.dumps(vecteur_consommation1)
            vecteur_consommation2_json = json.dumps(vecteur_consommation2)
            vecteur_pas1_json = json.dumps(vecteur_pas1)
            vecteur_pas2_json = json.dumps(vecteur_pas2)
            vecteur_consommation_jour1_json = json.dumps(vecteur_consommation_jour1)
            vecteur_consommation_jour2_json = json.dumps(vecteur_consommation_jour2)

            # print("Vecteur Consommation 1:", vecteur_consommation1)
            # print("Vecteur Consommation 2:", vecteur_consommation2)
            # print("Vecteur Consommation Jour 1:", vecteur_consommation_jour1)
            # print("Vecteur Consommation Jour 2:", vecteur_consommation_jour2)

             # Calculer la somme totale des vecteurs consommation
            total_vecteur_consommation1 = sum(vecteur_consommation1)
            total_vecteur_consommation2 = sum(vecteur_consommation2)

            # Afficher les résultats
            # print(f"Somme totale de Vecteur Consommation 1: {total_vecteur_consommation1}")
            # print(f"Somme totale de Vecteur Consommation 2: {total_vecteur_consommation2}")

            # Calculer la somme totale des vecteurs consommation par jour
            total_vecteur_consommation_jour1 = sum(vecteur_consommation_jour1)
            total_vecteur_consommation_jour2 = sum(vecteur_consommation_jour2)
            total_vecteur_consommation_heure1 = sum(vecteur_consommation_heure1)
            total_vecteur_consommation_semaine1 = sum(vecteur_consommation_semaine1)
            total_vecteur_consommation_semaine2 = sum(vecteur_consommation_semaine2)
            total_vecteur_consommation_mois1 = sum(vecteur_consommation_mois1)
            total_vecteur_consommation_mois2 = sum(vecteur_consommation_mois2)
            total_vecteur_consommation_annee1 = sum(vecteur_consommation_annee1)
            total_vecteur_consommation_annee2 = sum(vecteur_consommation_annee2)


            # Afficher les résultats
            # print(f"Somme totale de Vecteur Consommation Jour 1: {total_vecteur_consommation_jour1}")
            # print(f"Somme totale de Vecteur Consommation Jour 2: {total_vecteur_consommation_jour2}")

            fichier_obj.min=min_consommation
            fichier_obj.max=max_consommation
            fichier_obj.moyenne=moyenne_consommation
            fichier_obj.pas_1=pas_1
            fichier_obj.pas_2=pas_2
            fichier_obj.nbre_case=nbre_case
            fichier_obj.valeur_max=valeur_maximale
            fichier_obj.total_consommation1=total_vecteur_consommation1
            fichier_obj.total_consommation2=total_vecteur_consommation2
            fichier_obj.total_consommation_jour1=total_vecteur_consommation_jour1
            fichier_obj.total_consommation_jour2=total_vecteur_consommation_jour2
            fichier_obj.total_consommation_heure1=total_vecteur_consommation_heure1
            fichier_obj.total_consommation_semaine1=total_vecteur_consommation_semaine1
            fichier_obj.total_consommation_semaine2=total_vecteur_consommation_semaine2
            fichier_obj.total_consommation_mois1=total_vecteur_consommation_mois1
            fichier_obj.total_consommation_mois2=total_vecteur_consommation_mois2
            fichier_obj.total_consommation_annee1=total_vecteur_consommation_annee1
            fichier_obj.total_consommation_annee2=total_vecteur_consommation_annee2
            fichier_obj.filtered_data_json=encoded_data

            fichier_obj.save()

            calcul_obj = Calcul.objects.create(fichier=fichier_obj)

            for i in range(len(vecteur_pas1)):
                LigneCalcul.objects.create(
                    calcul=calcul_obj,
                    vecteur_pas1=vecteur_pas1[i],
                    vecteur_pas2=vecteur_pas2[i],
                    consommation_pas1=vecteur_consommation1[i],  # Assurez-vous que cette variable est définie dans votre code
                    consommation_pas2=vecteur_consommation2[i],  # Assurez-vous que cette variable est définie dans votre code
                    consommation_jour1=vecteur_consommation_jour1[i],  # Assurez-vous que cette variable est définie dans votre code
                    consommation_jour2=vecteur_consommation_jour2[i],  # Assurez-vous que cette variable est définie dans votre code
                    consommation_pas_heure1=vecteur_consommation_heure1[i],
                    consommation_semaine1=vecteur_consommation_semaine1[i],  # Assurez-vous que cette variable est définie dans votre code
                    consommation_semaine2=vecteur_consommation_semaine2[i],
                    consommation_mois1=vecteur_consommation_mois1[i],  # Assurez-vous que cette variable est définie dans votre code
                    consommation_mois2=vecteur_consommation_mois2[i],
                    consommation_annee1=vecteur_consommation_annee1[i],  # Assurez-vous que cette variable est définie dans votre code
                    consommation_annee2=vecteur_consommation_annee2[i],
                )
            id_fichier=fichier_obj.id
        # Fermer le client Dask à la fin du traitement
            client.close()
            context = {
                 'id_fichier' : id_fichier,
            'valeur_maximale': valeur_maximale,
                'nbre_case': nbre_case,
                'coef': coef,
                'id_compteur':id_compteur,
                'num_compteur':num_compteur,
                'lib_compteur':lib_compteur,
                'source':source,
                'unite':unite,
                'pas_1': pas_1,
                'pas_2': pas_2,
                'min_consommation': min_consommation,
                'max_consommation': max_consommation,
                'moyenne_consommation': moyenne_consommation,
                'vecteur_pas1': vecteur_pas1,
                'longueur_vecteur_pas1': longueur_vecteur_pas1,
                'indices_et_valeurs_pas1': indices_et_valeurs_pas1,
                'vecteur_pas2': vecteur_pas2,
                'vecteur_consommation1': vecteur_consommation1,
                'vecteur_consommation_heure1' : vecteur_consommation_heure1,
                'vecteur_consommation1_json':vecteur_consommation1_json,
                'vecteur_consommation2_json':vecteur_consommation2_json,
                'vecteur_consommation_jour1_json':vecteur_consommation_jour1_json,
                'vecteur_consommation_jour2_json':vecteur_consommation_jour2_json,
                'vecteur_pas1_json':vecteur_pas1_json,
                'vecteur_pas2_json':vecteur_pas2_json,
                'vecteur_consommation2': vecteur_consommation2,
                'vecteur_consommation_jour1': vecteur_consommation_jour1,
                'vecteur_consommation_jour2': vecteur_consommation_jour2,
                'vecteur_consommation_semaine1': vecteur_consommation_semaine1,
                'vecteur_consommation_semaine2': vecteur_consommation_semaine2,
                'vecteur_consommation_mois1' : vecteur_consommation_mois1,
                'vecteur_consommation_mois2' : vecteur_consommation_mois2,
                'vecteur_consommation_annee1' : vecteur_consommation_annee1,
                'vecteur_consommation_annee2' : vecteur_consommation_annee2,
                'total_vecteur_consommation1': total_vecteur_consommation1,
                'total_vecteur_consommation2': total_vecteur_consommation2,
                'total_vecteur_consommation_jour1': total_vecteur_consommation_jour1,
                'total_vecteur_consommation_jour2': total_vecteur_consommation_jour2,
                'total_vecteur_consommation_heure1': total_vecteur_consommation_heure1,
                'total_vecteur_consommation_semaine1': total_vecteur_consommation_semaine1,
                'total_vecteur_consommation_semaine2': total_vecteur_consommation_semaine2,
                'total_vecteur_consommation_mois1': total_vecteur_consommation_mois1,
                'total_vecteur_consommation_mois2': total_vecteur_consommation_mois2,
                'total_vecteur_consommation_annee1': total_vecteur_consommation_annee1,
                'total_vecteur_consommation_annee2': total_vecteur_consommation_annee2,
                'filtered_data_json':filtered_data_json,

        }
        
            return render(request, 'testexcel/upload_success.html', context)
        except ValidationError as e:
            # Gérer les erreurs de validation
            error_message = str(e)

    return render(request, 'testexcel/upload_excel.html', {'error_message': error_message})
