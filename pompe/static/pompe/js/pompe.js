/* =====================================================
   SIMULATION POMPE - ANW KA TA DJI
   Gestion :
   - Choix carburant
   - Saisie du montant (FCFA)
   - Calcul automatique des litres
   - Animation remplissage
   - Paiement
   - Envoi à l'API Django
   - Ticket de vente
===================================================== */

// Variables principales
let carburant = "";
let prix = 0;
let montantSaisi = 0;
let litres = 0;
let paiement = "";
let paiementAffichage = "";
let venteId = null;
let sessionId = null;

// ✅ Récupérer session_id depuis le champ caché HTML
const sessionIdEl = document.getElementById('session-id');
if (sessionIdEl) {
    sessionId = parseInt(sessionIdEl.value);
    console.log("🔍 Session ID récupéré du champ caché:", sessionId);
} else {
    // Fallback: essayer de récupérer depuis l'URL
    const urlParams = new URLSearchParams(window.location.search);
    sessionId = urlParams.get('session_id');
    console.log("🔍 Session ID récupéré de l'URL:", sessionId);
}

if (!sessionId) {
    console.error("❌ Aucun session_id trouvé !");
}

// Références DOM
const carburantEl = document.getElementById("carburant");
const montantSaisiEl = document.getElementById("montant-saisi");
const litresEl = document.getElementById("litres");
const messageEl = document.getElementById("message");
const progressBar = document.getElementById("progress-bar");
const btnDemarrer = document.getElementById("btn-demarrer");
const btnValider = document.getElementById("btn-valider");

// ✅ TABLE DE CONVERSION DES MODES DE PAIEMENT
const MODE_PAIEMENT_MAP = {
    'espèces': 'especes',
    'Espèces': 'especes',
    'especes': 'especes',
    'orange money': 'orange_money',
    'Orange Money': 'orange_money',
    'orange_money': 'orange_money',
    'mobicash': 'mobicash',
    'Mobicash': 'mobicash',
    'wave': 'wave',
    'Wave': 'wave',
    'carte': 'card',
    'Carte': 'card',
    'card': 'card'
};

function normaliserModePaiement(mode) {
    return MODE_PAIEMENT_MAP[mode] || 'especes';
}

/* =====================================================
   CHOIX DU CARBURANT
===================================================== */

function choisirCarburant(nom, prixCarburant) {
    carburant = nom;
    prix = prixCarburant;

    carburantEl.innerHTML = `
        ${nom}
        <br>
        ${prix} FCFA / L
    `;

    calculerLitres();
    verifierFormulaire();
    
    console.log(`✅ Carburant choisi: ${nom} - ${prix} FCFA/L`);
}

/* =====================================================
   PAVE NUMÉRIQUE (SAISIE DU MONTANT EN FCFA)
===================================================== */

function ajouterChiffre(chiffre) {
    if (montantSaisi.toString().length >= 7) {
        return;
    }

    montantSaisi = Number(montantSaisi.toString() + chiffre);
    afficher();
    verifierFormulaire();
}

function vider() {
    montantSaisi = 0;
    litres = 0;
    afficher();
    verifierFormulaire();
}

function supprimerChiffre() {
    let str = montantSaisi.toString();
    str = str.slice(0, -1);
    montantSaisi = str === "" ? 0 : Number(str);
    afficher();
    verifierFormulaire();
}

/* =====================================================
   AFFICHAGE ÉCRAN
===================================================== */

function afficher() {
    montantSaisiEl.textContent = montantSaisi.toLocaleString();
    calculerLitres();
}

function calculerLitres() {
    if (prix > 0 && montantSaisi > 0) {
        litres = montantSaisi / prix;
        litresEl.textContent = litres.toFixed(2);
    } else {
        litres = 0;
        litresEl.textContent = "0.00";
    }
}

/* =====================================================
   VÉRIFICATION DU FORMULAIRE
===================================================== */

function verifierFormulaire() {
    if (carburant !== "" && montantSaisi > 0) {
        btnDemarrer.disabled = false;
        btnDemarrer.style.opacity = "1";
    } else {
        btnDemarrer.disabled = true;
        btnDemarrer.style.opacity = "0.5";
    }

    if (carburant !== "" && montantSaisi > 0 && paiement !== "") {
        btnValider.disabled = false;
        btnValider.style.opacity = "1";
    } else {
        btnValider.disabled = true;
        btnValider.style.opacity = "0.5";
    }
}

