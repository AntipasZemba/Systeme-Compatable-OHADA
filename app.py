"""
=====================================================================
APPLICATION COMPTABLE OHADA (SYSTÈME NORMALISÉ)
Fichier unique : app.py
Contraintes : > 500 lignes, No SQL, No Tkinter, Base Vierge au démarrage
=====================================================================
Ce programme simule un progiciel de gestion comptable complet en ligne 
de commande. Il respecte les règles fondamentales de la partie double, 
de la validation des comptes du référentiel et de la génération 
dynamique des états financiers (Journal, Grand Livre, Balance, 
Compte de Résultat et Bilan).
"""

import sys
import os
from datetime import datetime

# =====================================================================
# 1. BASE DE DONNÉES EN MÉMOIRE (RÉFÉRENTIEL COMPTABLE SYSCOHADA)
# =====================================================================

# Plan Comptable Général OHADA révisé - Extrait exhaustif des classes 1 à 8
PLAN_COMPTABLE_OHADA = {
    # -----------------------------------------------------------------
    # CLASSE 1 : COMPTES DE RESSOURCES DURABLES
    # -----------------------------------------------------------------
    "101000": "Capital social",
    "102000": "Capital des entreprises individuelles",
    "111000": "Réserve légale",
    "112000": "Réserves statutaires ou contractuelles",
    "121000": "Emprunts et dettes financières diverses",
    "131000": "Résultat net de l'exercice (Bénéfice)",
    "139000": "Résultat net de l'exercice (Perte)",
    "141000": "Subventions d'investissement",
    "161000": "Provisions pour litiges",
    "165000": "Provisions pour grosses réparations",
    
    # -----------------------------------------------------------------
    # CLASSE 2 : COMPTES D'ACTIF IMMOBILISÉ
    # -----------------------------------------------------------------
    "211000": "Frais de développement",
    "212000": "Brevets, licences, logiciels",
    "221000": "Terrains",
    "222000": "Terrains aménagés",
    "231000": "Bâtiments",
    "234000": "Installations complexes",
    "241000": "Matériel industriel",
    "242000": "Installations techniques",
    "244000": "Matériel informatique",
    "245000": "Matériel de transport",
    "247000": "Agencements, aménagements",
    "271000": "Titres de participation",
    "274000": "Prêts accordés",
    
    # -----------------------------------------------------------------
    # CLASSE 3 : COMPTES DE STOCKS
    # -----------------------------------------------------------------
    "311000": "Marchandises",
    "321000": "Matières premières",
    "335000": "Produits finis",
    "371000": "Approvisionnements consommables",
    
    # -----------------------------------------------------------------
    # CLASSE 4 : COMPTES DE TIERS
    # -----------------------------------------------------------------
    "401100": "Fournisseurs d'exploitation",
    "401200": "Fournisseurs d'immobilisations",
    "411100": "Clients",
    "412000": "Clients, effets à recevoir",
    "422000": "Personnel, rémunérations dues",
    "431000": "Sécurité sociale",
    "442100": "État, impôt sur le résultat",
    "443100": "État, TVA facturée",
    "445100": "État, TVA récupérable",
    "445300": "État, TVA due",
    "461000": "Débiteurs divers",
    "471000": "Comptes d'attente",
    
    # -----------------------------------------------------------------
    # CLASSE 5 : COMPTES DE TRÉSORERIE
    # -----------------------------------------------------------------
    "521100": "Banques locales",
    "521200": "Banques devises",
    "531100": "Chèques à encaisser",
    "571100": "Caisse principale",
    "571200": "Caisse secondaire",
    
    # -----------------------------------------------------------------
    # CLASSE 6 : COMPTES DE CHARGES DES ACTIVITÉS ORDINAIRES
    # -----------------------------------------------------------------
    "601100": "Achats de marchandises",
    "601200": "Rabais, remises obtenus sur achats",
    "602100": "Achats de matières premières",
    "605100": "Fournitures non stockables (Eau, Électricité)",
    "611000": "Transports",
    "622000": "Locations et charges locatives",
    "624000": "Entretien, réparations",
    "625000": "Primes d'assurances",
    "632000": "Rémunérations d'intermédiaires et honoraires",
    "633000": "Frais de publicité",
    "641100": "Impôts et taxes directs",
    "651000": "Frais de déplacement et missions",
    "661100": "Charges de personnel",
    "664000": "Charges sociales",
    "671000": "Intérêts des emprunts",
    "691000": "Dotations aux amortissements",
    
    # -----------------------------------------------------------------
    # CLASSE 7 : COMPTES DE PRODUITS DES ACTIVITÉS ORDINAIRES
    # -----------------------------------------------------------------
    "701100": "Ventes de marchandises",
    "702100": "Ventes de produits finis",
    "706000": "Services vendus",
    "707100": "Produits accessoires",
    "754000": "Subventions d'exploitation",
    "771000": "Intérêts courus et produits assimilés",
    "791000": "Reprises d'amortissements et provisions",
    
    # -----------------------------------------------------------------
    # CLASSE 8 : COMPTES DES AUTRES CHARGES/PRODUITS (HAO)
    # -----------------------------------------------------------------
    "811000": "Valeurs comptables des cessions d'immobilisations",
    "821000": "Produits des cessions d'immobilisations",
    "831000": "Dons et libéralités accordés",
    "841000": "Dons et libéralités reçus",
    "851000": "Créances irrécouvrables HAO"
}

