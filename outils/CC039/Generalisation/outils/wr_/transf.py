#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
#****************************    Fiche signaletique shell  encodage: iso-8859-15    ****************************************    #
# Nom du programme : transfert.py    But du programme : transfert de fichier     Version minimum de l'interpreteur python : 2.4
#**********************************************    Historique    *************************************************************  #
# Version       Date            AUTEUR          ENTREPRISE      Commentaires
# 1.0           16/03/2012      C.CHAPUT        La Poste        Creation
# 1.1           04/06/2012      C.CHAPUT        la Poste        Corrections suite a qualif T.B
# 1.2           04/10/2012      C.CHAPUT        La Poste        Correction suite a pb de lib win32 et compatibilite UNIX
# 1.3           21/02/2013      C.CHAPUT        La Poste        Correction suite a incident lorsque les fichiers sont superieurs a 1Mo
# 1.4           26/02/2013      C.CHAPUT        La Poste        Ajout du code retour 3 en cas d absence de fichier
# 1.5           17/01/2014      C.CHAPUT        La Poste        Calcul de la retention -t sur le mtime pour linux unix
# 1.6           10/09/2015      R.SAVIGNY       PIXON           Modification de l'option "--force <bloc|pass|suppr>"
# 1.7           25/01/2017      Z.BEN ALI       La Poste        Modification du code retour de l'option "--force=suppr"
# 1.8           09/04/2018      Z.BEN ALI       La Poste        Modification du traitement du timestamp (avant seul le timestamp 
#                                                               au debut du nom était traite, maintenant on peut traiter les 2)
# 1.9           11/02/2021      Y. LE BOUEDEC   ATOS            Modification pour test sur repertoire distant
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
# import re
import os.path
import glob
# import string
import datetime
from shutil import copyfile, move
from os import remove
# import re
import time

# Mode Bouchon : False ou True
VG_BOUCHON = False
VG_code_retour_bouchon = 5 # Code retour dans le cas de l'utilisation du mode bouchon
# Fin du parametrage du mode bouchon

# Variablles globales
#vg_outputfiles = ''
vg_inputdirectory = ''
vg_outputdirectory = ''
vg_inputfiles = ''
vg_savedirectory = ''
vg_keeptimestamp = False
vg_force = None
vg_force_err_count = 0
vg_force_av_count = 0
vg_no_tmp = False
vg_md5sum = False
vg_82safe = True
vg_complete = False
vg_retention = None
vg_version = None
vg_onlyone = False
vg_delta = None
vg_verbeux = False # Pour le debugg
vg_end=False
vg_test_dir = False
vg_test_dir_tempo = 10  # tempo de retentative pour test repertoire
vg_test_dir_retry = 5  # nombre de tentatives pour test repertoire

# Variablles globales code retour VTOM
vg_bl = 3
vg_wg = 1

# Definition des variables systeme
__SYSTEM = sys.platform
__PYTHON_VERSION = sys.version

# Version du CC a completer
version = "transf.py v1.9 - python "+__PYTHON_VERSION+" - "+__SYSTEM

#*****************************************************************************************************************************  #
# Definitions des fonctions locales
#*****************************************************************************************************************************  #

def p_test_options(arguments):
    # teste la validite de certaines options de la ligne de commande
    global vg_inputdirectory
    global vg_outputdirectory
    global vg_inputfiles
    global vg_savedirectory
    global vg_complete
    global vg_retention
    global vg_version
    global vg_delta
    global vg_keeptimestamp

    print "Tests des arguments du script ..."
    p_debug("arguments : " + str(arguments))
    if not arguments:
        print "*** un argument est manquant ***"
        p_printusage(vg_bl)

    if vg_inputdirectory == '':
        p_print_error("L'argument dossier input est vide ...", vg_bl)

    if vg_outputdirectory == '':
        p_print_error("L'argument dossier output est vide ...",vg_bl)

    if vg_inputfiles == '':
        p_print_error("L'argument filtre fichiers est vide ...",vg_bl)

    p_debug("Save dir : " + vg_savedirectory + " " + str(vg_retention) + ":" + str(vg_version))
    if vg_savedirectory <> '':
        if (vg_retention == None) and (vg_version == None):
            p_print_error("Option Retention ou Version non renseignee ...",vg_bl)
        if (vg_retention <> None) and (vg_version <> None):
            p_print_error("Options Retention et Version incompatibles ...",vg_bl)

    p_debug("Complete : " + str(vg_complete) + " " + str(vg_delta))
    if (vg_delta <> None) and (vg_complete == True):
        p_print_error("Options delta et complete imcompatibles",vg_bl)

    if vg_keeptimestamp == True :
        if (vg_delta == None) and (vg_complete == False):
            p_print_error("Option keeptimestamp doit etre utilisee avec delta et complete",vg_bl)
    print "Tests des arguments du script termines"
	
