from django.urls import path
from . import views

urlpatterns = [
    # Page principale de la pompe
    path('', views.pompe, name='pompe'),
    
    # API - Démarrer une vente
    path('api/demarrer/', views.demarrer_vente, name='demarrer_vente'),
    
    # API - Simuler le remplissage
    path('api/remplir/', views.remplir, name='remplir'),
    
    # API - Payer et valider
    path('api/payer/', views.payer, name='payer'),
    
    # API - Annuler la vente
    path('api/annuler/', views.annuler, name='annuler'),
      path('api/sync/', views.sync_all, name='sync_all'),  # ← NOUVELLE ROUTE
]