# Variable globale stockant le registre des écritures
JOURNAL_COMPTABLE = []

# =====================================================================
# 2. LOGIQUE MÉTIER ET CLASSES DE VALIDATION COMPTABLE
# =====================================================================

class EcritureComptable:
    """Représente une pièce comptable standardisée."""
    def __init__(self, identifiant, date_str, libelle):
        self.identifiant = identifiant
        try:
            self.date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            self.date = datetime.today().date()
        self.libelle = libelle
        self.debits = []   # Format: (compte_id, montant_float)
        self.credits = []  # Format: (compte_id, montant_float)

    def ajouter_debit(self, compte, montant):
        """Injecte une ligne au débit après validations strictes."""
        if compte not in PLAN_COMPTABLE_OHADA:
            raise ValueError(f"Le compte {compte} n'est pas référencé dans le plan OHADA.")
        if montant <= 0:
            raise ValueError("Le montant doit être strictement positif.")
        self.debits.append((compte, float(montant)))

    def ajouter_credit(self, compte, montant):
        """Injecte une ligne au crédit après validations strictes."""
        if compte not in PLAN_COMPTABLE_OHADA:
            raise ValueError(f"Le compte {compte} n'est pas référencé dans le plan OHADA.")
        if montant <= 0:
            raise ValueError("Le montant doit être strictement positif.")
        self.credits.append((compte, float(montant)))

    def est_equilibree(self):
        """Vérifie le respect absolu de la partie double."""
        total_debit = sum(m for _, m in self.debits)
        total_credit = sum(m for _, m in self.credits)
        return abs(total_debit - total_credit) < 0.01

    def obtenir_total(self):
        """Retourne le volume financier total de l'écriture."""
        return sum(m for _, m in self.debits)


# =====================================================================
# 3. JEU DE DONNÉES INITIAL (CONSERVÉ POUR ARCHIVE OU CHARGEMENT MANUEL)
# =====================================================================

def charger_donnees_initiales():
    """Générateur d'écritures de démonstration (désactivé par défaut)."""
    global JOURNAL_COMPTABLE
    if JOURNAL_COMPTABLE:
        return
    
    # Écritures témoins à titre d'exemple structurel
    e1 = EcritureComptable(1, "2026-01-02", "Apport initial de capital")
    e1.ajouter_debit("521100", 50000000.0) 
    e1.ajouter_credit("101000", 50000000.0) 
    JOURNAL_COMPTABLE.append(e1)

    e2 = EcritureComptable(2, "2026-01-05", "Emprunt bancaire contracté")
    e2.ajouter_debit("521100", 15000000.0)
    e2.ajouter_credit("121000", 15000000.0)
    JOURNAL_COMPTABLE.append(e2)


# =====================================================================
# 4. MOTEURS DE CALCULS ET SYNTHÈSES COMPTABLES
# =====================================================================

def generer_grand_livre():
    """Génère le Grand Livre par regroupement et traitement analytique."""
    grand_livre = {}
    
    for cpte in PLAN_COMPTABLE_OHADA:
        grand_livre[cpte] = {"debits": [], "credits": [], "total_debit": 0.0, "total_credit": 0.0}

    for ecriture in JOURNAL_COMPTABLE:
        for cpte, mnt in ecriture.debits:
            if cpte in grand_livre:
                grand_livre[cpte]["debits"].append((ecriture.date, ecriture.libelle, mnt))
                grand_livre[cpte]["total_debit"] += mnt
        for cpte, mnt in ecriture.credits:
            if cpte in grand_livre:
                grand_livre[cpte]["credits"].append((ecriture.date, ecriture.libelle, mnt))
                grand_livre[cpte]["total_credit"] += mnt
                
    return grand_livre