def p_debug(chaine):
    # permet d afficher certains messages lorsque l option debugg est active
    if vg_verbeux : print str(chaine)

def p_print_error(mesg, num):
    # retourne le message d erreur et sort en code retour
    print mesg
    print "Sortie en code retour " + str(num)
    sys.exit(num)

def p_printusage(err):
    # affiche le message d aide
    print r"""
   Usage de la commande :
   transf.py -i <input_directory> -o <output_directory> -f <filtre_fichier>

   Les parametres suivants sont obligatoires :
        -i <input_directory>
        -o <output_directory>
        -f <filtre_fichier>

   Les parametres optionnels :
        -I                                  : -i et -o sont positionnes a TRANSFERT/IMPORT et DONNEES/IMPORT
        -O                                  : -i et -o sont positionnes a DONNEES/export et TRANSFERT/EXPORT
        --save=            <nom_dossier>    : nom du dossier de sauvegarde
        --keeptimestamp                     : conserve le timestamp des fichiers apres transfert
        --force=           suppr|bloc|pass  : Traitement du cas, fichier existe deja :
                                              <bloc> (Defaut) sortie immediate CR3
                                              <pass> Passe le fichier et continue, sortie en fin de traitement CR3, affiche le nombre d'echecs
                                              <suppr> Supprime le fichier existant, et continue son traitement, sortie en fin de traitement CR3,
                                                      affiche le nombre d'echecs
        --no_tmp                            : pas de fichier temporaire lors du transfert
        --no82safe                          : ne prend pas en compte le filtre de fichiers 8 + 2
        --complete                          : transfert le fichier le plus recent et suppr les autres
        --retention=       < nb de jours>   : retention en nb de jours des fichiers presents sous SAVE
        --version=         < nb de version> : retention en nb de version des fichiers presents sous SAVE
        --onlyone                           : transfert le fichier le plus ancien
        --delta=           < nb de version> : transfert n fichiers du plus vieux au plus recent
        --cr3                               : retourne un code retour 3 au lieu de 1 dans le cas d un fichier absent
        --end                               : précise que le timestamp se situe en fin de nom du fichier
												Par défaut le timestamp est au début du nom de fichier

        --debug                             : Utilise a des fins de debug
        -h | --help                         : Affiche l'aide
        -B | --bouchon=   <code retour>     : bouchon CCO

        -n | --testdir    (mode nothing = test de repertoire uniquement)

        Exemple: transf.py -I -f "*b2caaaaa.b2" --no82safe --onlyone
        Attention ne pas mettre de point avant le "*" si le timestamp est à la fin du nomde fichier

        Exemple: transf.py -I -f "b2caaaaa.b2*" --no82safe --onlyone --end 
        Attention ne pas mettre de point avant le "*" si le timestamp est à la fin du nomde fichier


    """

    sys.exit(err)

def f_valorisation_var_system(chemin):
    # permet de valoriser des $ sous unix ou % sous windows
    resultat = os.path.expandvars(chemin)
    p_debug("Resultat de la valorisation " + str(resultat))
    return resultat

