#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

#****************************    Fiche signaletique shell  encodage: iso-8859-15    ****************************************    #
# Nom du programme : dos2unix.py    But du programme : Convertir  un fichier texte DOS en UNIX
# Version minimum de l'interpreteur python : 2.4
#***********************************************    Syntaxe    **************************************************************   #
#                      dos2unix.py -s param1
#**********************************************    Historique    *************************************************************  #
# Version       Date            AUTEUR          ENTREPRISE      Commentaires
# 1.0           18/10/2011      CCO             ATOS            Creation
# 1.1           20/10/2011      C CHAPUT        La Poste        Correction gestion des erreurs et des os, ajout option "-a"
#                                                               Encapsulation des commandes system pour unix et sles
# 1.2           20/04/2015      R. SAVIGNY      La Poste        Portage multi-OS, ajout option reverse "-r" unix2dos
#**********************************************    Codes retour    ***********************************************************  #
# code 0: Normal - Code retour normal : L enchainement est poursuivi
# code 1: Warning - Detection d une anomalie : L enchainement peut etre poursuivi
# code 2: Erreur - Erreur Non bloquante : possibilite de lancer une procedure de reprise
# code 3: Critique - Erreur Critique
# code > 3 : Traitement en erreur avec un code retour particulier
#*****************************************************************************************************************************  #

# Import des modules python


import os
import sys
import platform
import getopt
import re
import os.path
import glob
import string
import datetime

# Import des modules clients ou fonctions globales

# Variables globales
vg_cas_fichier_absent=False # est utilisee pour gerer le code retour en cas d absence de fichier
vg_reverse=False # mode reverse => unix2dos


# Mode Bouchon : False ou True
BOUCHON = False
code_retour_bouchon = 5 # Code retour dans le cas de l'utilisation du mode bouchon
# Fin du parametrage du mode bouchon

# Definition des variables systeme
__SYSTEM = sys.platform
__PYTHON_VERSION = sys.version

# Version du CC a completer
version = "dos2unix.py v1.2 - python "+__PYTHON_VERSION+" - "+__SYSTEM

#*****************************************************************************************************************************  #
# Definitions des fonctions locales
#*****************************************************************************************************************************  #

def test_options(arguments):
        " Tests des arguments du script "

        if (arguments == []) or (arguments is None) :
                print "*** un argument est manquant ***"
                printusage(3)


def printusage(err):

    print r"""
   dos2unix.py : Transforme un fichier dos en fichier unix ou inversement (option -r).

   Usage de la commande :
   dos2unix.py [-a] [-r] -s <chemin>
   dos2unix.py [-h|--help]

   Les parametres suivants sont obligatoires :

    -s <chemin>     : chemin du fichier a convertir

    options :
    -a              : code retour a 0 quand fichier absent sinon 3 par defaut
    -r              : mode reverse, transforme un fichier unix en fichier dos
    -h              : affichage de l aide
    """

    sys.exit(err)


def repl_backshlashs():
        " Remplace les \ des chemins Windows par des \\ lisibles par python "

	global example

        if example != None: example = example.replace("\\","\\\\")

def timestamp_name():
    # retourne un timestamp au format chaine de caractere
    today = datetime.datetime.now()
    return str(today.strftime("%Y%m%d%H%M%S"))

#*****************************************************************************************************************************  #
# definition des fonctions par system d exploitation
#*****************************************************************************************************************************  #