def generer_balance():
    """Compile la balance des comptes à 6 colonnes."""
    gl = generer_grand_livre()
    balance = {}
    
    for cpte, data in gl.items():
        td = data["total_debit"]
        tc = data["total_credit"]
        
        if td == 0 and tc == 0:
            continue
            
        solde_debit = 0.0
        solde_credit = 0.0
        
        if td >= tc:
            solde_debit = td - tc
        else:
            solde_credit = tc - td
            
        balance[cpte] = {
            "intitule": PLAN_COMPTABLE_OHADA[cpte],
            "total_debit": td,
            "total_credit": tc,
            "solde_debit": solde_debit,
            "solde_credit": solde_credit
        }
    return balance


def calculer_resultat_net():
    """Calcule le résultat net (Produits [Cl 7] - Charges [Cl 6, 8])"""
    gl = generer_grand_livre()
    total_charges = 0.0
    total_produits = 0.0
    
    for cpte, data in gl.items():
        if cpte.startswith('6') or cpte.startswith('81') or cpte.startswith('83') or cpte.startswith('85'):
            total_charges += (data["total_debit"] - data["total_credit"])
        elif cpte.startswith('7') or cpte.startswith('82') or cpte.startswith('84'):
            total_produits += (data["total_credit"] - data["total_debit"])
            
    resultat = total_produits - total_charges
    return resultat, total_charges, total_produits


# =====================================================================
# 5. COUCHE INTERFACE UTILISATEUR (UI CONSOLE TERMINAL)
# =====================================================================

def separateur(caractere="-", longueur=80):
    print(caractere * longueur)


def afficher_titre(titre):
    print("\n" + "=" * 80)
    print(f" {titre.upper()} ".center(80, "="))
    print("=" * 80 + "\n")


def menu_principal():
    print("\n" + "•" * 60)
    print(" SYSTEME COMPTABLE OHADA - BASE VIERGE ".center(60, "•"))
    print("•" * 60)
    print(" 1. Saisie d'une écriture comptable au Journal")
    print(" 2. Visualiser le Journal Général")
    print(" 3. Consulter le Grand Livre")
    print(" 4. Générer la Balance des Comptes (6 colonnes)")
    print(" 5. Afficher le Compte de Résultat")
    print(" 6. Consulter le Bilan Comptable Actif/Passif")
    print(" 7. Gérer le Plan Comptable (Affichage / Ajout)")
    print(" 8. Analyses financières, Audit & Clôture")
    print(" 9. Exporter la Liasse Financière (.TXT)")
    print(" 0. Quitter l'application")
    separateur("•", 60)


