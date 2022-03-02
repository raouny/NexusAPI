#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
#
#****************************    Fiche signaletique shell  encodage: iso-8859-15    ****************************************    #
# Nom du programme : purge.py    But du programme : Purger des fichiers - Version minimum de l'interpreteur python : 2.4
#***********************************************    Syntaxe    **************************************************************   #
# purge.py -i input_file -d input_directory -r -p fichier_param -s
#**********************************************    Historique    *************************************************************  #
# Version       Date            AUTEUR          ENTREPRISE      Commentaires
# 1.0           25/08/2011      C.CHAPUT        La Poste        Creation
# 1.1           23/11/2011      C.CHAPUT        La Poste        Correctif mode secure
# 1.2           28/11/2011      C.CHAPUT        La Poste        Modification du filtre d exclusion et optimisation + modif date
# 1.3           07/05/2012      C.CHAPUT        La Poste        Gestion des CR en cas d'erreur (mode force), mode Bouchon,
#                                                               option version, option history
# 1.4           05/03/2013      C.CHAPUT        La Poste        Correction du cas ou -v est a 0
# 1.5           22/03/2013      C.CHAPUT        La Poste        Modification du mode History pour gerer plusieurs fichiers
#                                                               ajout option --cr3
# 1.6           03/04/2013      C.CHAPUT        La Poste        Suppression du ou des fichier historises plutot que recreation a vide
# 1.7           14/06/2013      C.CHAPUT        La Poste        Ajout de l option --date_plus_ancienne pour la recherche et extension des noms de dossiers pour -w
# 1.8           12/07/2013      C.CHAPUT        La Poste        Ajout d un filtre d exclusion sur les noms de dossiers dans le cas du mode recursif
# 1.9           12/09/2013      C.CHAPUT        La Poste        Ajout d un controle de droits sur le dossier input suite a anomalie jira et correctif suite exclusion dossier
# 2.0           24/12/2013      C.CHAPUT        La Poste        Ajout du dossier backup et bkp pour l option -w
# 2.1           16/01/2014      C.CHAPUT        La Poste        Calcul de la retention -t sur le mtime pour linux unix et modification du filtre de version ajout de *
# 2.2           27/10/2014      R.SAVIGNY       PIXON           Activation de l'extention ZIP64, compression de fichiers > 2,5Go
# 2.3           12/08/2015      R.SAVIGNY       PIXON           I08079305  : Prise en compte fichier deja compresse 
#                                                               Detail de l'utilisation des caractere speciaux sous unix/linux
#                                                               Ajout de l'option "-D"
#                                                               Gestion des REGEX pour l'option "-x"
# 2.4           08/10/2015      R.SAVIGNY       PIXON           Fichier ouvert sous windows, on passe + CR0 
#                                                               Precision de l'usage de l'option "-D"
# 2.5           03/03/2016      P.BAUMES        La Poste        Affichage des fichiers ignores passe dans l'option debugg
#                                                               Ajout de l'affichage du nombre de fichiers supprimes
# 2.6           11/05/2016      R.SAVIGNY       PIXON           Ajout de l'option "-N (NO TIMESTAMP)" 
#                                                               Ajout du test "islink==False" dans le calcul de la place liberee
#                                                               Modifications pour utiliser les options "-t et -v" en meme temps
#**********************************************    Codes retour    ***********************************************************  #
# code 0: Normal - Code retour normal : L enchainement est poursuivi
# code 1: Warning - Detection d une anomalie : L enchainement peut etre poursuivi
# code 2: Erreur - Erreur Non bloquante : possibilite de lancer une procedure de reprise
# code 3: Critique - Erreur Critique
# code 3: Exemple d erreur - Erreur parametres incorrects
# code > 3 : Traitement en erreur avec un code retour particulier
#*****************************************************************************************************************************  #

# -------------------------
# Import des modules python
# -------------------------
import os
import sys
import getopt
import os.path
import glob
import datetime
import copy
import csv
import string
from shutil import copyfile, move
import zipfile
import mimetypes
import re
# -------------------------

# Mode Bouchon : False ou True
vg_BOUCHON = False
vg_code_retour_bouchon = 5 # Code retour dans le cas de l'utilisation du mode bouchon
# Fin du parametrage du mode bouchon

# Definition des variables systeme
__SYSTEM = sys.platform
__PYTHON_VERSION = sys.version

# Version du CC a completer
version = "purge.py v2.6 - python "+__PYTHON_VERSION+" - "+__SYSTEM

#*****************************************************************************************************************************  #
# Variables globales
#*****************************************************************************************************************************  #
vg_input_file=None                      # filtre fichiers
vg_input_directory=None                 # dossier de depart
vg_filtre_exclu=""                      # filtre exclusion
vg_param_file=None                      # mode fichier param
vg_recursif=False                       # mode recursif
vg_time=0                               # duree de retention
vg_simulation=False                     # simulation et non suppression
vg_warning_suppression_fichier=0        # nombre de warning lors de la suppression
vg_warning_liste_fichier=[]             # liste des fichiers en lecture seule
vg_espace_libere=0                      # espace liberer lors de la suppression
vg_verbeux=False                        # Mode Verbeux permet un debuggage plus precis / l option -v n affiche pas les parametres en entree
vg_secure=True                          # Mode secure pour eviter des suppressions dans des dossiers system
vg_version=0                            # Mode version idem que le mode vg_time mais en nombre de fichier
vg_history=False                        # Mode history, fonctionne comme un log rotate pour un nom de fichier
vg_compress=False                       # compress le fichier produit pas le mode history
vg_history_suppr=False                  # Si positionne a True le fichier historise est suppr
vg_date_plus_ancienne=False             # Si positionne a True la date de creation de fichier est utilisee
vg_filtre_exclu_dossier=""              # filtre exclusion de dossier dans le cas du mode recursif
vg_del_dossier_vide=False               # suppression des dossiers vides apres la purge
vg_NoTS=False                           # option NO TIMESTAMP
# Variablles globales code retour VTOM
vg_bl = 3
vg_wg = 1
#*****************************************************************************************************************************  #
# Definitions des fonctions locales
#*****************************************************************************************************************************  #

