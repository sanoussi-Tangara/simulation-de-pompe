from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import SessionJournee, VenteSimulee
import json
import random
import requests
import logging

# Configuration du logging
logger = logging.getLogger(__name__)

# URL de l'API ANW KA TA DJI
ANW_API_URL = "http://localhost:8000/api"

# ==============================================
# FONCTION - RÉCUPÉRER UN TOKEN DEPUIS ANW
# ==============================================

def obtenir_token_depuis_anw(email, password):
    """
    Récupère un token depuis ANW KA TA DJI via l'API login
    """
    try:
        print("🔐 Tentative de connexion à ANW pour récupérer un token...")
        
        response = requests.post(
            f"{ANW_API_URL}/login",
            json={
                'email': email,
                'password': password
            },
            timeout=10
        )
        
        print(f"Status code login: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            
            if not token and 'data' in data:
                token = data['data'].get('token')
            
            if token:
                print(f"✅ Token récupéré depuis ANW")
                return token
            else:
                print(f"❌ Aucun token dans la réponse: {data}")
                return None
        else:
            print(f"❌ Erreur login: {response.status_code}")
            print(f"Réponse: {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur récupération token: {e}")
        return None


# ==============================================
# 1. PAGE PRINCIPALE DE LA POMPE
# ==============================================

def pompe(request):
    """Affiche l'interface de la pompe"""
    
    pompiste_id = request.GET.get('pompiste_id')
    pompiste_nom = request.GET.get('nom', 'Pompiste')
    station_id = request.GET.get('station_id', 1)
    station_nom = request.GET.get('station', 'Station')
    token = request.GET.get('token')
    email = request.GET.get('email')
    password = request.GET.get('password')
    
    print("=" * 60)
    print("🚀 PAGE POMPE")
    print(f"Pompiste ID: {pompiste_id}")
    print(f"Pompiste: {pompiste_nom}")
    print(f"Station: {station_nom}")
    print("=" * 60)
    
    session_id = request.GET.get('session_id')
    
    if session_id:
        try:
            session = SessionJournee.objects.get(id=session_id)
            if token and token != session.token:
                session.token = token
            if email:
                session.email = email
            if password:
                session.password = password
            session.save()
            print(f"✅ Session existante: {session.id}")
        except SessionJournee.DoesNotExist:
            session = SessionJournee.objects.create(
                pompiste_id=pompiste_id,
                pompiste_nom=pompiste_nom,
                station_id=station_id,
                station_nom=station_nom,
                token=token,
                email=email,
                password=password
            )
            print(f"✅ Nouvelle session créée: {session.id}")
    else:
        session = SessionJournee.objects.create(
            pompiste_id=pompiste_id,
            pompiste_nom=pompiste_nom,
            station_id=station_id,
            station_nom=station_nom,
            token=token,
            email=email,
            password=password
        )
        print(f"✅ Nouvelle session créée: {session.id}")
    
    print("=" * 60)
    
    prix_essence = 940
    prix_gasoil = 875
    
    return render(request, 'pompe/pompe.html', {
        'pompiste': pompiste_nom,
        'station': station_nom,
        'prix_essence': prix_essence,
        'prix_gasoil': prix_gasoil,
        'session_id': session.id,
        'token': token,
        'pompiste_id': pompiste_id,
        'station_id': station_id,
    })


# ==============================================
# 2. API - DÉMARRER UNE VENTE
# ==============================================

@csrf_exempt
def demarrer_vente(request):
    """Démarre une nouvelle vente"""
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=400)
    
    try:
        data = json.loads(request.body)
        
        print("=" * 60)
        print("📤 DÉMARRER VENTE")
        print(f"Données reçues: {data}")
        
        session_id = data.get('session_id')
        type_carburant = data.get('type_carburant')
        montant = float(data.get('montant', 0))
        
        if not session_id:
            print("❌ session_id manquant!")
            return JsonResponse({
                'success': False,
                'message': 'session_id est requis'
            }, status=400)
        
        print(f"Session ID: {session_id}")
        print(f"Carburant: {type_carburant}")
        print(f"Montant: {montant} FCFA")
        
        try:
            session = SessionJournee.objects.get(id=session_id)
            print(f"✅ Session trouvée: {session.id} - {session.pompiste_nom}")
        except SessionJournee.DoesNotExist:
            print(f"❌ Session {session_id} non trouvée!")
            return JsonResponse({
                'success': False,
                'message': f'Session {session_id} non trouvée. Veuillez recharger la page.'
            }, status=404)
        
        prix_essence = 940
        prix_gasoil = 875
        prix = prix_essence if type_carburant == 'essence' else prix_gasoil
        quantite = round(montant / prix, 2)
        
        print(f"Prix: {prix} FCFA/L")
        print(f"Quantité calculée: {quantite} L")
        
        vente = VenteSimulee.objects.create(
            session_id=session_id,
            type_carburant=type_carburant,
            quantite=quantite,
            montant=montant,
            code_validation=str(random.randint(100000, 999999))
        )
        
        print(f"✅ Vente créée: {vente.id}")
        print(f"Code validation: {vente.code_validation}")
        print("=" * 60)
        
        return JsonResponse({
            'success': True,
            'vente_id': vente.id,
            'quantite': quantite,
            'montant': montant,
            'code_validation': vente.code_validation,
        })
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