def UI_saisie_ecriture():
    global JOURNAL_COMPTABLE
    print("\n=== SAISIE D'UNE NOUVELLE PIÈCE COMPTABLE ===")
    print("(Tapez 'q' à tout moment pour avorter et retourner au menu principal)")
    
    # 1. Traitement de l'en-tête
    date_ecr = input("Date comptable (AAAA-MM-JJ) : ").strip()
    if date_ecr.lower() == 'q': 
        print("[!] Saisie annulée."); return
    if not date_ecr:
        date_ecr = datetime.today().strftime('%Y-%m-%d')
        print(f"[*] Date par défaut affectée : {date_ecr}")
        
    libelle = input("Libellé explicite de l'opération : ").strip()
    if libelle.lower() == 'q': 
        print("[!] Saisie annulée."); return
    if not libelle:
        print("[-] Erreur : Le libellé ne peut demeurer vide.")
        return

    lignes_debit = []
    lignes_credit = []

    # 2. Saisie du bloc Débit
    print("\n--- BLOC DÉBIT ---")
    while True:
        compte = input("N° de compte Débiteur (ou 'f' pour finaliser le Débit) : ").strip()
        if compte.lower() == 'q':
            print("[!] Saisie annulée."); return
        if compte.lower() == 'f':
            if not lignes_debit:
                print("[-] Erreur de cohérence : Au moins une ligne de débit est obligatoire.")
                continue
            break
        
        if compte not in PLAN_COMPTABLE_OHADA:
            print("[-] Erreur : Ce compte n'existe pas dans le référentiel SYSCOHADA.")
            continue

        montant_str = input(f"Montant Débit pour {compte} ({PLAN_COMPTABLE_OHADA[compte]}) : ").strip()
        if montant_str.lower() == 'q':
            print("[!] Saisie annulée."); return
        if montant_str.lower() == 'f':
            print("[-] Opération impossible. Saisissez d'abord la valeur numérique.")
            continue
        
        try:
            montant = float(montant_str)
            if montant <= 0:
                print("[-] Erreur : Le montant doit être strictement positif.")
                continue
            lignes_debit.append((compte, montant))
        except ValueError:
            print("[-] Erreur : Format numérique invalide.")

    # 3. Saisie du bloc Crédit
    print("\n--- BLOC CRÉDIT ---")
    while True:
        compte = input("N° de compte Créditeur (ou 'f' pour finaliser le Crédit) : ").strip()
        if compte.lower() == 'q':
            print("[!] Saisie annulée."); return
        if compte.lower() == 'f':
            if not lignes_credit:
                print("[-] Erreur de cohérence : Au moins une ligne de crédit est obligatoire.")
                continue
            break

        if compte not in PLAN_COMPTABLE_OHADA:
            print("[-] Erreur : Ce compte n'existe pas dans le référentiel SYSCOHADA.")
            continue

        montant_str = input(f"Montant Crédit pour {compte} ({PLAN_COMPTABLE_OHADA[compte]}) : ").strip()
        if montant_str.lower() == 'q':
            print("[!] Saisie annulée."); return
        if montant_str.lower() == 'f':
            print("[-] Opération impossible. Saisissez d'abord la valeur numérique.")
            continue
        
        try:
            montant = float(montant_str)
            if montant <= 0:
                print("[-] Erreur : Le montant doit être strictement positif.")
                continue
            lignes_credit.append((compte, montant))
        except ValueError:
            print("[-] Erreur : Format numérique invalide.")

    # 4. Phase de validation de l'équilibre financier (Partie double)
    total_debit = sum(m for _, m in lignes_debit)
    total_credit = sum(m for _, m in lignes_credit)

    if abs(total_debit - total_credit) > 0.01:
        print(f"\n[X] REJET DE L'ÉCRITURE : Déséquilibre constaté !")
        print(f"Total Débit : {total_debit:,.2f} | Total Crédit : {total_credit:,.2f}")
        print("[!] Les livres comptables OHADA exigent un équilibre parfait. Saisie effacée.")
        return

    # 5. Injection finale dans la base en mémoire
    prochain_id = len(JOURNAL_COMPTABLE) + 1
    nouvelle_ecriture = EcritureComptable(prochain_id, date_ecr, libelle)
    
    for c, m in lignes_debit:
        nouvelle_ecriture.ajouter_debit(c, m)
    for c, m in lignes_credit:
        nouvelle_ecriture.ajouter_credit(c, m)
        
    JOURNAL_COMPTABLE.append(nouvelle_ecriture)
    print(f"\n[✔] Succès : Pièce comptable N°{prochain_id:04d} archivée avec succès ({total_debit:,.2f} USD) !")


def UI_afficher_journal():
    afficher_titre("Journal Général de l'Exercice")
    if not JOURNAL_COMPTABLE:
        print("[*] Le journal général ne contient aucune écriture pour le moment.")
        return

    print(f"{'Date':<12} | {'Compte':<8} | {'Intitulé du compte / Libellé':<40} | {'Débit (USD)':<15} | {'Crédit (USD)':<15}")
    separateur("=", 100)

    for ecriture in JOURNAL_COMPTABLE:
        print(f"{ecriture.date.strftime('%Y-%m-%d'):<12} | {'':<8} | Pièce N°{ecriture.identifiant:04d}: {ecriture.libelle:<32} | {'':<15} | {'':<15}")
        
        for cpte, mnt in ecriture.debits:
            print(f"{'':<12} | {cpte:<8} |   D: {PLAN_COMPTABLE_OHADA[cpte][:35]:<35} | {mnt:<15,.2f} | {'':<15}")
            
        for cpte, mnt in ecriture.credits:
            print(f"{'':<12} | {cpte:<8} |   C: {PLAN_COMPTABLE_OHADA[cpte][:35]:<35} | {'':<15} | {mnt:<15,.2f}")
        separateur("-", 100)


