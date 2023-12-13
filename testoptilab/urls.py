from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import details_page,import_donnees,affiche_fichier,upload_excel

app_name = 'testoptilab'  # Assurez-vous d'utiliser le même nom d'espace de noms ici

urlpatterns = [
    path('affichefichier/', affiche_fichier, name='affiche_fichier'),
    path('import_donnees/', import_donnees, name='import_donnees'),
    path('upload/', upload_excel, name='upload_excel'),
    path('detail_page/<int:fichier_id>/', details_page, name='details_page'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
