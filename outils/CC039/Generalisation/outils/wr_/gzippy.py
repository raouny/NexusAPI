#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

#****************************    Fiche signaletique shell  encodage: iso-8859-15    ****************************************    #
# Nom du programme : gzippy.py    But du programme : Gzip     Version minimum de l'interpreteur python : 2.4
#***********************************************    Syntaxe    **************************************************************   #
#                       gzippy.py -i file
#**********************************************    Historique    *************************************************************  #
# Version       Date            AUTEUR          ENTREPRISE      Commentaires
# 1.0          02/09/2011       J.TARRASSON        ProximIT        Creation
# 1.1          18/10/2011       C CHAPUT           La Poste        Bouchons linux /unix
# 2.0          15/06/2012       Y HERVE            La Poste        Re-ecriture du script sans gzip.exe + option force
#                                                                  + gestion multi-fichiers + mode decompression + modif mode Bouchon
#**********************************************    Codes retour    ***********************************************************  #
# code 0: Normal - Code retour normal : L enchainement est poursuivi
# code 1: Warning - Detection d une anomalie : L enchainement peut etre poursuivi
# code 2: Warning - Detection d une anomalie : L enchainement peut etre poursuivi
# code 3: Critique - Erreur Critique
#*****************************************************************************************************************************  #

# Import des modules python
import os
import sys
#import platform
import getopt
#import re
import gzip
import os.path
import glob
#import string
#import subprocess
#import zlib

# Definition des variables systeme
__SYSTEM = sys.platform
__PYTHON_VERSION = sys.version


# Definition des variables

vg_file_gzip = None
vg_decompress = None
vg_force_mode = False
vg_verbeux = False # Mode Verbeux permet un debuggage plus precis / l option -v n affiche pas les parametres en entree
vg_compress = 9 # taux de compression max, plus lent en temps de calcul
vg_preserve = False

# Variables globales des code retour
vg_bl=3
vg_wg=1


# Version du CC a completer
version = "gzippy.py v2.0 - python "+__PYTHON_VERSION+" - "+__SYSTEM

#*****************************************************************************************************************************  #
# Definitions des fonctions locales
#*****************************************************************************************************************************  #

#*****************************************************************************************************************************  #
# Fonction de test de presence de l argument obligatoire
#*****************************************************************************************************************************  #
def p_test_options():
        p_debugg("Test des arguments passes en entree du script ... ")
        if (( vg_file_gzip ) == None):
            print "*** au moins un argument est manquant ***"
            f_printusage(vg_bl)
        p_debugg("Les parametres obligatoires sont renseignes")


#*****************************************************************************************************************************  #
# Fonction d'aide a l utilisation du script
#*****************************************************************************************************************************  #