def f_param_lg_commande(char_os):
    # Gestion des arguments passes en parametre de la ligne de commandes
    global vg_inputdirectory
    global vg_outputdirectory
    global vg_inputfiles
    global vg_savedirectory
    global vg_keeptimestamp
    global vg_force
    global vg_no_tmp
    global vg_md5sum
    global vg_82safe
    global vg_complete
    global vg_retention
    global vg_version
    global vg_onlyone
    global vg_delta
    global VG_BOUCHON
    global VG_code_retour_bouchon
    global vg_verbeux # utiliser pour le debuggage
    global vg_bl
    global vg_wg
    global vg_end #pour preciser que timestamp en fin de nom de fichier
    global vg_test_dir

    arguments = sys.argv[1:]
    try:
        opts, args = getopt.getopt(arguments, "hnB:i:o:f:IO",
            ["help","bouchon=","save=","keeptimestamp","force=","no_tmp","no82safe",
            "complete","retention=","version=","onlyone","delta=","debug","cr3","end", "testdir"])

    except getopt.GetoptError, err:
        # print help information and exit:
        # will print something like "option -z not recognized"
        print "!!! ERREUR !!! l option n est pas reconnue : " + str(err)
        p_printusage(vg_bl)

    for o, a in opts:
        p_debug(str(o) + " " + str(a) )

        if o in ("-h", "--help"):
            p_printusage(vg_bl)

        elif o in ("--debug"):
            vg_verbeux = True
            p_debug("mode verbeux actif")

        elif o in ("-B", "--bouchon"):
            VG_BOUCHON = True
            VG_code_retour_bouchon = int(a)
            p_debug("Valeur du mode bouchon : " + str(VG_BOUCHON))
            p_print_error("Mode bouchon", VG_code_retour_bouchon)

        elif o in ("-i"):
            vg_inputdirectory = f_valorisation_var_system(a)
            if vg_inputdirectory[len(vg_inputdirectory)-1] == char_os :
                p_debug("suppression de : " + str(char_os) + " en fin de repertoire")
                vg_inputdirectory = vg_inputdirectory.rstrip(char_os)
            p_debug("nom du repertoire en entree : " + str(vg_inputdirectory))

        elif o in ("-o"):
            vg_outputdirectory = f_valorisation_var_system(a)
            if vg_outputdirectory[len(vg_outputdirectory)-1] == char_os :
                p_debug("suppression de : " + str(char_os) + " en fin de repertoire")
                vg_outputdirectory = vg_outputdirectory.rstrip(char_os)
            p_debug("nom du repertoire en sortie : " + str(vg_outputdirectory))

        elif o in ("-f"):
            vg_inputfiles = a
            p_debug("filtre fichers : " + str(vg_inputfiles))

        elif o in ("--save"):
            vg_savedirectory = f_valorisation_var_system(a)
            if vg_savedirectory[len(vg_savedirectory)-1] == char_os :
                p_debug("suppression de : " + str(char_os) + " en fin de repertoire")
                vg_savedirectory = vg_savedirectory.rstrip(char_os)
            p_debug("nom du repertoire de sav : " + str(vg_savedirectory))

        elif o in ("--keeptimestamp"):
            vg_keeptimestamp = True
            p_debug("Mode conservation timestamp actif : " + str(vg_keeptimestamp))

        elif o in ("--force"):
            if a not in ("suppr","pass","bloc") :
                p_print_error("option force : les valeurs possibles sont suppr ou bloc",vg_bl)
            vg_force = a
            p_debug("Option force active en mode : " + str(vg_force))

        elif o in ("--no_tmp"):
            vg_no_tmp = True
            p_debug("Option no_tmp active option : " + str(vg_no_tmp))

        elif o in ("--no82safe"):
            vg_82safe = False
            p_debug("Option no82safe desactive option : " + str(vg_82safe))

        elif o in ("--complete"):
            vg_complete = True
            p_debug("Option complete active option : " + str(vg_complete))

        elif o in ("--retention"):
            vg_retention = int(a)
            p_debug("Retention de n jours active : " + str(vg_retention))

        elif o in ("--version"):
            vg_version = int(a)
            p_debug("Retention de n versions active : " + str(vg_version))

        elif o in ("--onlyone"):
            vg_onlyone = True
            p_debug("Option onlyone active : " + str(vg_onlyone))

        elif o in ("--delta"):
            vg_delta = int(a)
            p_debug("Option delta active : " + str(vg_delta))

        elif o in ("-I"):
            input = None
            output = None
            if __SYSTEM == "win32":
                input = f_valorisation_var_system("%TRANSFERT%")
                if input == "%TRANSFERT%":
                    p_print_error("variable non definie",vg_bl)
                output = f_valorisation_var_system("%DONNEES%")
            else :
                input = f_valorisation_var_system("$TRANSFERT")
                output = f_valorisation_var_system("$DONNEES")

            vg_inputdirectory = input + char_os + "import"
            vg_outputdirectory = output + char_os + "import"
            p_debug("nom du repertoire en entree : " + str(vg_inputdirectory))
            p_debug("nom du repertoire en sortie : " + str(vg_outputdirectory))

        elif o in ("-O"):
            input = None
            output = None
            if __SYSTEM == "win32":
                input = f_valorisation_var_system("%DONNEES%")
                output = f_valorisation_var_system("%TRANSFERT%")
            else :
                input = f_valorisation_var_system("$DONNEES")
                output = f_valorisation_var_system("$TRANSFERT")

            vg_inputdirectory = input + char_os + "export"
            vg_outputdirectory = output + char_os + "export"
            p_debug("nom du repertoire en entree : " + str(vg_inputdirectory))
            p_debug("nom du repertoire en sortie : " + str(vg_outputdirectory))

        elif o in ("--cr3") :
            p_debug("code retour force a 3 au lieu de 1")
            vg_wg = vg_bl
        
        elif o in ("--end") : 
            p_debug("Le paramètre indiquant que le timestamp est a la fin du fichier est active")
            vg_end=True

        elif o in ("-n", "--testdir"):
            vg_test_dir = True
            p_debug("mode test repertoire actif")

        else:
            assert False, "option invalide !!!"
    p_test_options(arguments) # Verifie les param obligatoires
    return 0