def UI_consulter_grand_livre():
    afficher_titre("Grand Livre des Comptes")
    gl = generer_grand_livre()
    
    compte_recherche = input("Entrez un numéro de compte spécifique (ou 'Tous' pour l'intégralité) : ").strip()
    
    comptes_a_afficher = []
    if compte_recherche.lower() == 'tous' or compte_recherche == '':
        comptes_a_afficher = [c for c, d in gl.items() if d["total_debit"] > 0 or d["total_credit"] > 0]
    else:
        if compte_recherche in gl:
            comptes_a_afficher = [compte_recherche]
        else:
            print("[-] Erreur : Ce compte ne présente aucun mouvement historique ou est introuvable.")
            return

    if not comptes_a_afficher:
        print("[*] Aucun flux n'a encore transité par les comptes de l'application.")
        return

    for cpte in sorted(comptes_a_afficher):
        data = gl[cpte]
        print(f"\nCOMPTE {cpte} : {PLAN_COMPTABLE_OHADA[cpte].upper()}")
        separateur("-", 85)
        print(f" {'DÉBIT':<39} | {'CRÉDIT':<40}")
        print(f" {'Date':<6} | {'Libellé':<15} | {'Montant':<12} | {'Date':<6} | {'Libellé':<15} | {'Montant':<12}")
        separateur("-", 85)
        
        debits = data["debits"]
        credits = data["credits"]
        max_len = max(len(debits), len(credits))
        
        for i in range(max_len):
            line_deb = ""
            line_crd = ""
            if i < len(debits):
                d_date, d_lib, d_mnt = debits[i]
                line_deb = f"{d_date.strftime('%m-%d'):<6} | {d_lib[:14]:<14} | {d_mnt:<12,.0f}"
            else:
                line_deb = f"{'':<6} | {'':<14} | {'':<12}"
                
            if i < len(credits):
                c_date, c_lib, c_mnt = credits[i]
                line_crd = f"{c_date.strftime('%m-%d'):<6} | {c_lib[:14]:<14} | {c_mnt:<12,.0f}"
            else:
                line_crd = f"{'':<6} | {'':<14} | {'':<12}"
                
            print(f" {line_deb} | {line_crd}")
            
        separateur(".", 85)
        solde = data["total_debit"] - data["total_credit"]
        print(f" Total Débit  : {data['total_debit']:<22,.2f} | Total Crédit : {data['total_credit']:<22,.2f}")
        if solde >= 0:
            print(f" SOLDE DÉBITEUR : {solde:,.2f}")
        else:
            print(f" SOLDE CRÉDITEUR : {abs(solde):,.2f}")
        separateur("=", 85)


def UI_generer_balance():
    afficher_titre("Balance Générale des Comptes (6 Colonnes)")
    balance = generer_balance()
    
    if not balance:
        print("[*] La balance est vierge. Saisissez d'abord des écritures comptables.")
        return

    print(f"{'Numéro':<7} | {'Intitulé du Compte':<28} | {'Mvt Débit':<12} | {'Mvt Crédit':<12} | {'Solde Deb':<11} | {'Solde Crd':<11}")
    separateur("=", 100)
    
    tot_mvt_deb = tot_mvt_crd = tot_sld_deb = tot_sld_crd = 0.0
    
    for cpte in sorted(balance.keys()):
        data = balance[cpte]
        print(f"{cpte:<7} | {data['intitule'][:28]:<28} | {data['total_debit']:<12,.0f} | {data['total_credit']:<12,.0f} | {data['solde_debit']:<11,.0f} | {data['solde_credit']:<11,.0f}")
        
        tot_mvt_deb += data['total_debit']
        tot_mvt_crd += data['total_credit']
        tot_sld_deb += data['solde_debit']
        tot_sld_crd += data['solde_credit']
        
    separateur("=", 100)
    print(f"{'TOTAL GÉNÉRAL':<37} | {tot_mvt_deb:<12,.0f} | {tot_mvt_crd:<12,.0f} | {tot_sld_deb:<11,.0f} | {tot_sld_crd:<11,.0f}")
    
    print("\n[Vérification de cohérence technique]")
    if abs(tot_mvt_deb - tot_mvt_crd) < 0.1 and abs(tot_sld_deb - tot_sld_crd) < 0.1:
        print("[✔] Parfait : La balance répond aux critères de symétrie arithmétique.")
    else:
        print("[X] Alerte : Dysfonctionnement ou déséquilibre constaté.")