def f_printusage(err):
#   Affiche le message d utilisation du script
    print r"""
    gzippy.py <nom du fichier avec son chemin absolu>
              -->> possibilté de gerer une liste de fichier ccyyaaaa.*

            parametres optionnels :
                [-d ou --decompress]    : decompression du .gz place en argument
                [--force]               : ecrase le fichier .gz si deja present
                [--preserve]            : ne supprime pas le fichier source
                [--taux=]               : taux de compression par de 1 a 9.
                                          valeur par default = 9
                [-B ou --bouchon=]      : mode bouchon utilise par le CCO
                [--help]                : affiche l'aide
                [--debugg]              : mode "verbeux" debugg

            Sous UNIX / Linux le caractere * doit etre remplace par \*
    """
    p_print_error("",err)


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

    global vg_file_gzip
    global vg_decompress
    global vg_verbeux  # utiliser pour le debuggage
    global vg_force_mode
    global vg_compress
    global vg_preserve

    p_debugg("ligne de commande : "+ str(sys.argv) )

    #recuperation des arguments
    if len(sys.argv) == 1 :
        print "Parametres manquants"
        f_printusage(vg_bl)

    vg_file_gzip = sys.argv[1]
    p_debugg("nom du fichier en entree : "+ str(vg_file_gzip) )

    try:
        opts, args = getopt.getopt(sys.argv[2:], "dB:", ["decompress","force","help","bouchon=","debugg","taux=","preserve"])

    except getopt.GetoptError, err:
        # print help information and exit:
        # will print something like "option -z not recognized"
        print "!!! ERREUR !!! l option n est pas reconnue : ", str(err)
        f_printusage(vg_bl)

    #test des arguments et enrichissement des variables
    for o, a in opts:
        p_debugg(str(o) +" , " + str(a))
        if o in ("-h", "--help"):
            f_printusage(0)
        elif o == ("--taux"):
            vg_compress = int(a)
            p_debugg("taux de compression : " + str(vg_compress))
        elif o == ("--preserve"):
            vg_preserve = True
            p_debugg("mode preserve actif")
        elif o in ("-d", "--decompress"):
            vg_decompress = True
            p_debugg("mode decompress actif")
        elif o == ("--force"):
            vg_force_mode = True
            p_debugg("mode force actif")
        elif o in ("-B", "--bouchon"):
            p_print_error("mode bouchon",int(a))
        elif o == ("--debugg"):
            vg_verbeux = True
            p_debugg("mode verbeux actif")
        else:
            assert False, "option invalide !!!"

    # test de presence des options obligatoires
    p_test_options()

    return True

def p_debugg(chaine):
    if vg_verbeux : print str(chaine)


def f_valorisation_var_system(chemin):
    # permet de valoriser des $ sous unix ou % sous windows
    if chemin != None :
        resultat = os.path.expandvars(chemin)
        p_debugg("Resultat de la valorisation " + str(resultat))
    return resultat

def p_gzip(fichier_gziper_in,fichier_gziper_out):
    p_debugg("Debut de la fonction p_gzip")
    try :
        f_in = open(fichier_gziper_in, 'rb',1)
        f_out = gzip.open(fichier_gziper_out, 'wb', compresslevel=vg_compress)
        f_out.writelines(f_in)
        f_out.close()
        f_in.close()
        print "Fichier traité :", fichier_gziper_in
    except OSError , (errno,strerror):
        print "OSerror (", str(errno), ") : ",str(strerror)
        p_print_error ("", vg_bl)
    except IOError , (errno,strerror):
        print "IOerror (", str(errno), ") : ",str(strerror)
        p_print_error ("", vg_bl)
    except :
        p_print_error ("Erreur inconnue - sortie en code retour", vg_bl)

def p_gunzip(fichier_gziper_in,fichier_nogzip_out):
    p_debugg("Debut de la fonction p_gunzip")

    try :
        f_in = gzip.GzipFile(fichier_gziper_in, 'rb');
        f_out = open(fichier_nogzip_out, "wb")
        f_out.write(f_in.read())
        f_in.close()
        f_out.close()
        print "Fichier traité :", fichier_gziper_in

    except OSError , (errno,strerror):
        print "OSerror (", str(errno), ") : ",str(strerror)
        p_print_error ("", vg_bl)
    except IOError :
        print "IOerror : anomalie dans le ficher gz"
        p_print_error ("", vg_bl)
    except :
        p_print_error ("Erreur inconnue - sortie en code retour", vg_bl)

def p_supp_fic(le_fichier):
    try :
        os.remove(le_fichier)
    except OSError , (errno,strerror):
        print "OS error (", str(errno), ") : ",str(strerror)
        p_print_error ("Erreur lors de la suppression du fichier", vg_bl)


#*****************************************************************************************************************************  #
# definition des fonctions par system d exploitation
#*****************************************************************************************************************************  #