# ==============================================
# 3. API - SIMULER LE REMPLISSAGE
# ==============================================

@csrf_exempt
def remplir(request):
    """Simule le remplissage en temps réel"""
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=400)
    
    try:
        data = json.loads(request.body)
        vente_id = data.get('vente_id')
        progression = data.get('progression', 0)
        
        vente = VenteSimulee.objects.get(id=vente_id)
        
        if progression >= 100:
            vente.statut = 'ok'
            vente.save()
        
        return JsonResponse({
            'success': True,
            'progression': progression,
            'statut': vente.statut,
        })
        
    except Exception as e:
        print(f"❌ ERREUR remplissage: {e}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


# ==============================================
# 4. API - PAYER ET VALIDER (AVEC ROUTE PUBLIQUE)
# ==============================================

@csrf_exempt
def payer(request):
    """Valide le paiement et envoie à ANW KA TA DJI via route publique"""
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=400)
    
    try:
        data = json.loads(request.body)
        
        print("=" * 60)
        print("💰 PAIEMENT ET VALIDATION")
        print(f"Données reçues: {data}")
        
        vente_id = data.get('vente_id')
        mode_paiement = data.get('mode_paiement')
        
        print(f"Vente ID: {vente_id}")
        print(f"Mode paiement original: {mode_paiement}")
        
        # ✅ CORRIGER LE MODE DE PAIEMENT
        mode_map = {
            'espèces': 'especes',
            'especes': 'especes',
            'orange money': 'orange_money',
            'orange_money': 'orange_money',
            'mobicash': 'mobicash',
            'wave': 'wave',
            'carte': 'card',
            'card': 'card',
            'orange money': 'orange_money',
            'Orange Money': 'orange_money'
        }
        
        mode_paiement_normalise = mode_map.get(mode_paiement.lower(), 'especes')
        print(f"Mode paiement normalisé: {mode_paiement_normalise}")
        
        vente = VenteSimulee.objects.get(id=vente_id)
        vente.mode_paiement = mode_paiement_normalise
        vente.save()
        
        session = vente.session
        
        print(f"Session pompiste: {session.pompiste_nom}")
        print(f"Station: {session.station_nom}")
        
        # ==========================================
        # ENVOI DE LA VENTE À ANW VIA ROUTE PUBLIQUE
        # ==========================================
        
        data_vente = {
            'pompiste_id': session.pompiste_id,
            'station_id': session.station_id,
            'type_carburant': vente.type_carburant,
            'quantite': float(vente.quantite),
            'montant': float(vente.montant),
            'mode_paiement': mode_paiement_normalise,  # ← MODE CORRIGÉ
        }
        
        print(f"📤 Envoi à ANW (route publique): {data_vente}")
        print(f"URL: {ANW_API_URL}/pompiste/vente/public")
        
        try:
            response = requests.post(
                f"{ANW_API_URL}/pompiste/vente/public",
                json=data_vente,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            print(f"Status code: {response.status_code}")
            print(f"Réponse: {response.text[:500]}")
            print("=" * 60)
            
            if response.status_code in [200, 201]:
                try:
                    resultat = response.json()
                    vente.vente_id_anw = resultat.get('vente', {}).get('id') or resultat.get('id')
                    vente.synchronise = True
                    vente.save()
                    
                    print(f"✅ Vente enregistrée dans ANW (ID: {vente.vente_id_anw})")
                    
                    return JsonResponse({
                        'success': True,
                        'message': 'Vente enregistrée dans ANW KA TA DJI',
                        'vente_id_anw': vente.vente_id_anw,
                        'quantite': float(vente.quantite),
                        'montant': float(vente.montant),
                        'type_carburant': vente.type_carburant,
                        'mode_paiement': vente.mode_paiement,
                        'code_validation': vente.code_validation,
                    })
                except Exception as e:
                    print(f"⚠️ Erreur parsing: {e}")
                    vente.synchronise = False
                    vente.save()
                    return JsonResponse({
                        'success': True,
                        'message': 'Vente enregistrée localement (erreur parsing)',
                        'quantite': float(vente.quantite),
                        'montant': float(vente.montant),
                        'type_carburant': vente.type_carburant,
                        'mode_paiement': vente.mode_paiement,
                        'code_validation': vente.code_validation,
                    })
            else:
                print(f"⚠️ Erreur ANW: {response.status_code}")
                print(f"Détail: {response.text}")
                vente.synchronise = False
                vente.save()
                return JsonResponse({
                    'success': True,
                    'message': f'Vente enregistrée localement (ANW: {response.status_code})',
                    'quantite': float(vente.quantite),
                    'montant': float(vente.montant),
                    'type_carburant': vente.type_carburant,
                    'mode_paiement': vente.mode_paiement,
                    'code_validation': vente.code_validation,
                    'anw_error': True,
                })
                    
        except requests.exceptions.ConnectionError:
            print("❌ ANW hors ligne")
            vente.synchronise = False
            vente.save()
            return JsonResponse({
                'success': True,
                'message': 'Vente enregistrée localement (ANW hors ligne)',
                'quantite': float(vente.quantite),
                'montant': float(vente.montant),
                'type_carburant': vente.type_carburant,
                'mode_paiement': vente.mode_paiement,
                'code_validation': vente.code_validation,
                'anw_hors_ligne': True,
            })
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


# ==============================================
# 5. API - SYNC ALL
# ==============================================

@csrf_exempt
def sync_all(request):
    """Synchronise toutes les ventes en attente"""
    try:
        ventes = VenteSimulee.objects.filter(synchronise=False)
        sync_result = []
        
        for vente in ventes:
            resultat = synchroniser_une_vente(vente.id)
            sync_result.append({
                'id': vente.id,
                'sync': resultat
            })
        
        return JsonResponse({
            'success': True,
            'message': f"{len(sync_result)} ventes traitées",
            'details': sync_result
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


# ==============================================
# 6. FONCTION - SYNCHRONISER UNE VENTE
# ==============================================

def synchroniser_une_vente(vente_id):
    """
    Synchronise une vente spécifique via route publique
    """
    try:
        vente = VenteSimulee.objects.get(id=vente_id)
        session = vente.session
        
        if vente.synchronise:
            return True
        
        # ✅ CORRIGER LE MODE DE PAIEMENT
        mode_map = {
            'espèces': 'especes',
            'especes': 'especes',
            'orange money': 'orange_money',
            'orange_money': 'orange_money',
            'mobicash': 'mobicash',
            'wave': 'wave',
            'carte': 'card',
            'card': 'card'
        }
        
        mode_paiement_normalise = mode_map.get(vente.mode_paiement.lower(), 'especes')
        
        data = {
            'pompiste_id': session.pompiste_id,
            'station_id': session.station_id,
            'type_carburant': vente.type_carburant,
            'quantite': float(vente.quantite),
            'montant': float(vente.montant),
            'mode_paiement': mode_paiement_normalise,  # ← MODE CORRIGÉ
        }
        
        response = requests.post(
            f"{ANW_API_URL}/pompiste/vente/public",
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            vente.synchronise = True
            vente.save()
            print(f"✅ Vente {vente.id} synchronisée")
            return True
        else:
            vente.tentative_sync = (vente.tentative_sync or 0) + 1
            vente.save()
            print(f"⚠️ Vente {vente.id} non synchronisée (tentative {vente.tentative_sync})")
            return False
            
    except Exception as e:
        print(f"❌ Erreur synchronisation: {e}")
        return False


# ==============================================
# 7. API - ANNULER LA VENTE
# ==============================================

@csrf_exempt
def annuler(request):
    """Annule la vente en cours"""
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=400)
    
    try:
        data = json.loads(request.body)
        vente_id = data.get('vente_id')
        
        print(f"❌ Annulation de la vente: {vente_id}")
        
        vente = VenteSimulee.objects.get(id=vente_id)
        vente.statut = 'annule'
        vente.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Vente annulée',
        })
        
    except Exception as e:
        print(f"❌ ERREUR annulation: {e}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


# ==============================================
# 8. API - RÉCUPÉRER LES PRIX DEPUIS ANW
# ==============================================

def get_prix_anw(request):
    """Récupère les prix depuis ANW KA TA DJI"""
    
    try:
        token = request.GET.get('token')
        
        if not token:
            print("❌ Aucun token fourni pour récupérer les prix")
            return JsonResponse({
                'success': False,
                'essence': 875,
                'gasoil': 940,
            })
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        print(f"📤 Récupération des prix depuis ANW")
        print(f"URL: {ANW_API_URL}/pompiste/prix")
        
        response = requests.get(
            f"{ANW_API_URL}/pompiste/prix",
            headers=headers
        )
        
        print(f"Status code: {response.status_code}")
        print(f"Réponse: {response.text[:200]}")
        
        if response.status_code == 200:
            data = response.json()
            return JsonResponse({
                'success': True,
                'essence': data.get('essence', 940),
                'gasoil': data.get('gasoil', 875),
            })
        else:
            return JsonResponse({
                'success': False,
                'essence': 875,
                'gasoil': 940,
            })
            
    except Exception as e:
        print(f"❌ Erreur récupération prix: {e}")
        return JsonResponse({
            'success': False,
            'essence': 875,
            'gasoil': 940,
        })