def UI_compte_resultat():
    afficher_titre("Compte de Résultat (Système Normalisé OHADA)")
    gl = generer_grand_livre()
    
    res_net, total_ch, total_prod = calculer_resultat_net()
    
    print(f"{'RUBRIQUES / COMPTES DE CHARGES':<45} | {'MONTANT (USD)':<25}")
    separateur("-", 75)
    for cpte in sorted(gl.keys()):
        if cpte.startswith('6') or cpte.startswith('81') or cpte.startswith('83') or cpte.startswith('85'):
            solde = gl[cpte]["total_debit"] - gl[cpte]["total_credit"]
            if solde != 0:
                print(f" {cpte} - {PLAN_COMPTABLE_OHADA[cpte][:35]:<35} | {solde:<25,.2f}")
                
    print(f"\n{'RUBRIQUES / COMPTES DE PRODUITS':<45} | {'MONTANT (USD)':<25}")
    separateur("-", 75)
    for cpte in sorted(gl.keys()):
        if cpte.startswith('7') or cpte.startswith('82') or cpte.startswith('84'):
            solde = gl[cpte]["total_credit"] - gl[cpte]["total_debit"]
            if solde != 0:
                print(f" {cpte} - {PLAN_COMPTABLE_OHADA[cpte][:35]:<35} | {solde:<25,.2f}")
                
    separateur("=", 75)
    print(f"{'TOTAL DES CHARGES ORDINAIRES ET HAO':<45} | {total_ch:<25,.2f}")
    print(f"{'TOTAL DES PRODUITS ORDINAIRES ET HAO':<45} | {total_prod:<25,.2f}")
    separateur("=", 75)
    
    if res_net >= 0:
        print(f"{'RÉSULTAT NET COMPTABLE (BÉNÉFICE)':<45} | {res_net:<25,.2f}")
    else:
        print(f"{'RÉSULTAT NET COMPTABLE (PERTE)':<45} | {abs(res_net):<25,.2f}")
    separateur("=", 75)


def UI_bilan_comptable():
    afficher_titre("Bilan Comptable Normalisé (Actif & Passif)")
    balance = generer_balance()
    res_net, _, _ = calculer_resultat_net()
    
    actif_immobilise = 0.0
    actif_circulant = 0.0
    tresorerie_actif = 0.0
    
    capitaux_propres = 0.0
    dettes_financieres = 0.0
    passif_circulant = 0.0
    tresorerie_passif = 0.0

    for cpte, data in balance.items():
        solde = data["solde_debit"] - data["solde_credit"]
        
        if cpte.startswith('2'): 
            actif_immobilise += solde
        elif cpte.startswith('3') or cpte.startswith('41') or cpte.startswith('46') or cpte.startswith('47'): 
            actif_circulant += solde
        elif cpte.startswith('5') and solde >= 0: 
            tresorerie_actif += solde
        elif cpte.startswith('10') or cpte.startswith('11') or cpte.startswith('14'): 
            capitaux_propres += (-solde)
        elif cpte.startswith('12'): 
            dettes_financieres += (-solde)
        elif cpte.startswith('40') or cpte.startswith('42') or cpte.startswith('43') or cpte.startswith('44'): 
            passif_circulant += (-solde)
        elif cpte.startswith('5') and solde < 0: 
            tresorerie_passif += abs(solde)

    # Transfert dynamique du résultat comptable vers le passif interne
    capitaux_propres += res_net
    total_actif = actif_immobilise + actif_circulant + tresorerie_actif
    total_passif = capitaux_propres + dettes_financieres + passif_circulant + tresorerie_passif

    print(f" {'ACTIF':<36} | {'PASSIF':<37}")
    print(f" {'Rubrique':<25} | {'Montant':<8} | {'Rubrique':<25} | {'Montant':<8}")
    separateur("-", 80)
    
    print(f" {'ACTIF IMMOBILISÉ':<25} | {actif_immobilise:<8,.0f} | {'CAPITAUX PROPRES*':<25} | {capitaux_propres:<8,.0f}")
    print(f" {'ACTIF CIRCULANT':<25} | {actif_circulant:<8,.0f} | {'DETTES FINANCIÈRES':<25} | {dettes_financieres:<8,.0f}")
    print(f" {'TRÉSORERIE ACTIF':<25} | {tresorerie_actif:<8,.0f} | {'PASSIF CIRCULANT':<25} | {passif_circulant:<8,.0f}")
    print(f" {'':<25} | {'':<8} | {'TRÉSORERIE PASSIF':<25} | {tresorerie_passif:<8,.0f}")
    
    separateur("=", 80)
    print(f" {'TOTAL ACTIF':<25} | {total_actif:<8,.0f} | {'TOTAL PASSIF':<25} | {total_passif:<8,.0f}")
    separateur("=", 80)
    print("(*) Intègre l'état de résultat courant calculé dynamiquement.")
    
    if abs(total_actif - total_passif) < 1.0:
        print("[✔] ÉQUILIBRE PATRIMONIAL CONSTATÉ.")
    else:
        print(f"[X] ERREUR : Écart de structure détecté : {abs(total_actif - total_passif):,.2f}")