def p_test_options():
        print "Test des arguments passes en entree du script ... "

        if (( vg_input_file and vg_input_directory ) == None )and (vg_param_file==None):
            print "*** un argument est manquant ***"
            p_printusage(vg_bl)

        if (vg_history_suppr==True) and (vg_history == False) :
            print "option --suppr peut etre utilisee seulement avec -H"
            p_print_error("anomalie dans le parametre --suppr", vg_bl)

        if vg_history == True :
            if (vg_time == 0) and (vg_version == 0):
                p_print_error("le mode history doit etre couple a l option -t ou -v",vg_bl)

        if vg_compress == True and vg_history == False :
            p_print_error("l'option -z fonctionne seulement avec le mode H", vg_bl)

        if vg_recursif == True and vg_version <> 0 :
            p_print_error("le mode version -v ne supporte pas la reccursivite -r",vg_bl)

        if vg_recursif == True and vg_history == True :
            p_print_error("le mode version -H ne supporte pas la reccursivite -r",vg_bl)

        if vg_date_plus_ancienne == True and vg_time == 0 :
            p_print_error("l option --date_plus_ancienne fonctionne avec -t",vg_bl)

        if vg_recursif == False and vg_filtre_exclu_dossier <> "" :
            p_print_error("l option -x fonctionne avec -r",vg_bl)

        p_debugg("Les parametres obligatoires sont renseignes")

def p_printusage(err):
#   Affiche le message d utilisation du script
    print r"""
    Usage de la commande :
    purge.py -i input_file -d input_directory -r -e liste_exclusion
    purge.py -p fichier_param

    Les parametres suivants sont obligatoires :
            -i ( nom du fichier, Accepte les REGEX )
            -d ( nom DU repertoire en entree )
        OU
            -p (ce mode annule -i et -d si utilise sur la meme ligne de commande)

    Les parametres optionels sont :
            -r ( recursif )
            -s ( simulation )

            -e ( liste_exclusion de noms de fichiers separee par des , ou ; ) Accepte les REGEX
                Si utilisation du ";", il faut passer l option sur la ligne de commande et non en parametre. BUG VTOM
            -x ( liste_exclusion de noms de dossiers separee par des , ou ; ) Accepte les REGEX
                Si utilisation du ";", il faut passer l option sur la ligne de commande et non en parametre. BUG VTOM

            -D ( suppression des dossiers vides SI et seulement SI des fichiers y ont ete purges )
            -w ( mode de suppr etendu a tous les dossiers )
                A utiliser dans le cas ou les dossiers ne contiennent pas les chaines de caracteres suivantes :
                TEMP, TMP, TRACE, LOG, DONNEE, DUMP, AUDIT, TRANSFERT,
                TRAVAIL, SVDB, EXPORT, IMPORT, DATA, DIAG, SAS, ENVOI, RECU
            -t ( duree en jour : fichiers de plus de x jours )
            --date_plus_ancienne (calcul la date de retention par rapport a la date de creation du fichier)
            -H ( mode history a utiliser avec -v ou -t dans ce cas le filtre pour -v et -t est nom_fichier.TIMESTAMP.old
                il ne tient pas compte de -r et -e)
            -v ( nombre de versions des fichiers) fonctionne seulement avec -i et -d
                cette option est prioritaire sur l'option "-t" 
                ce mode n est pas compatible avec la recursivite
                                les fichiers doivent etre du type TIMESTAMP.nom_fichier*
                                TIMESTAMP est egal a YYYYMMDDHHMMSS
                            OU
                                Utiliser l option -N
            -N ( NO TIMESTAMP, permet de traiter des fichiers dont le nom n est PAS de la forme TIMESTAMP.nom_fichier*
            -z ( compress le fichier dans le cas du mode history)

            --cr3 force le code retour 1 a 3
            --suppr a utilise seulement avec -H permet de supprimer le fichier d origine et ne cree pas l enveloppe

    Sous UNIX / Linux les caracteres speciaux "*", "?", "[", "]" doivent etre precedes par le caractere "\"
    Exemples :
       La REGEX : l5x[at]aa?a.de    doit etre ecrite ainsi : l5x\[at\]aa\?a.de
       La REGEX : file*             doit etre ecrite ainsi : file\*

    -h | --help : produit l'aide suivante
    --debugg    : mode verbose - permet de debugger
    -B | --bouchon=   <code retour>   : bouchon CCO

    """

    sys.exit(err)