def f_timestamp_name():
    # retourne un timestamp au format chaine de caractere
    today = datetime.datetime.now()
    return str(today.strftime("%Y%m%d%H%M%S"))

def f_listdirectory(path, filtre, char_os):
    # Retourne une liste de fichier en fonction du filtre et du path

    fichier=[]
    extension_filtre = False
    p_debug("fonction f_listdirectory")
    if (((vg_complete == True) or (vg_delta <> None) or (vg_onlyone == True)) and (vg_82safe == True) and vg_end == False) :
        p_debug("option complete, delta, onlyone avec vg_82safe actif  ; timestamp au debut")
        chemin_full = path+char_os+"??????????????.????????.??"
        l = glob.glob(chemin_full)
        extension_filtre = True

    elif (((vg_complete == True) or (vg_delta <> None) or (vg_onlyone == True)) and (vg_82safe == True)and vg_end == True) :
        p_debug("option complete, delta, onlyone avec vg_82safe actif ; timestamp a la fin")
        chemin_full = path+char_os+"????????.??.??????????????"
        l = glob.glob(chemin_full)
        extension_filtre = True


    elif (((vg_complete == True) or (vg_delta <> None) or (vg_onlyone == True)) and (vg_82safe == False) and vg_end == False) :
        p_debug("option complete, delta, onlyone avec vg_82safe inactif; timestamp au debut")
        chemin_full = path+char_os+"??????????????.*"
        l = glob.glob(chemin_full)
        p_debug('chemin full '+ str(chemin_full))
        p_debug('l '+ str(l))
        extension_filtre = True

    elif (((vg_complete == True) or (vg_delta <> None) or (vg_onlyone == True)) and (vg_82safe == False) and vg_end == True) :
        p_debug("option complete, delta, onlyone avec vg_82safe inactif ; timestamp a la fin")
        chemin_full = path+char_os+"*.??????????????" 
        l = glob.glob(chemin_full)     
        p_debug('chemin full '+ str(chemin_full))       
        p_debug('l '+ str(l))
        extension_filtre = True


    elif vg_82safe == True :
        p_debug("option 8.2 active")
        chemin_full = path+char_os+"????????.??"
        l = glob.glob(chemin_full)
    else :
        p_debug("option 8.2 desactive")
        chemin_full = path+char_os+"*"
        l = glob.glob(chemin_full)
        # * - necessaire pour pouvoir lister la totalite

    # recup la liste des fichiers filtres dans le dossier courant
    if extension_filtre == True and vg_end == False :
        chemin_filtre = path+char_os+"??????????????."+filtre
    elif extension_filtre == True and vg_end == True :
        chemin_filtre = path+char_os+filtre+".??????????????"

    else :
        chemin_filtre = path+char_os+filtre
    p_debug("chemin filtre : "+ str(chemin_filtre))
    
    l_filtree = glob.glob(chemin_filtre)
    p_debug("l_filtree : "+ str(l_filtree))

    for i in l:
        if os.path.isfile(i):
            if i in l_filtree :
                p_debug("fichier : " +i + " ajoute")
                fichier.append(i)
    return fichier

def f_nom_fichier_sans_timestamp(nom):
    p_debug("nom du fichier avec timestamp :"+ str(nom))
    
    if vg_end == True :
        p_debug("nom du fichier sans timestamp :"+ str(nom[len(nom)-26:len(nom)-15]))
        return nom[len(nom)-26:len(nom)-15] # retourne le nom de fichier sans le timestamp apres le nom de fichier
    else:
        p_debug("nom du fichier sans timestamp :"+ str(nom[len(nom)-11:len(nom)]))
        return nom[len(nom)-11:len(nom)] # retourne le nom de fichier sans le timestamp avant

def f_get_free_space(folder):
    # retourne l espace libre d un dossier du disque octet
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
        return long(free_bytes.value)
    else:
        stat = os.statvfs(folder)
        return long(stat.f_bsize * stat.f_bavail)

def f_nb_objet(liste, objet):
    # retourne le nb d objet present dans une liste
    nb = 0
    for i in liste :
        if objet == i:
            nb +=1
    return nb