def UI_gerer_plan_comptable():
    afficher_titre("Gestion du Plan Comptable OHADA")
    print(" 1. Lister tous les comptes configurés")
    print(" 2. Ajouter un nouveau compte manuel")
    choix = input("Votre option : ").strip()
    
    if choix == "1":
        separateur("-", 60)
        for num, intitule in sorted(PLAN_COMPTABLE_OHADA.items()):
            print(f" Compte N° {num:<8} : {intitule}")
    elif choix == "2":
        num = input("Entrez le numéro du nouveau compte (ex: 245100) : ").strip()
        if not num.isdigit() or len(num) < 3:
            print("[-] Erreur : Format de compte invalide (chiffres requis).")
            return
        if num in PLAN_COMPTABLE_OHADA:
            print("[-] Erreur : Ce compte existe déjà au catalogue.")
            return
        intitule = input("Entrez l'intitulé officiel : ").strip()
        if not intitule:
            print("[-] Erreur : L'intitulé ne peut être vide.")
            return
        PLAN_COMPTABLE_OHADA[num] = intitule
        print(f"[+] Le compte {num} a été greffé au plan général.")


def UI_aide_ohada():
    afficher_titre("Aide & Cadre Conceptuel du Droit Comptable OHADA")
    print("""
    Le Système Comptable OHADA (SYSCOHADA) harmonise les pratiques comptables 
    dans l'espace unifié des économies africaines signataires.
    
    Règles d'or implémentées au sein du moteur de l'application :
    1. PARTIE DOUBLE : Les débits équilibrent obligatoirement les crédits.
    2. TYPOLOGIE DES CLASSES STRUCTURÉES :
       - Classe 1 à 5 : Comptes de Bilan (Patrimoine global)
       - Classe 6 et 7 : Comptes de Gestion (Performance de l'exercice financier)
       - Classe 8 : Éléments exceptionnels Hors Activités Ordinaires (HAO)
    """)


# =====================================================================
# 6. EXTENSIONS POUR L'AUDIT ET LES RATIOS FINANCIERS
# =====================================================================

def UI_audit_comptable():
    afficher_titre("Module d'Audit Révisé de Conformité")
    print("[*] Lancement des scripts d'analyse des anomalies métiers...")
    
    erreurs = 0
    gl = generer_grand_livre()
    
    caisse = gl.get("571100", {"total_debit": 0, "total_credit": 0})
    solde_caisse = caisse["total_debit"] - caisse["total_credit"]
    if solde_caisse < 0:
        print("[ALERTE] Le compte Caisse (571100) affiche un solde créditeur ! Interdit en droit comptable.")
        erreurs += 1
        
    cap = gl.get("101000", {"total_debit": 0, "total_credit": 0})
    if cap["total_debit"] == 0 and cap["total_credit"] == 0:
        print("[AVERTISSEMENT] Le capital social (101000) est à zéro. Structure non capitalisée.")
        erreurs += 1
        
    if erreurs == 0:
        print("[✔] RAS : Vos livres de comptes respectent les règles de cohérence de base.")
    else:
        print(f"[X] Audit achevé : {erreurs} point(s) de vigilance à régulariser.")