def f_param_lg_commande(char_os):
    # Gestion des arguments passes en parametre de la ligne de commandes

    global vg_input_file
    global vg_input_directory
    global vg_filtre_exclu
    global vg_param_file
    global vg_recursif
    global vg_time
    global vg_simulation
    global vg_secure
    global vg_verbeux  # utiliser pour le debuggage
    global vg_BOUCHON
    global vg_code_retour_bouchon
    global vg_version
    global vg_history
    global vg_compress
    global vg_wg
    global vg_history_suppr
    global vg_date_plus_ancienne
    global vg_filtre_exclu_dossier
    global vg_del_dossier_vide
    global vg_NoTS

    nombre_d_element = arguments = None

    ind_i = ind_d = ind_r = ind_p = ind_e = ind_s = ind_t = ind_w = 0

    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:d:t:rp:e:swhB:Hv:zx:DN", ["help","bouchon=","debugg","cr3","suppr","date_plus_ancienne"])

    except getopt.GetoptError, err:
        # print help information and exit:
        # will print something like "option -z not recognized"
        print "!!! ERREUR !!! l option n est pas reconnue : " + str(err)
        p_printusage(vg_bl)

    for o, a in opts:
        p_debugg(str(o) + " " + str(a) )
        if o in ("-h", "--help"):
            p_printusage(vg_bl)
        elif o == ("--debugg"):
            vg_verbeux = True
            p_debugg("mode verbeux actif")
        elif o == ("-i"):
            if ind_i >= 1 :
                p_print_error("Parametre -i en double ...",vg_bl)
            vg_input_file = a
            p_debugg("nom du fichier en entree : " + str(vg_input_file))
            ind_i +=1
        elif o == ("-d"):
            if ind_d >= 1 :
                p_print_error("Parametre -d en double ...",vg_bl)
            vg_input_directory = a
            if vg_input_directory[len(vg_input_directory)-1] == char_os :
                p_debugg("suppression de : " + str(char_os) + " en fin de repertoire")
                vg_input_directory = vg_input_directory.rstrip(char_os)
            p_debugg("nom du repertoire en sortie : " + str(vg_input_directory))
            ind_d +=1
        elif o == ("-D"):
            vg_del_dossier_vide=True
            p_debugg("suppression dossier vide activee...")
        elif o == ("-r"):
            if ind_r >= 1 :
                p_print_error("Parametre -r en double ...",vg_bl)
            vg_recursif = True
            p_debugg("Mode recursif actif")
            ind_r +=1
        elif o == ("-p"):
            if ind_p >=1 :
                p_print_error("Parametre -p en double ...", vg_bl)
            vg_param_file = a
            p_debugg("Nom du fichier de param : " + str(a))
        elif o == ("-t"):
            if ind_t >= 1 :
                p_print_error("Parametre -t en double ...",vg_bl)
            vg_time = int(a)
            p_debugg("mode retention de : " + str(vg_time) + "j actif")
            ind_t +=1
        elif o == ("-e") :
            if ind_e >= 1 :
                p_print_error("Parametre -e en double ...",vg_bl)
            vg_filtre_exclu = a
            p_debugg("filtre d exclusion : " + str(a))
            ind_e +=1
        elif o == ("-x") :
            vg_filtre_exclu_dossier = a
            p_debugg("filtre d exclusion de dossier : " + str(a))
        elif o == ("-s") :
            if ind_s >= 1 :
                p_print_error("Parametre -s en double ...",vg_bl)
            vg_simulation = True
            p_debugg("!!! Mode Simu Actif !!!")
            ind_s +=1
        elif o == ("-w") :
            vg_secure = False
            p_debugg("mode secure desactive")
        elif o in ("-B", "--bouchon"):
            vg_BOUCHON = True
            vg_code_retour_bouchon = int(a)
            p_debugg("Valeur du mode bouchon : " + str(vg_BOUCHON))
            p_print_error("Mode bouchon", vg_code_retour_bouchon)
        elif o == ("-v"):
            vg_version = int(a)
            p_debugg("Mode version actif " + str(vg_version))
            if vg_version == 0 :
                p_print_error("Le nombre de version doit etre superieur > ou = a 1",vg_bl)
        elif o == ("-H"):
            vg_history = True
            p_debugg("Mode History actif " + str(vg_history))
        elif o == ("-z"):
            vg_compress = True
            p_debugg("Mode compression actif " + str(vg_compress))
        elif o == ("-N"):
            vg_NoTS = True
            p_debugg("Mode No TIMESTAMP actif " + str(vg_NoTS))
        elif o == ("--cr3"):
            vg_wg = vg_bl
        elif o == ("--suppr"):
            vg_history_suppr=True
            p_debugg("Mode History SUPPR actif " + str(vg_history_suppr))
        elif o == ("--date_plus_ancienne"):
            vg_date_plus_ancienne=True
            p_debugg("Mode de calcul de la retention sur la date de creation actif")
        else:
            assert False, "option invalide !!!"

    p_test_options() # Verifie les param obligatoires
    return True

def p_debugg(chaine):
    if vg_verbeux : print str(chaine)

def p_print_error(mesg, num):
    # retourne le message d erreur et sort en code retour
    print mesg
    print "Sortie en code retour " + str(num)
    sys.exit(num)


def f_listdirectory(path, filtre, mode_recursif, char_os):
    fichier=[]

    if mode_recursif == "True" : print "mode recursif active"
    chemin_full = path+char_os+"*"

    if os.access(os.path.realpath(path+char_os), os.W_OK) == False :
        print ("Erreur lors de l acces au dossier : "+str(os.path.realpath(path+char_os)))
        p_print_error("",vg_bl)

    l = glob.glob(chemin_full)
    # * - necessaire pour pouvoir lister la totalite en cas de recursivite
    
    # recup la liste des fichiers filtres dans le dossier courant
    chemin_filtre = path+char_os+filtre
    l_filtree = glob.glob(chemin_filtre)
    
    for i in l:
        if os.path.isdir(i):
            if mode_recursif == True :
                fichier.extend(f_listdirectory(i, filtre, mode_recursif, char_os))
        else:
            if i in l_filtree :
                p_debugg("fichier : " + i + " ajoute")
                fichier.append(i)
    return fichier