/* =====================================================
   DÉMARRER LE REMPLISSAGE - AVEC API
===================================================== */

async function demarrerRemplissage() {
    if (carburant === "") {
        alert("Veuillez choisir le carburant");
        return;
    }

    if (montantSaisi <= 0) {
        alert("Veuillez entrer un montant valide");
        return;
    }

    // ✅ Vérifier que sessionId est valide
    if (!sessionId) {
        alert("❌ Erreur: Session non trouvée. Veuillez recharger la page.");
        console.error("❌ Session ID est null");
        return;
    }

    btnDemarrer.disabled = true;
    btnDemarrer.style.opacity = "0.5";

    try {
        console.log("📤 Démarrage vente...");
        console.log("Session ID:", sessionId);
        console.log("Carburant:", carburant);
        console.log("Montant:", montantSaisi);

        // Appel à l'API Django pour démarrer la vente
        const response = await fetch('/api/demarrer/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: parseInt(sessionId),
                type_carburant: carburant.toLowerCase(),
                montant: montantSaisi
            })
        });

        const data = await response.json();
        console.log("📥 Réponse:", data);

        if (data.success) {
            venteId = data.vente_id;
            console.log(`✅ Vente démarrée (ID: ${venteId})`);
            startRemplissage(venteId);
        } else {
            alert("❌ Erreur: " + data.message);
            btnDemarrer.disabled = false;
            btnDemarrer.style.opacity = "1";
        }

    } catch (error) {
        console.error("❌ Erreur:", error);
        alert("❌ Erreur lors du démarrage de la vente");
        btnDemarrer.disabled = false;
        btnDemarrer.style.opacity = "1";
    }
}

/* =====================================================
   SIMULATION DU REMPLISSAGE
===================================================== */

function startRemplissage(venteId) {
    let compteur = 0;
    const totalLitres = litres;
    const totalMontant = montantSaisi;

    progressBar.style.width = "0%";
    messageEl.innerHTML = "⛽ Remplissage en cours...";

    const interval = setInterval(function() {
        compteur++;

        progressBar.style.width = compteur + "%";

        let litresActuel = (totalLitres * compteur) / 100;
        let montantActuel = (totalMontant * compteur) / 100;

        montantSaisiEl.textContent = Math.floor(montantActuel).toLocaleString();
        litresEl.textContent = litresActuel.toFixed(2);

        messageEl.innerHTML = `
            ⛽ Remplissage : 
            ${litresActuel.toFixed(2)} L / ${totalLitres.toFixed(2)} L
            <br>
            💰 ${Math.floor(montantActuel).toLocaleString()} FCFA / ${totalMontant.toLocaleString()} FCFA
        `;

        // Envoyer la progression à Django
        fetch('/api/remplir/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                vente_id: venteId,
                progression: compteur
            })
        }).catch(err => console.error("Erreur progression:", err));

        if (compteur >= 100) {
            clearInterval(interval);

            montantSaisiEl.textContent = totalMontant.toLocaleString();
            litresEl.textContent = totalLitres.toFixed(2);

            messageEl.innerHTML = `
                ✅ Remplissage terminé !
                <br>
                ${totalLitres.toFixed(2)} L de ${carburant}
                <br>
                Montant : ${totalMontant.toLocaleString()} FCFA
            `;

            verifierFormulaire();
        }
    }, 50);
}

/* =====================================================
   MODE DE PAIEMENT
===================================================== */

function choisirPaiement(mode) {
    paiementAffichage = mode;  // Pour l'affichage (ex: "Orange Money")
    paiement = normaliserModePaiement(mode);  // Pour l'API (ex: "orange_money")
    
    document.getElementById("paiement").textContent = paiementAffichage;
    verifierFormulaire();
    
    console.log(`✅ Paiement choisi: ${paiementAffichage} → ${paiement}`);
}

/* =====================================================
   VALIDATION DE LA VENTE - AVEC API
===================================================== */

