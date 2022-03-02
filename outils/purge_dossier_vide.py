#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

#****************************    Fiche signaletique shell  encodage: iso-8859-15    ****************************************    #
# Nom du programme : purge_dossier_vide.py    But du programme : purge d arborescence vide Version minimum de l'interpreteur python : 2.4
#***********************************************    Syntaxe    **************************************************************   #
#                       purge_dossier_vide.py -d param1 [-e param2]
#**********************************************    Historique    *************************************************************  #
# Version       Date            AUTEUR          ENTREPRISE      Commentaires
# 1.0           06/06/2013      C.CHAPUT        La Poste        Creation
# 1.1           02/10/2013      C.CHAPUT        La Poste        Cas d un pb de droits, plusieurs dossiers en input et prise en compte du ,
# 1.2           24/12/2013      C.CHAPUT        La Poste        Correction de l anomalie lors de l'affichage de l aide
# 1.3           16/01/2014      C.CHAPUT        La Poste        Calcul de la retention -t sur le mtime pour linux unix
# 1.4           17/08/2015      R.SAVIGNY       PIXON           I08085391 - corection de la fonction liste d'exclusion (option -e)
#**********************************************    Codes retour    ***********************************************************  #
# code 0: Normal - Code retour normal : L enchainement est poursuivi
# code 1: Warning - Detection d une anomalie : L enchainement peut etre poursuivi
# code 3: Critique - Erreur Critique
# code 3: Exemple d erreur - Erreur parametres incorrects
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
import copy


# Mode Bouchon : False ou True
VG_BOUCHON = False
VG_code_retour_bouchon = 5 # Code retour dans le cas de l'utilisation du mode bouchon
# Fin du parametrage du mode bouchon

# Variable globale
vg_verbeux = False # mode debug
vg_directory = ""
vg_time = 0
vg_exclude = ""
vg_recursif = False
vg_time_creation = False
vg_simu = False
vg_espace_libere = 0
vg_warning_suppression_fichier = 0
vg_warning_liste_fichier = []
vg_chemin_user = ""

# Constantes
vg_bl = 3
vg_wg = 1

# Definition des variables systeme
__SYSTEM = sys.platform
__PYTHON_VERSION = sys.version

# Version du CC a completer
version = "purge_dossier_vide.py v1.4 - python "+__PYTHON_VERSION+" - "+__SYSTEM

#*****************************************************************************************************************************  #
# Definitions des fonctions locales
#*****************************************************************************************************************************  #

def p_test_options(arguments):
        " Tests des arguments du script "

        if arguments is None:
            print "*** un argument est manquant ***"
            p_printusage(vg_bl)
        if vg_directory == "":
            print "*** -d n est pas renseigne ***"
            p_printusage(vg_bl)

        if vg_time == 0 and vg_time_creation == True :
            print ("-c doit etre utilise avec -t")
            p_printusage(vg_bl)


def p_printusage(err):

    p_print_error ( r"""
   purge_dossier_vide.py -d <directory>

   Les parametres suivants sont obligatoires :

       -d <arborescence>
       
   Les paramtres optionnels sont :
   
       [-r]                           : recursif ou non
       [-t <num>]                     : duree de retention en jours des dossiers vide
       [-c]                           : se base sur la date de creation
       [-e <chaine>]                  : "liste exclusions" : utilisation de ";" ou "," pour separer les noms
       [-B <num> | --bouchon=<num>]   : mode bouchon pour le CCO
       [-s]                           : mode simulation ne supprime pas les dossiers
       [-h | --help]                  : affiche l'aide
       [--debug]                      : mode debug

    """ , err)


def p_debugg(chaine):
    # utiliser par le mode debug
    if vg_verbeux : print str(chaine)