def f_generation_liste_fichiers_en_entree(input_directory, input_file, mode_recursif, char_os):
    # retourne la liste des fichiers a traiter
    path = input_directory + char_os + input_file
    p_debugg("Recherche des fichiers presents : " + str(path))

    # recup la liste de tous les fichiers
    list_fichiers = f_listdirectory(input_directory ,input_file, mode_recursif, char_os)

    if len(list_fichiers) != 0 :
        return list_fichiers
#    else :
#        p_print_error( "Aucun fichier a traiter", vg_wg)

def f_filtre_exclusion_d_une_liste_de_noms(input_directory, liste_fichiers, liste_filtre_exclu,recursif,char_os):
    # applique le filtre de retention sur les noms de fichiers

    # recopie la liste de fichiers via la librairie copy
    liste_finale = copy.copy(liste_fichiers)

    if liste_filtre_exclu <> "" :
        if ',' in liste_filtre_exclu :
            liste_filtre = liste_filtre_exclu.split(",")
        elif ';' in liste_filtre_exclu :
            liste_filtre = liste_filtre_exclu.split(";")
        else :
            liste_filtre = liste_filtre_exclu.split(";")

        for filtre_exclusion in liste_filtre :
            print "Utilisation du filtre de fichier", filtre_exclusion

            vlf_list_fichiers_filtres = f_generation_liste_fichiers_en_entree(input_directory ,filtre_exclusion, recursif, char_os)
            if vlf_list_fichiers_filtres <> None :
                for ind in vlf_list_fichiers_filtres :
                    if ind in liste_finale :
                        liste_finale.remove(ind)
                        p_debugg( "fichier : " + ind + " ignore")
                    else :
                        p_debugg("le fichier " + str(ind) + " va etre supprime - non concerne par le filtre")

        p_debugg("liste a traiter : " + str(liste_finale))
        return liste_finale

    else :
        return liste_fichiers


def f_filtre_exclusion_d_une_liste_de_noms_de_dossiers(input_directory, liste_fichiers, liste_filtre_exclu_dossier,recursif,char_os):
    # applique le filtre de dossier

    # recopie la liste de fichier via la librairie copy
    vl_liste_finale=copy.copy(liste_fichiers)

    if liste_fichiers <> [] :

        if liste_filtre_exclu_dossier <> "" :
            if ',' in liste_filtre_exclu_dossier :
                liste_filtre = liste_filtre_exclu_dossier.split(",")
            elif ';' in liste_filtre_exclu_dossier :
                liste_filtre = liste_filtre_exclu_dossier.split(";")
            else :
                liste_filtre = liste_filtre_exclu_dossier.split(";")

            for filtre_exclusion in liste_filtre :
                print "Utilisation du filtre de dossier : ", filtre_exclusion
                for fichier in liste_fichiers :
                    directory = os.path.dirname(fichier)
                    chaine = directory[len(input_directory):]
                    if chaine <> "" :
                        vl_regex = f_compile_regex(filtre_exclusion)
                        p_debugg("vl_regex : " + str(vl_regex))
                        rg=re.compile(vl_regex)
                        if rg.findall(chaine) :
                            p_debugg(str(vl_regex)+" trouvee dans : "+chaine)
                            if len(vl_liste_finale) > 0 :
                                # dans le cas ou la liste est deja vide et qu il y a un autre filtre
                                if vl_liste_finale.count(fichier) > 0 :
                                    vl_liste_finale.remove(fichier)
                                    p_debugg( "fichier ignore : " + fichier)

            p_debugg("liste de : " + str(len(vl_liste_finale)) + " fichiers a traiter apres filtre dossier : " + str(vl_liste_finale))
            return vl_liste_finale

        else :
            return liste_fichiers
    else :
        print "Liste de fichier vide pas de filtre de dossier a appliquer"
        return liste_fichiers

def f_verification_fichiers_en_entree(list_fichiers, warning_liste_fichier):

    resultat = True

    # Verifie les attributs des fichiers en entree
    for i in list_fichiers :
        p_debugg("Verification des attributs sur le fichier : " + str(i))
        if not(os.access(i, os.W_OK)):
            print "Attention l option lecture seule sur le fichier : " + str(i) + " est incompatible avec la purge"
            resultat = False
            warning_liste_fichier.append(i)
            list_fichiers.remove(i)
#        else :
#            p_debugg("L option est compatible avec le mode suppression de la source")
    return resultat


def p_verif_existence_dir(dossier): # sort en erreur dans le cas ou le dossier n existe pas
        p_debugg("Verif existence du dossier : " + str(dossier))
        if os.path.exists(dossier) == False :
            p_print_error("Erreur dossier : " + str(dossier) + " absent",vg_bl)
        if os.access(dossier,os.W_OK) == False :
            p_print_error("Erreur de droits (write) sur le dossier : " + str(dossier),vg_bl)
        if os.access(dossier,os.R_OK) == False :
            p_print_error("Erreur de droits (read) sur le dossier : " + str(dossier),vg_bl)

def f_valorisation_var_system(chemin): # permet de valoriser des $ sous unix ou % sous windows
    resultat = os.path.expandvars(chemin)
    p_debugg("Resultat de la valorisation " + str(resultat))
    return resultat