def f_liste_type_fichier(liste, char_os):
    # retourne la liste des noms de fichiers 8.2 differents
    liste_f=[]

    for i in liste :
        nom = f_nom_fichier_sans_timestamp(i)
        if nom not in liste_f :
            liste_f.append(nom)

    if liste_f == [] :
        p_print_error("Anomalie la liste de type de fichiers est null ...", vg_bl)
    return liste_f

def f_fichier_plus_vieux_liste(liste_fic, nb_version,char_os):
    # retourne les fichiers plus vieux que le nb de version - possibilite de retourner plusieurs
    liste=[]
    liste_nom=[]

    liste_fic.sort()
    for i in liste_fic :
        nom = f_nom_fichier_sans_timestamp(i)
        liste_nom.append(nom)
        nb_elt = f_nb_objet(liste_nom, nom)
        if nb_elt <= nb_version :
            liste.append(i)
    return liste

def f_fichier_plus_recent_liste(liste_fic, char_os):
    # retourne le fichier le plus recent pour une liste - possibilite de retourner plusieurs
    liste=[]
    liste_nom=[]

    liste_fic.sort(reverse=True)
    for i in liste_fic :
        if f_nom_fichier_sans_timestamp(i) not in liste_nom :
            liste_nom.append(f_nom_fichier_sans_timestamp(i))
            liste.append(i)
    return liste

def f_retire_fichiers(liste_fic, fic):
    # suppr un fichier d une liste
    for i in fic :
        liste_fic.remove(i)
    return 0

def f_generation_liste_fichiers_en_entree(input_directory, input_file, char_os):
    # retourne la liste des fichiers a traiter
    # dans le cas d une liste vide sort en code warning

    path = input_directory + char_os + input_file
    print "Recherche des fichiers presents : " + str(path)

    list_fichiers = None
    # recup la liste de tous les fichiers
    list_fichiers = f_listdirectory(input_directory ,input_file, char_os)

    # dans le cas ou la liste de fichiers est vide sortie en code warning
    if len(list_fichiers) == 0 :
        p_print_error("Pas de fichier a traite !!! ", vg_wg)

    return list_fichiers


def p_verif_existence_dir(dossier):
    # verifie l existence d un dossier
    # sort en erreur dans le cas ou le dossier n existe pas
    p_debug("Verif existence du dossier : " + str(dossier))
    # YLC : 09/02/21 , os.path.isdir peut verifier un repertoire
    # vg_test_dir_tempo  = tempo de retentative pour test repertoire
    # vg_test_dir_retry  = nombre de tentatives pour test repertoire

    tstrep = os.path.exists(dossier)
    if not tstrep:
        for i in range(vg_test_dir_retry):
            time.sleep(vg_test_dir_tempo)
            p_debug("Verif existence du dossier a nouveau : " + str(dossier))
            tstrep = os.path.exists(dossier)
            if tstrep:
                break
    if not tstrep:
        p_print_error("Erreur dossier : " + str(dossier) + " absent",vg_bl)

def p_copy(input, output):
    # fonction de copie d un fichier
    p_debug("p_copy")

    if vg_test_dir:
        print "Pas d execution du copyfile : test repertoire uniquement"
        return

    try:
        p_debug("Debut de la copie :" + str(input) + " - " + str(output))
        copyfile(input,output)
    except IOError , (errno,strerror):
        print "I/O error (", str(errno), ") : ",str(strerror)
        p_print_error("Ecriture impossible dans le repertoire de destination",vg_bl)
    except :
        p_print_error("Erreur lors de la copie",vg_bl)
    p_debug("la commande copyfile a reussi")


def p_move(input, output):
    # fonction de deplacement d un fichier
    p_debug("p_move")

    if vg_test_dir:
        print "Pas d execution du movefile : test repertoire uniquement"
        return

    try :
        p_debug("Debut du deplacement :" + str(input) + " - " + str(output))
        move(input, output)
    except IOError , (errno,strerror):
        print "I/O error (", str(errno), ") : ",str(strerror)
        p_print_error("Ecriture impossible dans le repertoire de destination",vg_bl)
    except :
        p_print_error("Erreur lors du move",vg_bl)
    p_debug("la commande move a reussi")


def p_remove(input):
    # fonction de suppression d un fichier
    p_debug("p_remove")

    if vg_test_dir:
        print "Pas d execution du removefile : test repertoire uniquement"
        return 0

    try :
        print("Suppression du fichier :"+str(input))
        remove(input)
    except OSError , (errno,strerror):
        print "I/O error (", str(errno), ") : ",str(strerror)
        p_print_error("Erreur de suppression",vg_bl)
    except :
        p_print_error("Erreur lors du remove",vg_bl)
    p_debug("la commande suppr a reussi")
    return 0



