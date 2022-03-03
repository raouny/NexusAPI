#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

#****************************    Fiche signaletique shell  encodage: iso-8859-15    ****************************************    #
# Nom du programme : ficmodif.py    But du programme : substituer des caractères dans un fichier
# Version minimum de l'interpreteur python : 2.4
#***********************************************    Syntaxe    **************************************************************   #
#                      ficmodif.py -i <fichier_entree> -c <caractere_entree> -s <caractere_sortie> [-o <fichier_sortie>]
#**********************************************    Historique    *************************************************************  #
# Version       Date            AUTEUR          ENTREPRISE      Commentaires
# 1.0           18/10/2011      Y.HERVE             GER            Creation
#
#**********************************************    Codes retour    ***********************************************************  #
# code 0: Normal - Code retour normal : L enchainement est poursuivi
# code 1: Warning - Detection d une anomalie : L enchainement peut etre poursuivi
# code 3: Critique - Erreur Critique
# code > 3 : Traitement en erreur avec un code retour particulier
#*****************************************************************************************************************************  #

# Import des modules python

import os
import sys
#import platform
import getopt
#import re
import os.path
#import glob
#import string
import datetime

# Variables globales
vg_input_file=None
vg_car_in=None
vg_car_out=None
vg_output_file=None
vg_verbeux=False # Mode Verbeux permet un debuggage plus precis / l option -v n affiche pas les parametres en entree
vg_bl=3
vg_wg=1

# Definition des variables systeme
__SYSTEM = sys.platform
__PYTHON_VERSION = sys.version

# Version du CC a completer
version = "ficmodif.py v1.0 - python "+__PYTHON_VERSION+" - "+__SYSTEM

#*****************************************************************************************************************************  #
# Definitions des fonctions locales
#*****************************************************************************************************************************  #

#*****************************************************************************************************************************  #
# Fonction de test de présence des arguments obligatoires
#*****************************************************************************************************************************  #
def p_test_options():
        print "Test des arguments passes en entree du script ... "

        if (( vg_input_file and vg_car_in and vg_car_out ) == None):
            print "*** un argument est manquant ***"
            f_printusage(3)
        if vg_verbeux :  print ("Les parametres obligatoires sont renseignes")


#*****************************************************************************************************************************  #
# Fonction d'aide à l'utilisation du script
#*****************************************************************************************************************************  #

def f_printusage(err):
#   Affiche le message d utilisation du script
    print r"""
    ficmodif.py -i <chemin/fichier_entree> -c <caractere_entree> -s <caractere_sortie> [-o <chemin/fichier_sortie>]

    Les parametres suivants sont obligatoires :

    -i <fichier_entree>     : fichier a modifier avec son chemin
    -c <caractere_entree>   : caractere a remplacer
    -s <caractere_sortie>   : nouveau caractere de substitution

    Le parametre suivant est facultatif :

    -o <fichier_sortie>     : fichier modifie en sortie avec son chemin, si absent ecrase le fichier en entree

    Sous UNIX / Linux les caracteres speciaux doivent etre precedes par un \

    options :
    -v              : mode verbeux
    -h              : affichage de l aide
    --help          : affichage de l aide
    """
    sys.exit(err)


#*****************************************************************************************************************************  #
# Fonction de gestion des erreurs
#*****************************************************************************************************************************  #

def p_print_error(mesg, num):
    # retourne le message d erreur et sort en fonction du code retour
    print mesg
    print "Sortie en code retour " + str(num)
    sys.exit(num)
    

#*****************************************************************************************************************************  #
# Fonction de gestion des arguments passes en parametre de la ligne de commandes
#*****************************************************************************************************************************  #

def f_param_lg_commande():
    
    global vg_input_file
    global vg_output_file
    global vg_car_in
    global vg_car_out
    global vg_verbeux  # utiliser pour le debuggage

    ind_i = ind_c = ind_s = ind_o = 0

    #recuperation des arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:c:s:o:vB:h", ["help","bouchon="])
        
    except getopt.GetoptError, err:
        # print help information and exit:
        # will print something like "option -z not recognized"
        p_print_error ("!!! ERREUR !!! l option n est pas reconnue : ", str(err))
        f_printusage(3)

    #test des arguments et enrichissement des variables
    for o, a in opts:
        if vg_verbeux : print o, a
        if o in ("-h", "--help"):
            f_printusage(0)
        elif o in ("-v"):
            vg_verbeux = True
            if vg_verbeux : print "mode verbeux actif"
        elif o in ("-i"):
            if ind_i >= 1 :
                p_print_error ("Parametre -i en double ...", vg_bl)
            vg_input_file = a
            if vg_verbeux : print "nom du fichier en entree : " + str(vg_input_file)
            ind_i +=1
        elif o in ("-c"):
            if ind_c >= 1 :
                p_print_error ("Parametre -c en double ...", vg_bl)
            vg_car_in = a
            if vg_verbeux : print "Caractère a remplacer : " + str(vg_car_in)
            ind_c +=1
        elif o in ("-s"):
            if ind_s >= 1 :
                p_print_error ("Parametre -s en double ...", vg_bl)
            vg_car_out = a
            if vg_verbeux : print "Caractère de substitution : " + str(vg_car_out)
            ind_s +=1
        elif o in ("-o"):
            if ind_o >= 1 :
                p_print_error ("Parametre -o en double ...", vg_bl)
            vg_output_file = a
            if vg_verbeux : print "nom du fichier en sortie : " + str(vg_output_file)
            ind_o +=1
        elif o in ("-B", "--bouchon"):
            p_print_error("mode bouchon",int(a))
        else:
            assert False, "option invalide !!!"
    # test de présence des options obligatoires
    p_test_options()

    return True

def p_debugg(chaine):
    if vg_verbeux : print str(chaine)