def UI_visualiser_statistiques():
    afficher_titre("Ratios de Structure et Indicateurs de Rentabilité")
    res, charges, produits = calculer_resultat_net()
    
    if produits > 0:
        marge_nette = (res / produits) * 100
        print(f" Marge de Rentabilité Nette        : {marge_nette:.2f} %")
    else:
        print(" Marge de Rentabilité Nette        : Indéterminable (Chiffre d'affaires nul)")
        
    print(f" Consommations de l'exercice (6/8) : {charges:,.2f} USD")
    print(f" Revenus de l'exercice (7/8)       : {produits:,.2f} USD")


def afficher_sous_menu_analyses():
    while True:
        print("\n" + " - " * 15)
        print(" ANALYSES COMPTABLES AVANCÉES ".center(45, " "))
        print(" - " * 15)
        print(" A. Lancer l'Audit de conformité des comptes")
        print(" B. Visualiser les Ratios de Performance")
        print(" C. Consulter le Cadre Conceptuel Théorique")
        print(" R. Retour au menu principal")
        choix = input("Sélectionnez (A/B/C/R) : ").strip().upper()
        
        if choix == "A":
            UI_audit_comptable()
        elif choix == "B":
            UI_visualiser_statistiques()
        elif choix == "C":
            UI_aide_ohada()
        elif choix == "R":
            break
        else:
            print("[-] Choix invalide. Saisissez A, B, C ou R.")


# =====================================================================
# 7. MODULE D'EXPORTATION TEXTE ( PERSISTANCE SANS SQL )
# =====================================================================

def exporter_etats_financiers():
    afficher_titre("Exportation Textuelle de la Liasse Financière")
    filename = "liasse_financiere_ohada.txt"
    balance = generer_balance()
    res_net, charges, produits = calculer_resultat_net()
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("========================================================\n")
            f.write("        LIASSE DES ÉTATS FINANCIERS REVISÉS (OHADA)     \n")
            f.write(f"        Éditée le : {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write("========================================================\n\n")
            
            f.write("--- BALANCE DES COMPTES ---\n")
            for cpte in sorted(balance.keys()):
                d = balance[cpte]
                f.write(f"Compte {cpte:<7} | {d['intitule'][:25]:<25} | Solde Deb: {d['solde_debit']:12,.0f} | Solde Crd: {d['solde_credit']:12,.0f}\n")
                
            f.write("\n--- ANALYSE DE GESTION ---\n")
            f.write(f"Volume des Charges  : {charges:,.2f} USD\n")
            f.write(f"Volume des Produits : {produits:,.2f} USD\n")
            f.write(f"RÉSULTAT DU CODE FINANCIER : {res_net:,.2f} USD\n")
            
        print(f"[✔] Rapport exporté avec succès sous la référence : '{os.path.abspath(filename)}'")
    except Exception as e:
        print(f"[X] Échec d'écriture sur le disque local : {str(e)}")


# =====================================================================
# 8. POINT D'ENTRÉE ET LOGIQUE DE CONTRÔLE PRINCIPALE
# =====================================================================

def execute_app():
    """Initialise le programme et pilote la boucle de saisie principale."""
    
    # -----------------------------------------------------------------
    # LIGNE CRUCIALE : Commentée pour garantir une application vierge au lancement.
    # Si vous désirez injecter des écritures d'exemples, décommentez la ligne ci-dessous.
    # -----------------------------------------------------------------
    # charger_donnees_initiales()
    
    while True:
        menu_principal()
        choix = input("Sélectionnez votre action (0-9) : ").strip()
        
        if choix == "1":
            UI_saisie_ecriture()
        elif choix == "2":
            UI_afficher_journal()
        elif choix == "3":
            UI_consulter_grand_livre()
        elif choix == "4":
            UI_generer_balance()
        elif choix == "5":
            UI_compte_resultat()
        elif choix == "6":
            UI_bilan_comptable()
        elif choix == "7":
            UI_gerer_plan_comptable()
        elif choix == "8":
            afficher_sous_menu_analyses()
        elif choix == "9":
            exporter_etats_financiers()
        elif choix == "0":
            print("\n[✔] Fermeture de l'application comptable. Données en mémoire libérées. Au revoir !")
            sys.exit(0)
        else:
            print("[-] Option erronée. Saisissez une valeur comprise entre 0 et 9.")
            
        input("\n[Action Terminée] Appuyez sur Entrée pour retourner au menu principal...")


if __name__ == "__main__":
    execute_app()