def f_filtre_retention(liste_fic, duree):
    # retourne une liste de fichiers plus anciens que le filtre de duree
    p_debug("f_filtre_retention")

    resultat = []
    nb_fic_ignore = 0

    print "Debut du filtre de retention"
    if duree <> 0 : # evite de recalculer a chaque iteration la retention
        date_du_jour = datetime.datetime.now()
        date_retention = date_du_jour - datetime.timedelta(days=duree) # calcul de la retention
        p_debug( "date limite de retention : " + str( date_retention.ctime() ) ) #.strftime("%Y%m%d%H%M%S)

        for mon_fic in liste_fic :
            if __SYSTEM == "win32": # cas windows on calcule la date sur la creation et la modification
                date_derniere_modif_fichier = datetime.datetime.fromtimestamp(os.stat(mon_fic).st_mtime)
                date_creation_fichier = datetime.datetime.fromtimestamp(os.stat(mon_fic).st_ctime)
                if date_creation_fichier > date_derniere_modif_fichier :
                    p_debug("warning date de creation plus recente que la date de modification - date de creation utilise")
                    date_du_fichier = date_creation_fichier
                else :
                    date_du_fichier = date_derniere_modif_fichier
#                p_debug( "date du fichier : "+ str(mon_fic)+ "-"+ str(date_du_fichier))
            else : # cas unix/linux on calcule la date sur la modification
                date_du_fichier = datetime.datetime.fromtimestamp(os.stat(mon_fic).st_mtime)
                p_debug( "date du fichier : "+ str(mon_fic)+ " - "+ str(date_du_fichier))
            if (date_retention > date_du_fichier):
                resultat.append(mon_fic)
                p_debug( "fichier plus ancien - traitement du fichier : " + str(mon_fic))
            else:
                # p_debug( "fichier :" + str(mon_fic) + "-" + str(date_du_fichier) + "trop recent - ignore" + str( date_retention.ctime() ))
                print "fichier ignore : " , mon_fic,"-", str(date_du_fichier), "car trop recent"
                nb_fic_ignore += 1
        print (str(nb_fic_ignore) + " fichiers ignores")
        return resultat
    else :
        p_debug( "Pas de filtre de traitement de duree ...")
        return liste_fic


def f_calcul_assez_de_place(nom_fichier, dossier_arrivee):
    p_debug("f_calcul_assez_de_place")

    total_libre = f_get_free_space(dossier_arrivee)
    taille_fichier = os.path.getsize(nom_fichier)
    print("Taille de l espace libre : " + str(total_libre))
    print("Taille du fichier a transferer : " + str(taille_fichier))
    if (taille_fichier) < total_libre :
        return True
    else :
        return False



