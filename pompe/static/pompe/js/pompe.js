/* =====================================================
   SIMULATION POMPE
   Application ANW KA TA DJI

   Gestion :
   - Choix carburant
   - Calcul prix
   - Pavé numérique
   - Animation remplissage
   - Paiement
   - Ticket de vente
===================================================== */



// Variables principales

let carburant = "";

let prix = 0;

let litres = 0;

let paiement = "";





/* =====================================================
   CHOIX DU CARBURANT
===================================================== */


function choisirCarburant(nom, prixCarburant){


    carburant = nom;

    prix = prixCarburant;



    document.getElementById("carburant").innerHTML =

    `
    ${nom}
    <br>
    ${prix} FCFA / L
    `;



    calculerMontant();


}







/* =====================================================
   PAVE NUMERIQUE
===================================================== */



function ajouterChiffre(chiffre){


    // évite les nombres trop longs

    if(litres.toString().length >=4){

        return;

    }



    litres = Number(

        litres.toString() + chiffre

    );



    afficher();


}






// Bouton C

function vider(){


    litres = 0;


    afficher();


}






// Bouton supprimer

function supprimerChiffre(){


    litres = litres.toString().slice(0,-1);



    if(litres === ""){


        litres = 0;


    }



    litres = Number(litres);


    afficher();


}








/* =====================================================
   AFFICHAGE ECRAN DIGITAL
===================================================== */


function afficher(){


    document.getElementById("litres").innerHTML =

    litres;



    calculerMontant();


}








/* =====================================================
   CALCUL DU PRIX
===================================================== */


function calculerMontant(){



    let montant = litres * prix;



    document.getElementById("montant").innerHTML =

    montant.toLocaleString();



}










/* =====================================================
   ANIMATION REMPLISSAGE
===================================================== */


function demarrerRemplissage(){



    if(carburant === ""){


        alert(
        "Veuillez choisir le carburant"
        );


        return;

    }



    if(litres <=0){


        alert(
        "Veuillez entrer la quantité"
        );


        return;

    }




    let compteur = 0;


    let barre =

    document.getElementById(
    "progress-bar"
    );



    let animation = setInterval(function(){



        compteur++;



        barre.style.width =

        compteur + "%";




        let litresActuel = Math.floor(

            litres * compteur /100

        );




        document.getElementById("message").innerHTML =


        `
        ⛽ Remplissage :
        ${litresActuel} L / ${litres} L
        `;





        if(compteur >=100){



            clearInterval(animation);



            document.getElementById("message").innerHTML =


            `
            ✅ Remplissage terminé
            `;



        }




    },50);



}








/* =====================================================
   MODE DE PAIEMENT
===================================================== */



function choisirPaiement(mode){



    paiement = mode;



    document.getElementById("paiement").innerHTML =


    mode;



}








/* =====================================================
   VALIDATION VENTE
===================================================== */


function validerVente(){



    if(
        carburant === "" ||

        litres <=0 ||

        paiement === ""

    ){


        alert(

        "Veuillez compléter toutes les informations"

        );


        return;


    }






    let montant = litres * prix;





    document.getElementById("ticket").innerHTML =



    `


    <h2>
    🎫 Ticket de vente
    </h2>


    <hr>


    <b>Carburant :</b>

    ${carburant}


    <br>


    <b>Quantité :</b>

    ${litres} Litres


    <br>


    <b>Montant :</b>

    ${montant.toLocaleString()} FCFA


    <br>


    <b>Paiement :</b>

    ${paiement}


    <br>


    <b>Date :</b>

    ${new Date().toLocaleString()}


    <hr>


    Merci pour votre confiance 🚀



    `;



}