def f_filtre_retention(liste_fic, duree):
    resultat = []
    nb_fic_ignore = 0

    print "Debut du filtre de retention"
    if duree <> 0 : # evite de recalculer a chaque iteration la retention
        date_du_jour = datetime.datetime.now()
        date_retention = date_du_jour - datetime.timedelta(days=duree) # calcul de la retention
        p_debugg( "date limite de retention : " + str( date_retention.ctime() ) ) #.strftime("%Y%m%d%H%M%S)

        for mon_fic in liste_fic :
            # modification pour prise en compte de la date de creation ou creation modification
            if vg_date_plus_ancienne == False :
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
                p_debugg( "date du fichier : "+ str(mon_fic)+ " - "+ str(date_du_fichier))
            else :
                p_debugg("Calcul de la retention sur la date la plus ancienne")
                date_ancienne_fichier = datetime.datetime.fromtimestamp(os.stat(mon_fic).st_atime)
                if date_ancienne_fichier > datetime.datetime.fromtimestamp(os.stat(mon_fic).st_mtime):
                    p_debugg("Permute mtime")
                    date_ancienne_fichier = datetime.datetime.fromtimestamp(os.stat(mon_fic).st_mtime)
                if date_ancienne_fichier > datetime.datetime.fromtimestamp(os.stat(mon_fic).st_ctime):
                    p_debugg("Permute ctime")
                    date_ancienne_fichier = datetime.datetime.fromtimestamp(os.stat(mon_fic).st_ctime)
                date_du_fichier = date_ancienne_fichier
                p_debugg( "date du fichier : "+ str(mon_fic)+ " - "+ str(date_du_fichier))
            if (date_retention > date_du_fichier):
                resultat.append(mon_fic)
                p_debugg( "fichier plus ancien - traitement du fichier : " + str(mon_fic))
            else:
                # p_debugg( "fichier :" + str(mon_fic) + "-" + str(date_du_fichier) + "trop recent - ignore" + str( date_retention.ctime() ))
                p_debugg( "fichier ignore : " + mon_fic+" - "+ str(date_du_fichier)+ " car trop recent")
                nb_fic_ignore += 1
        p_debugg (str(nb_fic_ignore) + " fichiers ignores")
        return resultat
    else :
        p_debugg( "Pas de filtre de traitement de duree ...")
        return liste_fic

def f_filtre_version_history(liste_fichiers, nb_version, char_os):
    # retourne la liste des fichiers de + de nb_version dans le cas du mode history
    p_debugg("f_filtre_version_hitory")

    if vg_version <> 0 :
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
    else :
        return liste_fichiers

def f_filtre_version(liste_fichiers, nb_version, char_os):
    # retourne la liste des fichiers de + de nb_version mode classic
    p_debugg("f_filtre_version")
    if vg_version <> 0 :
        # liste = liste_fichiers
        liste_tempo = []
        liste_final = []
        liste_unique= []


        if len(liste_fichiers) == 1 :
            # dans le cas d un seul fichier dans la liste - aucune difficulte
            return f_filtre_version_history(liste_fichiers, nb_version, char_os)

        for i in liste_fichiers:
            # dans le cas ou il y a une liste de plusieurs noms de fichiers
            nom = os.path.basename(i)[15:] # je retire le chemin
            if nom not in liste_tempo :
                liste_tempo.append(nom) # je conserve le nom du fichier
                p_debugg("ajout du nom de fichier : " + str(nom))

        path = os.path.dirname(liste_fichiers[0])
        for j in liste_tempo :
            if vg_NoTS == True :
            	vl_fitre_recherche = "*"+vg_input_file+"*"
            	#vl_fitre_recherche = "*"+j.rpartition("_")[0]+"_??????-??????*"
            else :
            	vl_fitre_recherche = "??????????????."+j+"*"

            # modifie le filtre de recherche des anciens fichiers
            vl_list_fichiers_a_purger = f_generation_liste_fichiers_en_entree(path ,vl_fitre_recherche, vg_recursif, char_os)
            p_debugg("Liste des fichiers a purger avant filtre : "+ str(vl_list_fichiers_a_purger))
            liste_final.extend(f_filtre_version_history(vl_list_fichiers_a_purger,nb_version,char_os))
            for f in liste_final :
                if f not in liste_unique : liste_unique.append(f)
        return liste_unique
    else :
        # dans le cas ou l option version n est pas active
        return liste_fichiers

def f_suppression(liste_fichiers, mode_simulation):
    global vg_espace_libere
    global vg_warning_suppression_fichier
    global vg_warning_liste_fichier
    global vg_del_dossier_vide

    code_retour = 0
    nb_fichiers_sup = 0

    if mode_simulation == False :
        espace_libere = 0
        for i in liste_fichiers :
            if os.path.islink(i) == False : espace_libere += os.path.getsize(i)
            try :
                print "del : ", i
                os.remove(i)
                nb_fichiers_sup += 1
            except OSError , (errno,strerror):
                print "IMPOSSIBLE DE SUPPRIMER LE FICHIER ... :", str(i)
                #print "OS error (", str(errno), ") : ",str(strerror)
                if errno == 32 and __SYSTEM == "win32" :
				    print "Erreur fichier "+str(i)+" : "+str(strerror)
                else :
                    code_retour = vg_bl
                    espace_libere -= os.path.getsize(i)
                    vg_warning_suppression_fichier +=1
                    vg_warning_liste_fichier.append(i)
            except :
                code_retour = vg_bl
                print "ANOMALIE LORS DE LA SUPPRESSIONS, cause non connue"
            if vg_del_dossier_vide == True and os.listdir(os.path.dirname(i)) == []:
                print "rmdir : ", os.path.dirname(i)
                os.rmdir(os.path.dirname(i))
        print "Espace libere : ", espace_libere, " octets"
        vg_espace_libere +=espace_libere
        print "Nombre de fichier(s) supprime(s) : ", str(nb_fichiers_sup)
    else :
        for i in liste_fichiers :
            print "simu del : ",  i
            nb_fichiers_sup += 1
        print "Nombre de fichier(s) supprime(s) en mode simulation : ", str(nb_fichiers_sup)
    return code_retour