def f_transfert_un_fichier(nom, char_os):
    p_debug("f_transfert_un_fichier")
    global vg_force_err_count
    global vg_force_av_count
    vl_force_pass_error = False
    vl_force_suppr_avertissement = False
    vl_force_suppr_error = False
    # chemin = os.path.dirname(nom)
    nom_fichier = os.path.basename(nom)
    nom_fichier_absolu = nom
    nom_fichier_tempo = nom_fichier + ".tmp" + f_timestamp_name()
    nom_fichier_tempo_absolu = vg_outputdirectory+char_os+nom_fichier_tempo
    nom_fichier_sortie_absolu = vg_outputdirectory+char_os+nom_fichier

    # Verifie l espace libre
    p_debug("Calcul espace libre " + str(nom_fichier_absolu) + " - " + str(vg_outputdirectory))
    if f_calcul_assez_de_place(nom_fichier_absolu,vg_outputdirectory) == False :
        p_print_error("pas assez de place !!!",vg_bl)

    # dans le cas de l option complete suppression du timestamp
    if (vg_complete == True) and (vg_keeptimestamp == False) :
        p_debug("cas complete et suppr timestamp")
        nom_fichier_sortie_absolu = vg_outputdirectory+char_os+f_nom_fichier_sans_timestamp(nom)

    # dans le cas ou vg_delta est egal a 1, on suppr le timestamp
    if (vg_delta == 1) and (vg_keeptimestamp == False) :
        p_debug("Cas delta = 1")
        nom_fichier_sortie_absolu = vg_outputdirectory+char_os+f_nom_fichier_sans_timestamp(nom)
        print "nom_fichier_sortie_absolu " + str(nom_fichier_sortie_absolu)

    if os.path.isfile(nom_fichier_sortie_absolu) :
        if vg_force == "bloc" :
            print("Fichier \""+str(nom_fichier_sortie_absolu)+"\" deja present en sortie - option \"bloc\" active - on sort + CR3.")
            p_print_error("Fichier deja present", vg_bl)
        elif vg_force == "pass" :
            print("Fichier \""+str(nom_fichier_sortie_absolu)+"\" deja present en sortie - option \"pass\" active - on passe + CR3 en fin de traitement.")
            vl_force_pass_error = True
        elif vg_force == "suppr" :
            print("Fichier \""+str(nom_fichier_sortie_absolu)+"\" deja present en sortie - option \"suppr\" active - on supprime + CR1 en fin de traitement.")
            vl_force_suppr_avertissement = True            
            if p_remove(nom_fichier_sortie_absolu) <> 0 :
                vl_force_suppr_error = True
                print("Anomalie lors de la suppression du fichier \""+str(nom_fichier_sortie_absolu)+"\"")
        else :
            print("Fichier \""+str(nom_fichier_sortie_absolu)+"\" deja present en sortie - pas d'option \"force\" active - on sort + CR3.")
            p_print_error("Fichier deja present", vg_bl)

    if vl_force_suppr_avertissement == True : vg_force_av_count += 1
    if vl_force_suppr_error == True : vg_force_err_count += 1
    if vl_force_pass_error == True :
        vg_force_err_count += 1
        print("Erreur de traitement sur \""+str(nom_fichier_sortie_absolu)+"\", abandon du transfert, on continue.")
    else :
        if vg_savedirectory <> '' :
            print "Sauvegarde du fichier " + str(nom)
            nom_fichier_save = vg_savedirectory + char_os + "SAVE" + f_timestamp_name() +'.'+ nom_fichier
            p_copy(nom_fichier_absolu,nom_fichier_save)

        print "Debut du transfert du fichier : " + nom_fichier_absolu + " vers : " + nom_fichier_sortie_absolu
        if vg_no_tmp == False :
            p_debug("Cas de transfert avec fichier tempo")
            p_copy(nom_fichier_absolu, nom_fichier_tempo_absolu)
            p_move(nom_fichier_tempo_absolu, nom_fichier_sortie_absolu)
            p_remove(nom_fichier_absolu)
        else :
            p_debug("Cas de transfert sans fichier tempo")
            p_copy(nom_fichier_absolu,nom_fichier_sortie_absolu)
            p_remove(nom_fichier_absolu)
        print "Fin du transfert"
    return 0

def f_filtre_version(liste_fichiers, nb_version, char_os):
    # retourne la liste des fichiers de + de nb_version
    p_debug("f_filtre_version")

    liste = liste_fichiers
    liste_f = []

    liste.sort(reverse=True)

    if len(liste) <= nb_version :
        print("nb de version inf, pas de suppr")
    else :
        cpt = nb_version
        while cpt < len(liste) :
            liste_f.append(liste[cpt])
            cpt +=1
    return liste_f

def f_transfert(liste_fichiers,char_os):
    # transfert une liste de fichiers
    p_debug("f_transfert")

    code_retour = 0

    liste_noms = []

    if liste_fichiers == None :
        p_print_error("Aucun fichier a traiter",vg_wg)

    for i in liste_fichiers :
        cr = f_transfert_un_fichier(i,char_os)
        if cr > code_retour :
            code_retour = cr


    if code_retour == 0 :
        # Nettoie le dossier SAVE dans le cas ou les transferts se sont bien termines

        # gestion des retentions
        if vg_retention <> None :
            p_debug("gestion des retentions")
            #reccup la liste des differents type de fichiers 8.2
            liste_noms = f_liste_type_fichier(liste_fichiers,char_os)

            liste =[]
            l_tous_fichiers_suppr = []

            for i in liste_noms :
                nom = f_nom_fichier_sans_timestamp(i)
                liste = glob.glob(vg_savedirectory+char_os+"*"+nom)

                # reccup les fichiers de plus de n jours
                l1 = f_filtre_retention(liste, vg_retention)
                if l1 <> [] :
                    l_tous_fichiers_suppr.extend(l1)

            if l_tous_fichiers_suppr <> []:
                print("Debut de suppression des fichiers trop anciens de : " + str(vg_retention) + " jours sous : " + vg_savedirectory)
                for i in l_tous_fichiers_suppr :
                    p_remove(i)


        # gestion des versions de sauvegarde
        if vg_version <> None :
            p_debug("gestion des versions")
            #reccup la liste des differents type de fichiers 8.2
            liste_noms = f_liste_type_fichier(liste_fichiers,char_os)

            liste =[]
            l_tous_fichiers_suppr = []
            for i in liste_noms :
                nom = f_nom_fichier_sans_timestamp(i)
                liste = glob.glob(vg_savedirectory+char_os+"*"+nom)

                # reccup les fichiers de plus de n_version
                l1 = f_filtre_version(liste, vg_version, char_os)
                if l1 <> [] :
                    l_tous_fichiers_suppr.extend(l1)

            if l_tous_fichiers_suppr <> []:
                print("Debut de suppression des fichiers trop anciens de : " + str(vg_version) + " versions sous : " + vg_savedirectory)
                for i in l_tous_fichiers_suppr :
                    p_remove(i)
    else :
        print "Attention une anomalie est detectee, les purges de versions-retentions n auront pas lieu"

    return code_retour