def f_timestamp_name():
    # retourne un timestamp au format chaine de caractere
    today = datetime.datetime.now()
    return str(today.strftime("%Y%m%d%H%M%S"))

def f_valorisation_var_system(chemin):
    # permet de valoriser des $ sous unix ou % sous windows
    if chemin != None :
        resultat = os.path.expandvars(chemin)
        p_debugg("Resultat de la valorisation " + str(resultat))
        return resultat


#*****************************************************************************************************************************  #
# fonction de substitution de caractère(s) dans un fichier
#*****************************************************************************************************************************  #

def f_substitute_char():
    print "Debut de la fonction substitution de caractere ou chaine de caracteres"

    # valorise les variables system
    nom_absolu_fichier = f_valorisation_var_system(vg_input_file)
    nom_absolu_fichier_sortie = f_valorisation_var_system(vg_output_file)

    print "le fichier a modifier est le suivant :", nom_absolu_fichier

    if vg_output_file != None :
        if vg_verbeux : print "le fichier integrant les modifications est le suivant :", nom_absolu_fichier_sortie

    #Test la presence du fichier a convertir
    if os.path.isfile(nom_absolu_fichier) == False :
        p_print_error("Le fichier : " + str(nom_absolu_fichier) + " n existe pas",vg_bl)
    else :
        try :
            # Creation du fichier temporaire
            nom_absolu_fichier_tempo = nom_absolu_fichier + f_timestamp_name()
            if vg_verbeux : print "Creation du fichier temporaire : ", nom_absolu_fichier_tempo

            # Affiche le nombre d'occurance a remplacer
            fichier1= open(nom_absolu_fichier, 'rb')
            car_count=fichier1.read().count(vg_car_in)
            print "nombre d'occurance(", vg_car_in, ") a substituer dans le fichier =", car_count
            fichier1.close()

            # realise la substitution de caractere
            fichier1= open(nom_absolu_fichier, 'rb')
            fichier2= open(nom_absolu_fichier_tempo  , 'wb')
            for ligne in fichier1.readlines():
                fichier2.write(ligne.replace(vg_car_in,vg_car_out))
                if vg_verbeux : print "Modification effectuee sur la ligne : ", str(ligne)
            fichier1.close()
            fichier2.close()

        except IOError , (errno,strerror):
            print "I/O error (", str(errno), ") : ",str(strerror)
            p_print_error ("Sortie en code retour 3", vg_bl)
        except OSError , (errno,strerror):
            print "OS error (", str(errno), ") : ",str(strerror)
            p_print_error ("Sortie en code retour 3", vg_bl)
        except :
            p_print_error ("Erreur inconnue - sortie en code retour 3", vg_bl)

    if car_count != 0 :
        print "Substitution de caractere effectuee avec succes"
    else :
        print "Pas d'occurance trouvee"
    cr=f_rename_file(nom_absolu_fichier,nom_absolu_fichier_tempo,nom_absolu_fichier_sortie)
    return cr


def f_rename_file(nom_absolu_fichier,nom_absolu_fichier_tempo,nom_absolu_fichier_sortie):
    if vg_verbeux : print "Debut de la fonction de creation et gestion du fichier de sortie"
    try :
        # Ecrase le fichier d'origine si option -o absente
        if vg_output_file == None :
            os.remove(nom_absolu_fichier)
            os.rename(nom_absolu_fichier_tempo, nom_absolu_fichier)
            if vg_verbeux : print "Le fichier resultat est le suivant", nom_absolu_fichier
        # inscrit les modifications demandees dans le fichier stipulé en argument -o
        else :
            if os.path.isfile(nom_absolu_fichier_sortie) == False :
                os.rename(nom_absolu_fichier_tempo, nom_absolu_fichier_sortie)
                if vg_verbeux : print "Le fichier resultat est le suivant", nom_absolu_fichier_sortie
            else :
                p_print_error ("le fichier de sortie existe déjà", vg_bl)
    except OSError , (errno,strerror):
        print "OS error (", str(errno), ") : ",str(strerror)
        p_print_error ("Sortie en code retour 3", vg_bl)
    return 0

#*****************************************************************************************************************************  #
# Main
#*****************************************************************************************************************************  #
if __name__ == "__main__":
    # Variables du programme principal

    #Variable code_retour
    #Ele est posiionnee avec un code retour different de 0 afin que la fonction modifie sa valeur

    code_retour = 56
    
    # Affiche la version
    print version + "\n"

    
    #*****************************************************************************************************************************  #
    # Lancement de la commande selon la plateforme utilisee
    #*****************************************************************************************************************************  #

    if __SYSTEM == "win32":
            if ( f_param_lg_commande() != True):
                p_print_error("sortie du programme en CR 3",vg_bl)
            code_retour = f_substitute_char()
    elif __SYSTEM == "hp-ux11":
            if ( f_param_lg_commande() != True):
                p_print_error("sortie du programme en CR 3",vg_bl)
            code_retour = f_substitute_char()
    elif __SYSTEM == "linux2":
            if ( f_param_lg_commande() != True):
                p_print_error("sortie du programme en CR 3",vg_bl)
            code_retour = f_substitute_char()
    elif __SYSTEM == "solaris":
            if ( f_param_lg_commande() != True):
                p_print_error("sortie du programme en CR 3",vg_bl)
            code_retour = f_substitute_char()
    else:
            print "Plateforme inconnue - sortie en CR 3"
            print_error(3)


    #######################################
    # Verification du code retour         #
    #######################################
    if code_retour not in (0, None):
            p_print_error ("Erreur inattendue - sortie en CR :", vg_bl)
            
    #######################################
    # Fin du Programme avec code_retour   #
    #######################################
    p_print_error ("", code_retour)
    