def f_lecture_fichier_param(fichier_entree):
    liste_param = []
    fname = fichier_entree

    try :
        
        file = open(fname,"rb")
        reader = csv.reader(file)
#        for row in reader :
#            print row[0],row[2]
        liste_param.extend(reader)
    except IOError , (errno,strerror):
        print "Ecriture impossible dans le r?pertoire de destination"
        print "I/O error (", str(errno), ") : ",str(strerror)
        if errno == 2 :
            p_print_error("Fichier param absent : " + str(fichier_entree),vg_bl)
        p_print_error("Pb lors de la lecture du fichier de param",vg_bl)
    else :
        file.close()

    print liste_param
    return liste_param


def p_verif_chemin_dangeureux(chemin,secure) :
    Erreur = False
    if secure == True :
        if "TEMP"  in str(string.upper(chemin)) :
            Erreur = True
        if "TMP" in str(string.upper(chemin)) :
            Erreur = True
        if "TRACE" in str(string.upper(chemin)) :
            Erreur = True
        if "LOG" in str(string.upper(chemin)) :
            Erreur = True
        if "DONNEE" in str(string.upper(chemin)) :
            Erreur = True
        if "DUMP" in str(string.upper(chemin)) :
            Erreur = True
        if "AUDIT" in str(string.upper(chemin)) :
            Erreur = True
        if "TRANSFERT" in str(string.upper(chemin)) :
            Erreur = True
        if "TRAVAIL" in str(string.upper(chemin)) :
            Erreur = True
        if "SVDB" in str(string.upper(chemin)) :
            Erreur = True
        if "IMPORT" in str(string.upper(chemin)) :
            Erreur = True
        if "EXPORT" in str(string.upper(chemin)) :
            Erreur = True
        if "DATA" in str(string.upper(chemin)) :
            Erreur = True
        if "DIAG" in str(string.upper(chemin)) :
            Erreur = True
        if "SAS" in str(string.upper(chemin)) :
            Erreur = True
        if "ENVOI" in str(string.upper(chemin)) :
            Erreur = True
        if "RECU" in str(string.upper(chemin)) :
            Erreur = True
        if "BACKUP" in str(string.upper(chemin)) :
            Erreur = True
        if "BKP" in str(string.upper(chemin)) :
            Erreur = True
        if Erreur == False :
            print "Le chemin n est pas un dossier de traces, logs, temps, donnees, dump, audit, travail, transfert, svdb, import, export, data, diag, sas, envoi, recu, backup, bkp. Utiliser l'option -w"
            p_print_error(" ",vg_bl)
            
def p_compress(input):
    # compress un fichier
    if vg_simulation == False :
        try:
            output = input + ".zip"
            if __PYTHON_VERSION > '2.5':
                file = zipfile.ZipFile(output,"w", allowZip64=True)
            else:
                file = zipfile.ZipFile(output,"w")
            print "Compression en cours"
            file.write(input, os.path.basename(input), zipfile.ZIP_DEFLATED)
            file.close()
        except IOError , (errno,strerror):
            print "Ecriture impossible dans le repertoire de destination"
            print "I/O error (", str(errno), ") : ",str(strerror)
            if errno == 28 :
                print "FS Full : Suppresion de la copie"
                if os.path.isfile(output) == True :
                    os.remove(output)
            p_print_error(3)
        except zipfile.LargeZipFile:
            print "Fichier trop gros ... necessite une version 64bits"
            p_print_error(3)
        except :
            print "Erreur lors de la compression"
            p_print_error(3)
    else:
        print "Simu : Compression en cours"
    if vg_verbeux : print "la commande de compression a reussie"

def p_copy(input, output):
    # fonction de copie d un fichier
    p_debugg("p_copy")

    if vg_simulation == False :
        try:
            p_debugg("Debut de la copie :" + str(input) + " - " + str(output))
            copyfile(input,output)
        except IOError , (errno,strerror):
            print "I/O error (", str(errno), ") : ",str(strerror)
            p_print_error("Ecriture impossible dans le r?pertoire de destination",vg_bl)
        except :
            p_print_error("Erreur lors de la copie",vg_bl)
    else :
        print"Simu : ", "Debut de la copie :" + str(input) + " - " + str(output)
    p_debugg("la commande copyfile a reussi")

def f_creation_fichier_vide(input):
    # creer un fichier vide
    code_retour = 0

    p_debugg("f_creation_fichier_vide")

    if vg_simulation == False :
        try :
            fichier = file(input,"w")
            fichier.write('')
            fichier.close
        except :
            code_retour = vg_bl
            print "ANOMALIE LORS DE LA REINITIALISATION DU FICHIER : " + input
            # p_print_error("Erreur lors de la reinitialisation du fichier",vg_bl)
    else :
        print "Simu : reinit du fichier", str(input)
    return code_retour

def f_timestamp_name():
    # retourne un timestamp au format chaine de caractere
    today = datetime.datetime.now()
    return str(today.strftime("%Y%m%d%H%M%S"))

def f_mode_history(vl_input_directory, input_file,  filtre_exclu, duree_retentention, recursif, simulation, secure, char_os):
    #retourne 0 si le traitement s est bien passe

    global vg_version
    global vg_warning_suppression_fichier
    global vg_warning_liste_fichier
    global vg_wg
    global vg_history_suppr

    vl_code_retour = 0
    vl_fitre_recherche = input_file

    print "Debut mode history avec l'option version egale a : " , int (vg_version)


    vl_list_fichiers_entree = f_generation_liste_fichiers_en_entree(vl_input_directory ,vl_fitre_recherche, recursif, char_os)

    if vl_list_fichiers_entree == None :
        p_debugg("Pas de fichier a traiter en mode history ... le filtre n est pas correct")
        return vg_wg