def f_dossier_vide(chemin):
    # retourne True si le dossier est vide
    global vg_warning_suppression_fichier
    global vg_warning_liste_fichier
    resultat = False

    try :
        if os.listdir(chemin) == []:
            p_debugg("dossier vide : " + str(chemin))
            resultat = True
    except OSError , (errno,strerror):
        print "ERREUR LORS DE L ACCESS AU DOSSIER ... :", str(chemin)
        print "OS error (", str(errno), ") : ",str(strerror)
        vg_warning_suppression_fichier +=1
        vg_warning_liste_fichier.append(chemin)
    except :
        print "ANOMALIE LORS DE LA SUPPRESSIONS, cause non connue"

    return resultat

def f_valorisation_var_system(chemin): # permet de valoriser des $ sous unix ou % sous windows
    resultat = os.path.expandvars(chemin)
    p_debugg("Resultat de la valorisation " + str(resultat))
    return resultat


def f_listdirectory_unique(path, mode_recursif, char_os):
    dossier=[]

    try :
        os.chdir(os.path.realpath(path+char_os))
    except OSError:
        print ("Erreur lors de l acces au dossier : "+str(os.path.realpath(path+char_os)))
        p_print_error("",vg_bl)
        
    chemin_full = path+char_os+"*"
    l = glob.glob(chemin_full)

    for i in l:
        if os.path.isdir(i):

            if f_dossier_vide(i) == True :
                p_debugg("dossier : " + i + " ajoute")
                dossier.append(i)
            if mode_recursif == True :
                dossier.extend(f_listdirectory_unique(i,mode_recursif, char_os))
    return dossier

def f_listdirectory(path, mode_recursif, char_os):
    resultat = []

    p_debugg("Liste de dossiers a analyser : " + str(path))
    liste_dossier = path.split(",")


    for i in liste_dossier :
        print "Recherche dans le dossier : " + str(i)
        resultat.extend(f_listdirectory_unique(i, mode_recursif, char_os))
#        print resultat

    return resultat

def f_filtre_exclusion_d_une_liste_de_noms(path, liste_dossiers, liste_filtre_exclu, char_os):
    p_debugg("Debut f_filtre_exclusion_d_une_liste_de_noms")

    # applique le filtre
    vl_liste_finale = copy.copy(liste_dossiers)

    # dans le cas de plusieurs dossiers en param separe par un ,
    vl_dossiers = path.split(",")

    if liste_filtre_exclu <> "" :
        if ";" in liste_filtre_exclu :
            vl_liste_filtre = liste_filtre_exclu.split(";")
        else :
            vl_liste_filtre = liste_filtre_exclu.split(",")

        for i in vl_dossiers :
        # balaie tous les dossiers fournis

            for filtre_exclusion in vl_liste_filtre :
            # balaie avec tous les filtres
                print "Utilisation du filtre : ", filtre_exclusion

                for ind in liste_dossiers :
                    # recherche dans la liste
                    if filtre_exclusion in ind[len(i):] :
                        if ind[:len(i)] == i :
                            print "dossier : ", ind, " ignore"
                            vl_liste_finale.remove(ind)
                    else :
                        p_debugg("le dossier : " + str(ind) + " va etre supprime - non concerne par le filtre")

        p_debugg("liste a traiter : " + str(vl_liste_finale))
        return vl_liste_finale
    else :
        return liste_dossiers


def f_filtre_retention(liste_dossier, duree):
    p_debugg("f_filtre_retention")
    resultat = []
    nb_fic_ignore = 0
    global vg_time_creation

    print "Debut du filtre de retention"
    if duree <> 0 : # evite de recalculer a chaque iteration la retention
        date_du_jour = datetime.datetime.now()
        date_retention = date_du_jour - datetime.timedelta(days=duree) # calcul de la retention
        p_debugg( "date limite de retention : " + str( date_retention.ctime() ) ) #.strftime("%Y%m%d%H%M%S)

        for mon_fic in liste_dossier :
            # modification pour travailler seulement sur la date de creation
            if vg_time_creation == False :
                if __SYSTEM == "win32": # cas windows on calcule la date sur la creation et la modification
                    date_derniere_modif_fichier = datetime.datetime.fromtimestamp(os.stat(mon_fic).st_mtime)
                    date_creation_fichier = datetime.datetime.fromtimestamp(os.stat(mon_fic).st_ctime)
                    if date_creation_fichier > date_derniere_modif_fichier :
                        p_debugg("warning date de creation plus recente que la date de modification - date de creation utilise")
                        date_du_fichier = date_creation_fichier
                    else :
                        date_du_fichier = date_derniere_modif_fichier