def lancement_windows(params):
    global vg_cas_fichier_absent
    global vg_reverse

    if vg_reverse == True :
        message = "Debut de la conversion Unix vers Dos"
    else :
        message = "Debut de la conversion Dos vers Unix"

    print message
    # valorise les variables system
    nom_absolu_fichier = os.path.expandvars(params)
    print "Nom du fichier : " + nom_absolu_fichier

    #Test la presence du fichier a convertir
    if os.path.isfile(nom_absolu_fichier) == False :
        print "Le fichier : " + str(nom_absolu_fichier) + " n existe pas"
        if vg_cas_fichier_absent == True :
            print "Sortie en code retour 0 - option -a active"
            sys.exit(0)
        else :
            print "Sotie en code retour 3"
            sys.exit(3)
    else :
        try :
            nom_absolu_fichier_tempo = nom_absolu_fichier + timestamp_name()
            print "Creation du fichier temporaire : ", nom_absolu_fichier_tempo
            fichier1= open(nom_absolu_fichier, 'U')
            # Creation d'un fichier temporaire dans lequel resultera la conversion
            fichier2= open(nom_absolu_fichier_tempo  , 'wb')
            if vg_reverse == True :
                fichier2.write(fichier1.read().replace("\n","\r\n"))
            else :
                fichier2.write(fichier1.read().replace("\r\n","\n"))
            fichier1.close()
            fichier2.close()
            os.remove(nom_absolu_fichier)
            os.rename(nom_absolu_fichier_tempo, nom_absolu_fichier)

        except IOError , (errno,strerror):
            print "I/O error (", str(errno), ") : ",str(strerror)
            print "Sortie en code retour 3"
            sys.exit(3)
        except OSError , (errno,strerror):
            print "OS error (", str(errno), ") : ",str(strerror)
            print "Sortie en code retour 3"
            sys.exit(3)
        except :
            print "Erreur inconnue - sortie en code retour 3"
            sys.exit(3)

    print "Fin du dos2unix."
    return 0

def lancement_hpux(params):
    lancement_windows(params)

def lancement_linux(params):
    lancement_windows(params)

def lancement_solaris(params):
    print "System non pris en charge"
    sys.exit(3)
    return 0

#*****************************************************************************************************************************  #
# Main
#*****************************************************************************************************************************  #
if BOUCHON == True :
    __name__ = "Bouchon"

if __name__ == "__main__":
    # Variables du programme principal

    #Variable code_retour
    #Ele est posiionnee avec un code retour different de 0 afin que la fonction modifie sa valeur
    code_retour = 56


    # Affiche la version
    print version + "\n"


    # Gestion des arguments en parametre
    # ++++++++++++++++++++++++++++++++++
    f_source = ""

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:ar", ["help"])

    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        printusage(3)

    for o, a in opts:
        if o in ("-h", "--help"):
            printusage(3)
        elif o in ("-s"):
            f_source = a
        elif o in ("-a"):
            # cas du fichier absent mais sortie en code retour 0
            vg_cas_fichier_absent = True
        elif o in ("-r"):
            # cas du fichier absent mais sortie en code retour 0
            vg_reverse = True
        else:
            assert False, "option invalide"

    # affiche un message d erreur en cas de params incorrects
    test_options(sys.argv[1:])

    # ++++++++++++++++++++++++++++++++++

    #*****************************************************************************************************************************  #
    # Lancement de la commande selon la plateforme utilisee
    #*****************************************************************************************************************************  #

    if __SYSTEM == "win32":
            code_retour = lancement_windows(f_source)
    elif __SYSTEM == "hp-ux11":
            code_retour = lancement_hpux(f_source)
    elif __SYSTEM == "linux2":
            code_retour = lancement_linux(f_source)
    elif __SYSTEM == "solaris":
            code_retour = lancement_solaris(f_source)
    else:
            print "Plateforme inconnue - sortie en CR 3"
            sys.exit(3)


    #######################################
    # Verification du code retour         #
    #######################################
    if code_retour not in (0, None):
            print "Erreur inattendue - sortie en CR 3"
            sys.exit(3)

    #######################################
    # Fin du Programme avec code_retour   #
    #######################################
    print "Fin du programme - code retour : " + str(code_retour)
    sys.exit(code_retour)

else:
    print "Mode bouchon - codre retour : " + str(code_retour_bouchon)
    sys.exit(code_retour_bouchon)