#    Mise EN PLACE DE LA ROTATION POUR PLUSIEURS FICHIERS
#    elif len(vl_list_fichiers_entree)>1 :
#        p_print_error("Le filtre retourne plusieurs noms de fichiers en entree, option non compatible avec -H",vg_bl)
    else :
        for i in vl_list_fichiers_entree :
            print "Debut de recopie du fichier : ", str(i)

            nom_fichier = os.path.basename(i)
            nom_fichier_absolu = i
            directory = os.path.dirname(i)
            fichier_arrivee = nom_fichier + "." + f_timestamp_name() + ".old"
            fichier_arrivee_absolu = directory+char_os+fichier_arrivee

            # procede a la copie du fichier
            p_copy(i,fichier_arrivee_absolu)

            # procede a la compression option -z
            if vg_compress == True and zipfile.is_zipfile(fichier_arrivee_absolu) == False :
                p_compress(fichier_arrivee_absolu)

                # suppression du fichier copie dans le cas de la compression
                liste=[]
                liste.append(fichier_arrivee_absolu)
                f_suppression(liste, simulation)

            # purge du contenu du fichier
            print "Purge du fichier : ", str(i)
            if vg_history_suppr == False :
                cr = f_creation_fichier_vide(nom_fichier_absolu)
                if cr > vl_code_retour :
                    vl_code_retour = cr
            else :
                print("Mode Suppression Actif - Supprime l original")
                liste=[]
                liste.append(i)
                cr = f_suppression(liste,simulation)
                if cr > vl_code_retour :
                    vl_code_retour = cr

            # gestion de la rotation
            vl_fitre_recherche = os.path.basename(i)+".??????????????.old*"
            # modifie le filtre de recherche des anciens fichiers
            vl_list_fichiers_a_purger = f_generation_liste_fichiers_en_entree(vl_input_directory ,vl_fitre_recherche, recursif, char_os)
            p_debugg("Liste des fichiers a purger avant filtre : "+ str(vl_list_fichiers_a_purger))

            if vl_list_fichiers_a_purger == None :
                "La liste des fichiers a purger est vide, les filtres de retention ne seront pas appliques"
            else :

                if vg_version <> 0 :
                    # Traite le cas du nombre de version et annule l'option duree de retention
                    vl_liste_retrait_duree = f_filtre_version_history(vl_list_fichiers_a_purger, vg_version, char_os)
                    p_debugg("liste des fichiers restants a supprimer apres filtre version : " + str(vl_liste_retrait_duree))
                else :
                    # Traite le cas de la retention
                    vl_liste_retrait_duree = f_filtre_retention(vl_list_fichiers_a_purger, duree_retentention)
                    p_debugg("liste des fichiers restants a supprimer apres filtre duree : " + str(vl_liste_retrait_duree))

                if vl_liste_retrait_duree == [] :
                    print("Pas de fichier a purger !!!")
                else :
                    cr = f_suppression(vl_liste_retrait_duree,simulation)
                    if cr > vl_code_retour :
                        vl_code_retour = cr

        return vl_code_retour

def f_enchainement_suppr(input_dir, input_file, filtre_exclu, duree_retentention, recursif, simulation, secure, char_os):

    global vg_warning_suppression_fichier
    global vg_warning_liste_fichier
    global vg_version
#    global simulation

    print "Lancement des enchainements avec les options : ", input_dir, input_file,  filtre_exclu, duree_retentention, recursif, simulation, char_os

    vl_code_retour = 0
    vl_fitre_recherche = input_file
    
    # Valorise les variables d environnement system
    vl_input_directory=f_valorisation_var_system(input_dir)

    # verification de l existence du dossier input
    p_verif_existence_dir(vl_input_directory)

    # verifie si le chemin est "dangereux" ou non
    p_verif_chemin_dangeureux(vl_input_directory, secure)

    # Dans le cas ou l option history n est pas active
    if vg_history == False :

        if vg_version <> 0:
            # dans le cas ou le mode purge version est actif
            if vg_NoTS == True :
            	vl_fitre_recherche = input_file
            else :
                vl_fitre_recherche = "??????????????."+input_file

        vl_list_fichiers_entree = f_generation_liste_fichiers_en_entree(vl_input_directory ,vl_fitre_recherche, recursif, char_os)

        if vl_list_fichiers_entree <> None :
            p_debugg("liste des fichiers a traiter : " + str(vl_list_fichiers_entree))

            # retire de la liste les exclusions
            vl_liste_retrait_exclu = f_filtre_exclusion_d_une_liste_de_noms(vl_input_directory, vl_list_fichiers_entree,filtre_exclu,recursif,char_os)

            # retire de la liste les exclusions de noms de dossier - > utilisation de la variable globale pour le filtre de dossier
            vl_liste_retrait_exclu_dossier = f_filtre_exclusion_d_une_liste_de_noms_de_dossiers(vl_input_directory, vl_liste_retrait_exclu, vg_filtre_exclu_dossier, recursif, char_os)

            p_debugg("liste de " + str(len(vl_liste_retrait_exclu_dossier)) + " fichiers restants apres filtre exclu : "  + str(vl_liste_retrait_exclu_dossier))

            if vg_version <> 0 :
                # Traite le cas du nombre de version et annule l'option duree de retention
                vl_liste_retrait_duree = f_filtre_version(vl_liste_retrait_exclu_dossier, vg_version, char_os)
            else :
                # Traite le cas de la retention
                vl_liste_retrait_duree = f_filtre_retention(vl_liste_retrait_exclu_dossier, duree_retentention)
                p_debugg("liste des fichiers restants apres filtre exclu : " + str(vl_liste_retrait_duree))


            if vl_liste_retrait_duree == [] :
                print("Pas de fichier a purger !!!")
            else :
                cr = f_suppression(vl_liste_retrait_duree,simulation)
                if cr > vl_code_retour :
                    vl_code_retour = cr
        else :
            print("Liste de fichiers vide !!! les options de filtre sont ignorees")

    else :
        # MODE HISTORY
        # passage de vl_input_directory en parametre car la valorisation est faite plus haut
        # Pas de recursivite dans le cas du mode history
        vl_code_retour = f_mode_history(vl_input_directory, input_file,  filtre_exclu, duree_retentention, False, simulation, secure, char_os)

    return vl_code_retour