#                    p_debugg( "date du fichier : "+ str(mon_fic)+ " - "+ str(date_du_fichier))
                else : # cas unix/linux on calcule la date sur la modification
                    date_du_fichier = datetime.datetime.fromtimestamp(os.stat(mon_fic).st_mtime)
#                    p_debugg( "date du fichier : "+ str(mon_fic)+ " - "+ str(date_du_fichier))
                p_debugg( "date du dossier : "+ str(mon_fic)+ " - "+ str(date_du_fichier))
            else :
                p_debugg("Calcul de la retention sur la date de creation")
                date_creation_fichier = datetime.datetime.fromtimestamp(os.stat(mon_fic).st_ctime)
                date_du_fichier = date_creation_fichier

            if (date_retention > date_du_fichier):
                resultat.append(mon_fic)
                p_debugg( "dossier plus ancien - traitement du dossier : " + str(mon_fic))
            else:
                # p_debugg( "fichier :" + str(mon_fic) + "-" + str(date_du_fichier) + "trop recent - ignore" + str( date_retention.ctime() ))
                print "Dossier ignore : " , mon_fic,"-", str(date_du_fichier), "car trop recent"
                nb_fic_ignore += 1
        print (str(nb_fic_ignore) + " Dossiers ignores")
        return resultat
    else :
        p_debugg( "Pas de filtre de traitement de duree ...")
        return liste_dossier

def p_verif_existence_dir(dossier): # sort en erreur dans le cas ou le dossier n existe pas

    liste_dossier = dossier.split(",")

    for i in liste_dossier :
        p_debugg("Verif existence du dossier : " + str(i))
        if os.path.exists(i) == False :
            p_print_error("Erreur dossier : " + str(i) + " absent",vg_bl)
        if os.access(i,os.W_OK) == False :
            p_print_error("Erreur de droits (write) sur le dossier : " + str(i),vg_bl)
        if os.access(i,os.R_OK) == False :
            p_print_error("Erreur de droits (read) sur le dossier : " + str(i),vg_bl)

def p_gestion_param(chaine):
    p_debugg("f_filtre_retention")
    global vg_verbeux # mode debug
    global vg_directory
    global vg_time
    global vg_exclude
    global vg_recursif
    global VG_BOUCHON
    global VG_code_retour_bouchon
    global vg_time_creation
    global vg_simu

    try:
        opts, args = getopt.getopt(chaine, "hrd:e:t:B:cs", ["help", "bouchon=", "debug"])

    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) + " !!!!!!!!!!!"
        p_printusage(vg_bl)


    for o, a in opts:
        if o in ("-h", "--help"):
            p_printusage(vg_bl)
        elif o == ("-d"):
            vg_directory = f_valorisation_var_system(a)
            p_debugg("directory a purger : " + str(vg_directory))
        elif o in ("--bouchon","-B"): # UTILISER POUR LE MODE BOUCHON
            VG_BOUCHON = True
            VG_code_retour_bouchon = a
        elif o == ("-r"):
            vg_recursif = True
            p_debugg("Mode recursif ACTIF")
        elif o == ("-e"):
            vg_exclude = a
            p_debugg("Liste d exclusion : " + vg_exclude)
        elif o == ("-t"):
            vg_time = int(a)
            p_debugg("Duree : " + str(vg_time))
            if vg_time < 0 :
                p_print_error("La valeur de temps doit etre positive",vg_bl)
        elif o == ("--debug"):
            vg_verbeux = True
        elif o == ("-c"):
            vg_time_creation = True
            p_debugg("La duree est calculee sur la date de creation")
        elif o == ("-s"):
            vg_simu = True
            p_debugg("Mode simulation actif")
        else:
            assert False, "option invalide"

    if VG_BOUCHON == True :
        p_print_error("Mode Bouchon",VG_code_retour_bouchon)