async function validerVente() {
    if (carburant === "" || montantSaisi <= 0 || paiement === "") {
        alert("Veuillez compléter toutes les informations");
        return;
    }

    if (!venteId) {
        alert("Aucune vente en cours. Veuillez démarrer le remplissage d'abord.");
        return;
    }

    btnValider.disabled = true;
    btnValider.style.opacity = "0.5";

    try {
        console.log("📤 Validation de la vente...");
        console.log("Vente ID:", venteId);
        console.log("Paiement (normalisé):", paiement);

        // Appel à l'API Django pour payer
        const response = await fetch('/api/payer/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                vente_id: venteId,
                mode_paiement: paiement  // ← Envoyer le mode normalisé
            })
        });

        const data = await response.json();
        console.log("📥 Réponse:", data);

        if (data.success) {
            // Afficher le ticket avec les données de la vente
            document.getElementById("ticket").innerHTML = `
                <h2>🎫 Ticket de vente</h2>
                <hr>
                <p><b>Carburant :</b> ${carburant}</p>
                <p><b>Quantité :</b> ${litres.toFixed(2)} Litres</p>
                <p><b>Montant :</b> ${montantSaisi.toLocaleString()} FCFA</p>
                <p><b>Paiement :</b> ${paiementAffichage}</p>
                <p><b>Date :</b> ${new Date().toLocaleString()}</p>
                ${data.vente_id_anw ? `<p><b>ID ANW :</b> ${data.vente_id_anw}</p>` : ''}
                ${data.anw_error ? `<p style="color:orange;"><b>⚠️ Vente enregistrée localement (ANW hors ligne)</b></p>` : ''}
                <hr>
                <p><b>✅ MERCI DE VOTRE CONFIANCE !</b> </p>
                <hr>
                <p><small>ANW KA TA DJI - Notre carburant</small></p>
            `;

            btnDemarrer.disabled = true;
            btnValider.disabled = true;
            btnDemarrer.style.opacity = "0.5";
            btnValider.style.opacity = "0.5";

            alert("✅ Vente validée avec succès !");
        } else {
            alert("❌ Erreur: " + data.message);
            btnValider.disabled = false;
            btnValider.style.opacity = "1";
        }

    } catch (error) {
        console.error("❌ Erreur:", error);
        alert("❌ Erreur lors de la validation");
        btnValider.disabled = false;
        btnValider.style.opacity = "1";
    }
}

/* =====================================================
   RÉINITIALISATION
===================================================== */

function reinitialiser() {
    carburant = "";
    prix = 0;
    montantSaisi = 0;
    litres = 0;
    paiement = "";
    paiementAffichage = "";
    venteId = null;

    carburantEl.innerHTML = "Aucun carburant sélectionné";
    montantSaisiEl.textContent = "0";
    litresEl.textContent = "0.00";
    messageEl.innerHTML = "";
    progressBar.style.width = "0%";
    document.getElementById("paiement").textContent = "Aucun";
    document.getElementById("ticket").innerHTML = "";

    btnDemarrer.disabled = true;
    btnValider.disabled = true;
    btnDemarrer.style.opacity = "0.5";
    btnValider.style.opacity = "0.5";

    document.querySelectorAll('.carburants button').forEach(btn => {
        btn.style.border = '2px solid #ddd';
        btn.style.background = '#f5f5f5';
        btn.style.color = '#333';
    });

    console.log("🔄 Vente réinitialisée");
}

/* =====================================================
   INITIALISATION
===================================================== */

console.log("🚀 Simulation pompe chargée");
console.log("Session ID:", sessionId);

// Ajout d'un bouton "Nouvelle vente"
document.addEventListener('DOMContentLoaded', function() {
    const container = document.querySelector('.pompe-card');
    const btnNouvelle = document.createElement('button');
    btnNouvelle.textContent = '🔄 Nouvelle vente';
    btnNouvelle.className = 'nouvelle-vente';
    btnNouvelle.style.cssText = `
        width: 100%;
        padding: 12px;
        margin-top: 15px;
        background: #3498db;
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 16px;
        cursor: pointer;
        transition: 0.3s;
    `;
    btnNouvelle.onclick = reinitialiser;
    btnNouvelle.onmouseover = function() { this.style.background = '#2980b9'; };
    btnNouvelle.onmouseout = function() { this.style.background = '#3498db'; };
    container.appendChild(btnNouvelle);
});