def f_compression_file(fichier_in):
    print "Debut de la fonction de gzip du fichier"

    # valorise les variables system
    nom_absolu_fichier_entree = f_valorisation_var_system(fichier_in)

    print "Le fichier a modifier est le suivant :", nom_absolu_fichier_entree

    #Test la presence du fichier a gzipper
    if os.path.isfile(nom_absolu_fichier_entree) == False :
        p_print_error("Le fichier : " + nom_absolu_fichier_entree + " n existe pas",vg_wg)


    p_debugg("Debut de la fonction de compression gzip du fichier en entree")

    # Ecrase le fichier .gz si option --force presente
    nom_absolu_fichier_sortie=nom_absolu_fichier_entree + '.gz'
    if vg_force_mode == True :
        if os.path.isfile(nom_absolu_fichier_sortie) == False :
            p_gzip(nom_absolu_fichier_entree,nom_absolu_fichier_sortie)
        else :
            p_supp_fic(nom_absolu_fichier_sortie)
            p_gzip (nom_absolu_fichier_entree,nom_absolu_fichier_sortie)
    else :
        if os.path.isfile(nom_absolu_fichier_sortie) == False :
            p_gzip (nom_absolu_fichier_entree,nom_absolu_fichier_sortie)
        else :
            p_print_error ("le fichier de sortie existe deja", vg_bl)

    p_debugg("Compression terminee")
    if vg_preserve == False :
        p_supp_fic(nom_absolu_fichier_entree)
    return 0

def f_decompression_file(fichier_in):

    nom_absolu_fichier_entree = f_valorisation_var_system(fichier_in)
    nom_absolu_fichier_sortie = '.'.join(nom_absolu_fichier_entree.split('.')[:-1])
    # Ecrase le fichier .gz si option --force presente
    if vg_force_mode == True :
        if os.path.isfile(nom_absolu_fichier_sortie) == False :
            p_gunzip(nom_absolu_fichier_entree,nom_absolu_fichier_sortie)
        else :
            p_supp_fic(nom_absolu_fichier_sortie)
            p_gunzip (nom_absolu_fichier_entree,nom_absolu_fichier_sortie)
    else :
        if os.path.isfile(nom_absolu_fichier_sortie) == False :
            p_gunzip (nom_absolu_fichier_entree,nom_absolu_fichier_sortie)
        else :
            p_print_error ("le fichier de sortie existe deja", vg_bl)

    if vg_preserve == False :
        p_supp_fic(nom_absolu_fichier_entree)
    return 0


def lancement():
    code_retour = 56
    if ( f_param_lg_commande() != True):
            p_print_error("sortie du programme en CR 3",vg_bl)
    if vg_decompress == True :
        print "Mode decompression active"
        list = glob.glob(vg_file_gzip)
        if list == [] :
            p_print_error("Pas de fichier en entree",vg_wg)
        for fichier in glob.glob(vg_file_gzip):
            code_retour = f_decompression_file(fichier)
    else :
        print "Mode compression active"
        list = glob.glob(vg_file_gzip)
        if list == [] :
            p_print_error("Pas de fichier en entree",vg_wg)
        for fichier in list:
            code_retour = f_compression_file(fichier)
    return code_retour

#*****************************************************************************************************************************  #
# Main
#*****************************************************************************************************************************  #
if __name__ == "__main__":
    # Variables du programme principal

    #Variable code_retour
    #Elle est positionnee avec un code retour different de 0 afin que la fonction modifie sa valeur
    code_retour = 56

    # Affiche la version
    print version + "\n"


    #*****************************************************************************************************************************  #
    # Lancement de la commande selon la plateforme utilisee
    #*****************************************************************************************************************************  #

    if __SYSTEM == "win32":
        code_retour = lancement()
    elif __SYSTEM == "hp-ux11":
        code_retour = lancement()
    elif __SYSTEM == "linux2":
        code_retour = lancement()
    else:
        print "Plateforme inconnue - sortie en CR 3"
        print_error(vg_bl)


    #######################################
    # Verification du code retour         #
    #######################################
    if code_retour not in (0,1, None):
            p_print_error ("Erreur inattendue - sortie en CR :", vg_bl)

    #######################################
    # Fin du Programme avec code_retour   #
    #######################################
    p_print_error ("Fin du programme", code_retour)

