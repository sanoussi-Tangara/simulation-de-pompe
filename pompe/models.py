from django.db import models

class SessionJournee(models.Model):
    pompiste_id = models.IntegerField()
    pompiste_nom = models.CharField(max_length=100)
    station_id = models.IntegerField()
    station_nom = models.CharField(max_length=100)
    token = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)  # ← AJOUTER
    password = models.CharField(max_length=255, blank=True, null=True)  # ← AJOUTER
    date_debut = models.DateTimeField(auto_now_add=True)
    date_fin = models.DateTimeField(null=True, blank=True)
    statut = models.CharField(max_length=20, default='en_cours')
    
    def __str__(self):
        return f"{self.pompiste_nom} - {self.date_debut.strftime('%d/%m/%Y')}"

class VenteSimulee(models.Model):
    session = models.ForeignKey(SessionJournee, on_delete=models.CASCADE)
    type_carburant = models.CharField(max_length=10)
    quantite = models.DecimalField(max_digits=10, decimal_places=2)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    mode_paiement = models.CharField(max_length=20, default='especes')
    date_vente = models.DateTimeField(auto_now_add=True)
    code_validation = models.CharField(max_length=6, blank=True, null=True)
    statut = models.CharField(max_length=20, default='en_cours')
    vente_id_anw = models.IntegerField(null=True, blank=True)  # ID de la vente dans ANW
    synchronise = models.BooleanField(default=False)  # ✅ AJOUTÉ
    tentative_sync = models.IntegerField(default=0)   # ✅ AJOUTÉ
    
    def __str__(self):
        return f"Vente #{self.id} - {self.quantite}L - {'✅' if self.synchronise else '⏳'}"