# change les backshlashs en shlashs
def f_replace_backslashs(chaine_a_modifier):
    chaine = chaine_a_modifier
    if chaine != None:
        chaine = chaine.replace("\\","/")
    if vg_verbeux : print "Debugg ... " + "Modification de la chaine effectuee :" , chaine
    return chaine

def f_compile_regex(regex):
    if vg_verbeux : print "REGEX a traiter : " + regex
    regex=regex.replace('.', '\.')
    regex=regex.replace('?', '.?')
    regex=regex.replace('*', '.*')
    if vg_verbeux : print "REGEX syntaxe python : " + regex
    return regex

#*****************************************************************************************************************************  #
# definition des fonctions par system d exploitation
#*****************************************************************************************************************************  #

def lancement_windows(char_os):

    global vg_input_directory
    global vg_warning_suppression_fichier
    global vg_warning_liste_fichier
    global vg_input_file
    global vg_filtre_exclu
    global vg_simulation
    global vg_espace_libere
    global vg_time
    global vg_recursif
    global vg_param_file
    global vg_secure

    code_retour_fonction = 0

    if vg_param_file <> None :
        liste_param = f_lecture_fichier_param(vg_param_file)
        p_debugg("listes param" + str(liste_param) + str(len(liste_param)))

        if len(liste_param) > 1 :
            for i in range(1,len(liste_param)) :
                vg_input_directory = liste_param[i][0]
                vg_input_file = liste_param[i][1]
                vg_filtre_exclu = liste_param[i][2]
                vg_time = int(liste_param[i][3])
                if liste_param[i][4] == "True" :
                    vg_recursif = True
                else :
                    vg_recursif = False
                if liste_param[i][5] == "True" :
                    vg_secure = True
                else :
                    vg_secure = False
                if liste_param[i][6] == "True" :
                    vg_simulation = True
                else :
                    vg_simulation = False

                cr = f_enchainement_suppr(vg_input_directory, vg_input_file, vg_filtre_exclu, vg_time, vg_recursif, vg_simulation, vg_secure, char_os)
                if cr > code_retour_fonction :
                    code_retour_fonction = cr
                print "Fin du traitement de la ligne numero : ", str(i), str(liste_param[i])
    else :

        cr = f_enchainement_suppr(vg_input_directory, vg_input_file, vg_filtre_exclu, vg_time, vg_recursif, vg_simulation, vg_secure, char_os)
        if cr > code_retour_fonction :
            code_retour_fonction = cr

    print "Fin suppression !!!"
    print "Espace total libere : " + str(vg_espace_libere) + " octets"
    # retourne le code retour de l execution de la commande
    return code_retour_fonction

def lancement_hpux(char_os):
    return lancement_windows(char_os)

def lancement_linux(char_os):
    return lancement_windows(char_os)

#*****************************************************************************************************************************  #
# Main
#*****************************************************************************************************************************  #
if __name__ == "__main__":
    # Variables du programme principal

    # Affiche la version
    print version + "\n"

    # Affiche la ligne de commande
    print "Execution de la commande : "
    print str(sys.argv)

    #*****************************************************************************************************************************  #
    # Lancement de la commande selon la plateforme utilisee
    #*****************************************************************************************************************************  #

    if __SYSTEM == "win32":
            char_os = "\\"
            print "Liste des parametres : "
            if ( f_param_lg_commande(char_os) != True):
                p_print_error("Erreur dans la verification des parametres de la lg de cmd",vg_bl)
            code_retour = lancement_windows(char_os)
    elif __SYSTEM == "hp-ux11":
            char_os = "/"
            print "Liste des parametres : "
            if ( f_param_lg_commande(char_os) != True):
                p_print_error("Erreur dans la verification des parametres de la lg de cmd",vg_bl)
            code_retour = lancement_hpux(char_os)
    elif __SYSTEM == "linux2":
            char_os = "/"
            print "Liste des parametres : "
            if ( f_param_lg_commande(char_os) != True):
                p_print_error("Erreur dans la verification des parametres de la lg de cmd",vg_bl)
            code_retour = lancement_linux(char_os)
    else:
            p_print_error("Plateforme inconnue",vg_bl)


    #######################################
    # Verification du code retour         #
    #######################################
    if code_retour not in (0, None,1,3):
            p_print_error("Erreur inattendue consulter le log",vg_bl)
    if vg_warning_suppression_fichier <> 0 :
            p_print_error("Anomalie au niveau des droits sur : " + str(vg_warning_suppression_fichier) + " fichiers a traiter : " + str(vg_warning_liste_fichier),vg_bl)

    #######################################
    # Fin du Programme avec code_retour   #
    #######################################
    print "Fin du programme - code retour : " + str(code_retour)
    sys.exit(code_retour)