#*****************************************************************************************************************************  #
# definition des fonctions par system d exploitation
#*****************************************************************************************************************************  #
def lancement_windows(params):
    # lancement du programme
    code_retour_fonction = 56
    char_os = params

    # Verifie l existence des dossiers fournis
    p_verif_existence_dir(vg_inputdirectory)
    p_verif_existence_dir(vg_outputdirectory)
    if vg_savedirectory <> '':
        p_verif_existence_dir(vg_savedirectory)

    # Genere la liste des fichiers en entree
    l_fichiers = None
    l_fichiers = f_generation_liste_fichiers_en_entree(vg_inputdirectory,vg_inputfiles,params)

    if (vg_complete == True) :
        p_debug("Cas complete actif")
        fichiers = []
        fichiers=f_fichier_plus_recent_liste(l_fichiers, char_os)
        if fichiers == [] :
            p_print_error("liste vide : anomalie",vg_bl)
        code_retour_fonction = f_transfert(fichiers, char_os)
        if f_retire_fichiers(l_fichiers,fichiers) <> 0 :
            p_print_error("Erreur lors de la generation des fichiers timestampes a suppr", vg_bl)
        if l_fichiers ==[] :
            p_debug("Plus de fichiers timestamp en attente")
        else :
            for i in l_fichiers :
                p_remove(i)
    elif (vg_delta <> None) :
        p_debug("Cas delta actif")
        fichiers = []
        fichiers = f_fichier_plus_vieux_liste(l_fichiers, vg_delta, char_os)
        if fichiers == [] :
            p_print_error("liste vide : anomalie",vg_bl)
        code_retour_fonction = f_transfert(fichiers, char_os)
    elif (vg_onlyone == True) :
        p_debug("cas onlyone actif")
        fichiers = []
        fichier = []
        # retourne seulement les plus vieux fichiers
        fichiers = f_fichier_plus_vieux_liste(l_fichiers, 1, char_os)
        # reccup seulement le plus vieux fichier
        fichier.append(str(fichiers[0]))
        code_retour_fonction = f_transfert(fichier, char_os)
    else :
        # Transfert les fichiers
        code_retour_fonction = f_transfert(l_fichiers, char_os)

    print "fin ..."
    # retourne le code retour de l execution de la commande
    return code_retour_fonction

def lancement_hpux(params):
    #pas de modification particuliere pour l environnement hpux
    return lancement_windows(params)

def lancement_linux(params):
    #pas de modification particuliere pour l environnement linux
    return lancement_windows(params)




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
            import ctypes
            char_os = '\\'
            f_param_lg_commande(char_os)
            code_retour = lancement_windows(char_os)
    elif __SYSTEM == "hp-ux11":
            char_os = '/'
            f_param_lg_commande(char_os)
            code_retour = lancement_hpux(char_os)
    elif __SYSTEM == "linux2":
            char_os = '/'
            f_param_lg_commande(char_os)
            code_retour = lancement_linux(char_os)
    else:
            print "PF inconnue - sortie en CR 3"
            sys.exit(vg_bl)

    # Prise en compte des fichiers remplaces avec option --force
    if vg_force_av_count > 0 :
        print("Avertissement : Nombre de fichier(s) supprime(s) et remplace(s): \""+str(vg_force_av_count)+"\", sortie en CR1.")
        code_retour = vg_wg

    # Prise en compte des echecs de transfert avec option --force
    if vg_force_err_count > 0 :
        print("Erreur : \""+str(vg_force_err_count)+"\" fichiers sont en erreurs de traitement, sortie en CR3.")
        code_retour = vg_bl

    #######################################
    # Fin du Programme avec code_retour   #
    #######################################
    print "Fin du programme - code retour : " + str(code_retour)
    sys.exit(code_retour)