def f_suppression(liste_dossiers, mode_simulation):
    global vg_warning_suppression_fichier
    global vg_warning_liste_fichier
    global vg_directory
    global vg_chemin_user

    code_retour = 0


    try :
        os.chdir(os.path.realpath(vg_chemin_user))
    except OSError:
        print ("Erreur lors de l acces au dossier : "+str(os.path.realpath(vg_chemin_user)))
        p_print_error("",vg_bl)

    if mode_simulation == False :
        for i in liste_dossiers :
            try :
                print "del : ", i
                os.rmdir(i)

            except OSError , (errno,strerror):
                print "IMPOSSIBLE DE SUPPRIMER LE DOSSIER ... :", str(i)
                print "OS error (", str(errno), ") : ",str(strerror)
                code_retour = vg_bl
                vg_warning_suppression_fichier +=1
                vg_warning_liste_fichier.append(i)
            except :
                code_retour = vg_bl
                print "ANOMALIE LORS DE LA SUPPRESSIONS, cause non connue"
    else :
        for i in liste_dossiers :
            print "simu del : ",  i
    return code_retour

def p_print_error(mesg, num):
    # retourne le message d erreur et sort en code retour
    print mesg
    print "Sortie en code retour : " + str(num)
    sys.exit(num)

#*****************************************************************************************************************************  #
# definition des fonctions par system d exploitation
#*****************************************************************************************************************************  #
def f_lancement(params):
    # global code_retour_fonction


    liste = f_listdirectory(vg_directory, vg_recursif,params)
    p_debugg("liste des dossiers a traiter : "+str(liste))

    liste_exclu = f_filtre_exclusion_d_une_liste_de_noms(vg_directory,liste,vg_exclude, params)

    p_debugg("Liste apres filtre exclu : " + str(liste_exclu))

    liste_date = f_filtre_retention(liste_exclu, vg_time)
    p_debugg("Liste apres filtre date : " + str(liste_date))
    
    code_retour_fonction = f_suppression(liste_date,vg_simu)

    return code_retour_fonction

#*****************************************************************************************************************************  #
# Main
#*****************************************************************************************************************************  #
if __name__ == "__main__":
    # Variables du programme principal

    #Variable code_retour
    #Ele est posiionnee avec un code retour different de 0 afin que la fonction modifie sa valeur
    code_retour_fonction = 56


    # Affiche la version
    print version + "\n"

    # Affiche la ligne de commande
    print "Execution de la commande : "
    print str(sys.argv)

    vg_chemin_user = os.getcwd()
    # Gestion des arguments en parametre
    # ++++++++++++++++++++++++++++++++++
    nombre_d_element = arguments = None
    name = ""

    vl_gestion_param = sys.argv[1:]

    p_gestion_param(vl_gestion_param)
    # affiche un message d erreur en cas de params incorrects
    p_test_options(vl_gestion_param)
    p_verif_existence_dir(vg_directory)

    # ++++++++++++++++++++++++++++++++++

    #*****************************************************************************************************************************  #
    # Lancement de la commande selon la plateforme utilisee
    #*****************************************************************************************************************************  #

    if __SYSTEM == "win32":
            code_retour = f_lancement("\\")
    elif __SYSTEM == "hp-ux11":
            code_retour = f_lancement("/")
    elif __SYSTEM == "linux2":
            code_retour = f_lancement("/")
    else:
        p_print_error("PF inconnue !!!",vg_bl)
            


    #######################################
    # Verification du code retour         #
    #######################################
    if code_retour not in (0, 1,3,None):
        p_print_error("Erreur inattendue",vg_bl)
    if vg_warning_suppression_fichier <> 0 :
        p_print_error("Anomalie au niveau des droits sur : " + str(vg_warning_suppression_fichier) + " dossier a traiter : " + str(vg_warning_liste_fichier),vg_bl)

    #######################################
    # Fin du Programme avec code_retour   #
    #######################################
    p_print_error("Fin du programme !!!!",code_retour)

