#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
# 
#****************************    Fiche signaletique shell  encodage: iso-8859-15    ****************************************    #
# Nom du programme : rename_all.py    But du programme : Renomage de fichiers - Version minimum de l'interpreteur python : 2.4
#***********************************************    Syntaxe    **************************************************************   #
# rename_all.py -i input_file -o output_file -p input_directory -c (concervation du fichier original)
#               -a add_suffixe -b add_prefixe -e delete_suffixe -r delete_prefixe
#               -R '<REGEX>' -O '<remplacement>'
#**********************************************    Historique    *************************************************************  #
# Version       Date            AUTEUR          ENTREPRISE      Commentaires
# 1.0           14/04/2015      R.SAVIGNY       GER - PIXON     Creation (a partir du rename.py)
#
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
import string
from shutil import copyfile, move
import datetime
import time
import zipfile
import re


# -------------------------

# Definition des variables systeme
__SYSTEM = sys.platform
__PYTHON_VERSION = sys.version

# Version du CC a completer
version = "rename_all.py v1.0 - python "+__PYTHON_VERSION+" - "+__SYSTEM

# code retour ordo
vg_bl=3
vg_wg=1
vg_ok=0

#*****************************************************************************************************************************  #
# Variables globales
#*****************************************************************************************************************************  #
vg_input_file=None
vg_output_file=None
vg_input_directory=None
vg_add_suffixe=None
vg_add_prefixe=None
vg_delete_suffixe=None
vg_delete_prefixe=None
vg_time=None
vg_suppression=True
vg_secure=True
vg_aaaammjj=False
vg_jjhhmmss=False
vg_verbeux=False # Mode Verbeux permet un debuggage plus precis / l option -v n affiche pas les parametres en entree
vg_force=0
vg_extension=False
vg_regex=None
vg_R=False
vg_replace=None
vg_O=False
vg_UPPER=False
vg_lower=False
vg_recursif=False
#*****************************************************************************************************************************  #
# Definitions des fonctions locales
#*****************************************************************************************************************************  #

def test_options():
        print "Test des arguments passes en entree du script ... "

        if (vg_input_file or vg_input_directory) == None:
                print "*** un argument est manquant ***"
                printusage(vg_bl)
        if (vg_R and not vg_O) or (not vg_R and vg_O) :
                print "Les options -R et -O indissociables"
                printusage(vg_bl)
        if vg_UPPER == True and vg_lower == True :
                print "l'option MAJUSCULE est incompatible avec l'option minuscule"
                printusage(vg_bl)
        if vg_aaaammjj == True and vg_jjhhmmss == True :
                print "l'option aaaammjj ne fonctionne pas en meme temps que jjhhmmss"
                printusage(vg_bl)
        if vg_verbeux :  print ("Les parametres obligatoires sont renseignes")

def printusage(err):
#   Affiche le message d utilisation du script
    print r"""
    Usage de la commande : 
    rename_all.py -i <REGEX ou input_file> -p <input_directory>
            [-o <output_file>] (dans le cas d'un seul fichier)
            [-R '<REGEX>' -O '<remplacement>'] <REGEX> expression reguliere a remplacer, par la chaine de <remplacement>
                                               Gere le multi-fichiers
            [-U] UPPER : passe le nom en MAJUSCULE
            [-L] lower : passe le nom en minuscule
            [-b <add_prefixe>]
            [-a <add_suffixe>]
            [-r <delete_prefixe>]
            [-e <delete_suffixe>]
            [-c] conserve l'original (par defaut le fichier original est supprime)
            [-t <fichiers de + de x jours>] (date de derniere modification)
            [-X] Conserve l'extension dans le(s) nom(s) de fichier(s) lors du traitement
                 Par defaut, le nom et l'extension sont separe, et recolle apres le traitement
            [-w] (desactive le mode secure)
                (A utiliser dans le cas ou les dossiers ne contiennent pas les chaines de caracteres suivantes :
                    TEMP, TMP, TRACE, LOG, DONNEE, DUMP, AUDIT, TRANSFERT,
                    TRAVAIL, SVDB, EXPORT, IMPORT, DATA, DIAG, SAS, ENVOI, RECU
                    BACKUP, BKP)
            [--recursif] (Active le mode recursif lors du traitement de l'input_directory)
            [--aaaammjj] (Modifie le format du TimeStamp par defaut : aaaammjj)
            [--jjhhmmss] (Modifie le format du TimeStamp par defaut : jjhhmmss)

    Les parametres suivants sont obligatoires :
            -i, -p
    
    Les parametres suivants sont indissociables :
            -R, -O
    
    L option -o est possible seulement dans le cas d un fichier a traite
    Elle annule -a -b -e -r et le nom specifie doit etre complet (avec son extension)

    La chaine TIMESTAMP est valorisee dans le cas des options -o -a -b -O
    Par defaut le format est le suivant : AAAAMMDDHHMMSS

    La chaine DATE pointera sur le ctime sous windows et mtime sous UNIX, linux
    Elle est valorisee dans le cas des options -o -a -b -O
    Par defaut le format est le suivant : AAAAMMDDHHMMSS

    Sous UNIX / Linux les caracteres speciaux "*", "?", "[", "]" doivent etre precedes par le caractere "\"
    Exemples :
       La REGEX : l5x[at]aa?a.de    doit etre ecrite ainsi : l5x\[at\]aa\?a.de
       La REGEX : file*             doit etre ecrite ainsi : file\*


    [-h] (produit l'aide suivante)
    [-v] (verbose - permet de debugger)
    [-B | --bouchon] <code_retour> (utilise par le CCO)
    [-f | --force] Force l'ecrasement des fichiers cibles s'ils existent deja
    """

    print_error(err)

def param_lg_commande():
    # Gestion des arguments passes en parametre de la ligne de commandes

    global vg_input_file
    global vg_input_directory
    global vg_output_file
    global vg_add_suffixe
    global vg_add_prefixe
    global vg_delete_suffixe
    global vg_delete_prefixe
    global vg_time
    global vg_secure
    global vg_suppression
    global vg_aaaammjj
    global vg_jjhhmmss
    global vg_verbeux  # utiliser pour le debuggage
    global vg_force
    global vg_extension
    global vg_regex
    global vg_R
    global vg_replace
    global vg_O
    global vg_UPPER
    global vg_lower
    global vg_recursif

    nombre_d_element = arguments = None

    ind_U = ind_L = ind_X = ind_R = ind_O = ind_i = ind_o = ind_p = ind_a = ind_b = ind_e = ind_r = ind_c = ind_t =ind_w = 0
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:o:p:d:a:b:e:r:t:R:O:XcvwhfULB:", ["help","bouchon=","recursif", "aaaammjj","jjhhmmss","force"])

    except getopt.GetoptError, err:
        # print help information and exit:
        # will print something like "option -z not recognized"
        print "!!! ERREUR !!! l option n est pas reconnue : " + str(err)
        printusage(vg_bl)

    for o, a in opts:
        if vg_verbeux : print o, a
        if o in ("-h", "--help"):
            printusage(vg_bl)
        elif o in ("-B", "--bouchon"):
            print "Mode bouchon"
            print_error(int(a))
        elif o in ("-f", "--force"):
            print "Mode force"
            vg_force = 1
        elif o == ("-i"):
            if ind_i >= 1 :
                print "Parametre -i en double ..."
                print_error(vg_bl)
            vg_input_file = a
            if vg_verbeux : print "Nom du fichier en entree : " + str(vg_input_file)
            ind_i +=1
        elif o == ("-o"):
            if ind_o >= 1 :
                print "Parametre -o en double ..."
                print_error(vg_bl)
            vg_output_file = a
            if vg_verbeux : print "Nom du fichier en sortie : " + str(vg_output_file)
            ind_o +=1
        elif o == ("-p"):
            if ind_p >= 1 :
                print "Parametre -p en double ..."
                print_error(vg_bl)
            vg_input_directory = a
            if vg_input_directory[len(vg_input_directory)-1] == os.sep :
                if vg_verbeux : print "Suppression de : " + str(os.sep) + " en fin de repertoire"
                vg_input_directory = vg_input_directory.rstrip(os.sep)
            if vg_verbeux : print "Nom du reperoire en entree : " + str(vg_input_directory)
            ind_p +=1
        elif o == ("-R"):
            if ind_R >= 1 :
                print "Parametre -R en double ..."
                print_error(vg_bl)
            vg_regex = compile_regex(a)
            vg_R = True
            if vg_verbeux : print "REGEX a remplacer : " + str(vg_regex)
            ind_R +=1
        elif o == ("-O"):
            if ind_O >= 1 :
                print "Parametre -O en double ..."
                print_error(vg_bl)
            vg_replace = a
            vg_O = True
            if vg_verbeux : print "Chaine de remplacement : " + str(vg_replace)
            ind_O +=1
        elif o == ("-a"):
            if ind_a >= 1 :
                print "Parametre -a en double ..."
                print_error(vg_bl)
            vg_add_suffixe = a
            if vg_verbeux : print "Ajout du suffixe : " + str(vg_add_suffixe)
            ind_a +=1
        elif o == ("-b"):
            if ind_b >= 1 :
                print "Parametre -b en double ..."
                print_error(vg_bl)
            vg_add_prefixe = a
            if vg_verbeux : print "Ajout du prefixe : " + str(vg_add_prefixe)
            ind_b +=1
        elif o == ("-e"):
            if ind_e >= 1 :
                print "Parametre -e en double ..."
                print_error(vg_bl)
            vg_delete_suffixe = a
            if vg_verbeux : print "Suppression du suffixe : " + str(vg_delete_suffixe)
            ind_e +=1
        elif o == ("-r"):
            if ind_r >= 1 :
                print "Parametre -r en double ..."
                print_error(vg_bl)
            vg_delete_prefixe = a
            if vg_verbeux : print "Suppression du prefixe : " + str(vg_delete_prefixe)
            ind_r +=1
        elif o == ("-t"):
            if ind_t >= 1 :
                print "Parametre -t en double ..."
                print_error(vg_bl)
            vg_time = int(a)
            if vg_verbeux : print "Mode retention de : " + str(vg_time) + "j actif"
            ind_t +=1
        elif o == ("-X"):
            if ind_X >= 1 :
                print "Parametre -X en double ..."
                print_error(vg_bl)
            vg_extension = True
            if vg_verbeux : print "Preservation de l'extension actif"
            ind_X +=1
        elif o == ("-U"):
            if ind_U >= 1 :
                print "Parametre -U en double ..."
                print_error(vg_bl)
            vg_UPPER = True
            if vg_verbeux : print "Mode MAJUSCULE actif"
            ind_U +=1
        elif o == ("-L"):
            if ind_L >= 1 :
                print "Parametre -L en double ..."
                print_error(vg_bl)
            vg_lower = True
            if vg_verbeux : print "Mode minuscule actif"
            ind_U +=1
        elif o == ("-w"):
            if ind_w >= 1 :
                print "Parametre -w en double ..."
                print_error(vg_bl)
            vg_secure = False
            if vg_verbeux : print "Mode secure actif"
            ind_w +=1
        elif o == ("-c"):
            if ind_c >= 1 :
                print "Parametre -c en double ..."
                print_error(vg_bl)
            vg_suppression = False
            if vg_verbeux : print "Mode conservation de l'original active"
            ind_c +=1
        elif o in ("--recursif"):
            print "Mode recursif actif"
            vg_recursif = True
        elif o == ("--aaaammjj"):
            vg_aaaammjj=True
            if vg_verbeux : print "Mode aaaammjj actif"
        elif o == ("--jjhhmmss"):
            vg_jjhhmmss=True
            if vg_verbeux : print "Mode jjhhmmss actif"
        elif o == ("-v"):
            vg_verbeux = True
            if vg_verbeux : print "Mode verbeux actif"
        else:
            assert False, "Option invalide !!!"
    test_options() # Verifie les param obligatoires
    return True


def timestamp_name():
    # retourne un timestamp au format chaine de caractere
    # ajout des option de format de timestamp
    today = datetime.datetime.now()
    resultat = str(today.strftime("%Y%m%d%H%M%S"))
    if vg_jjhhmmss == True :
        resultat = str(today.strftime("%d%H%M%S"))
    if vg_aaaammjj == True :
        resultat = str(today.strftime("%Y%m%d"))
    return resultat

def print_error(num):
    # retourne le message d erreur et sort en code retour
    print "Sortie en code retour " + str(num)
    sys.exit(num)

def compile_regex(regex):
    if vg_verbeux : print "REGEX a traiter : " + regex
    regex=regex.replace('.', '\.')
    regex=regex.replace('?', '.?')
    regex=regex.replace('*', '.*')
    if vg_verbeux : print "REGEX syntaxe python : " + regex
    if vg_verbeux : print "Chaine de remplacement : " + vg_replace
    return regex

def listdirectory_full(path, filtre, vg_recursif):
    # lit les fichiers dans un dossier avec un filtre
    l_fichiers=[] # liste retournee
    l_files_filtre = glob.glob(path+os.sep+filtre)
    if vg_verbeux : print "Liste filtre : " + str(l_files_filtre)
    l_files_full = glob.glob(path+os.sep+"*")
    if vg_verbeux : print "Liste full : " + str(l_files_full)
    for i in l_files_full:
        if os.path.isdir(i):
            if vg_verbeux : print "Chemin isdir : "+i
            if vg_recursif == True :
                extend=listdirectory_full(i, filtre, vg_recursif)
                l_fichiers.extend(extend)
        else:
            if i in l_files_filtre :
                if vg_verbeux : print("Fichier : " + i + " ajoute")
                l_fichiers.append(i)
    if vg_verbeux : print "Liste full des fichiers : " + str(l_fichiers)
    return l_fichiers

def listdirectory(l_files_full):
    fichiers=[] # liste retournee
    if vg_time <> None : # evite de recalculer a chaque iteration la retention
        if (vg_output_file<> None): # cas de l'option -o valoriser dans le cas de la retention
            print "L'option -o n est pas compatible avec la gestion de retention"
            print_error(vg_bl)
        date_du_jour = datetime.datetime.now()
        date_retention = date_du_jour - datetime.timedelta(days=vg_time) # calcul de la retention
        if vg_verbeux : print "Date limite de retention : " , date_retention.ctime() #.strftime("%Y%m%d%H%M%S)

    for mon_fic in l_files_full:
        if vg_verbeux : print "test si fichier existe : " , mon_fic
        if os.path.isfile(mon_fic) == True :
            if vg_time <> None : # gestion de la retention de fichier
                if __SYSTEM == "win32": # cas windows on calcule la date sur la creation et la modification
                    date_derniere_modif_fichier = datetime.datetime.fromtimestamp(os.stat(mon_fic).st_mtime)
                    date_creation_fichier = datetime.datetime.fromtimestamp(os.stat(mon_fic).st_ctime)
                    if date_creation_fichier > date_derniere_modif_fichier :
                        if vg_verbeux : print "warning date de creation plus recente que la date de modification - date de creation utilise"
                        date_du_fichier = date_creation_fichier
                    else :
                        date_du_fichier = date_derniere_modif_fichier
                else : # cas unix/linux on calcule la date sur la modification
                    date_du_fichier = datetime.datetime.fromtimestamp(os.stat(mon_fic).st_mtime)
                if vg_verbeux : print "date du fichier : " , mon_fic, "-", str(date_du_fichier)
                if (date_retention > date_du_fichier):
                    fichiers.append(mon_fic)
                    if vg_verbeux : print "fichier plus ancien - ajout du fichier : " , str(mon_fic)
                else:
                    if vg_verbeux : print "fichier :" , mon_fic,"-", str(date_du_fichier), "trop recent - ignore" , date_retention.ctime()
                    print "fichier ignore : " , mon_fic,"-", str(date_du_fichier), "car trop recent"
            else :
                fichiers.append(mon_fic)
                if vg_verbeux : print "ajout du fichier : " , str(mon_fic)
        else:
            if vg_verbeux : print mon_fic, " n est pas un fichier"
    return fichiers

def gestion_timestamp():
    # Valorise la chaine TIMESTAMP si présente dans la chaine
    global vg_add_suffixe
    global vg_add_prefixe
    global vg_output_file
    global vg_time

    print "Recherche de la chaine TIMESTAMP dans les prefixes et suffixes"
    
    if vg_add_suffixe <> None :
        if vg_verbeux :  print "traitemenent de la variable TIMESTAMP dans le suffixe"
        while "TIMESTAMP" in vg_add_suffixe :
            vg_add_suffixe = vg_add_suffixe.replace("TIMESTAMP", timestamp_name())
    if vg_add_prefixe <> None :
        if vg_verbeux :  print "traitemenent de la variable TIMESTAMP dans le prefixe"
        while "TIMESTAMP" in vg_add_prefixe :
            vg_add_prefixe = vg_add_prefixe.replace("TIMESTAMP", timestamp_name())
    if vg_output_file <> None :
        if vg_verbeux :  print "traitemenent de la variable TIMESTAMP dans le outputfile"
        while "TIMESTAMP" in vg_output_file :
            vg_output_file = vg_output_file.replace("TIMESTAMP", timestamp_name())

def calcul_date(fichier):
    # Valorise la chaine DATE si présente dans la chaine
    print "Calcul et traitement de la date de creation du fichier"
    if __SYSTEM == "win32":
        f_date=time.ctime(os.path.getctime(fichier))
    else:
        f_date=time.ctime(os.path.getmtime(fichier))
    t_struct = time.strptime(f_date, "%a %b %d %H:%M:%S %Y")
    format_date="%Y%m%d%H%M%S"
    if vg_jjhhmmss == True :
        format_date = "%d%H%M%S"
    f_date_format=time.strftime(format_date, t_struct)
    return f_date_format

def generation_liste_fichiers_en_entree():
    # retourne la liste des fichiers a traiter
    path = vg_input_directory + os.sep + vg_input_file
    print "Recherche des fichiers presents : " + str(path)
    list_full_fichiers = listdirectory_full(vg_input_directory, vg_input_file, vg_recursif)
    list_fichiers = listdirectory(list_full_fichiers)
    if len(list_fichiers) !=0 :
        return list_fichiers
    else :
        print "Aucun fichier a traiter"
        print "Sortie en code warning 1"
        sys.exit(vg_wg)

def verification_fichiers_en_entree(vg_input_directory, list_fichiers):
    # Verifie les attributs des fichiers en entree
    try :
        os.chdir(os.path.realpath(vg_input_directory+os.sep))
    except OSError:
        print ("Erreur lors de l acces au dossier : "+str(os.path.realpath(vg_input_directory+os.sep)))
        print_error(vg_bl)

    for i in list_fichiers :
        if vg_verbeux :  print "Verification des attributs sur le fichier : " + str(i)
        
        if os.access(i, os.R_OK):
            if vg_verbeux : print "Le fichier peut-etre lu"
        else :
            print "Le fichier : " + str(i) + " ne peut etre lu - verifier les droits"
            print_error(vg_bl)
        if not(os.access(i, os.W_OK)) and vg_suppression :
            print "Attention l option lecture seule sur le fichier : " + str(i) + " est incompatible avec le mode suppression"
            print_error(vg_bl)
        else :
            if vg_verbeux : print "L option est compatible avec le mode suppression de la source"
    return True

def constitution_liste_fichiers_export(list_fichiers_entree):
    global vg_add_suffixe
    global vg_add_prefixe
    global vg_delete_prefixe
    global vg_delete_suffixe
    global vg_extension
    global vg_regex
    global vg_replace
    global vg_UPPER
    global vg_lower

    list_fichiers_sortie=[]

    print "Preparation des fichiers en sortie"
    for i in list_fichiers_entree :
        if vg_verbeux : print "\nTraitement du fichier : " + str(i)
        # recupere le chemin du fichier a traiter
        che_fic = str(os.path.dirname(i))
        # recupere le nom du fichier a traiter sans le chemin
        if vg_extension == True :
            nom_fic = str(os.path.basename(i))
        else :
            fichier = str(os.path.basename(i)).rsplit('.',1)
            nom_fic = fichier[0]
            ext_fic = fichier[1]

        if vg_verbeux : print "Nom fichier : " + nom_fic, str(len(nom_fic)) + " caracteres"

        if vg_output_file <> None : #gere le cas d un nouveau nom
            if vg_verbeux : print "Mode nouveau nom..."
            if vg_verbeux : print "Desactivation des suffixes et prefixe"
            vg_delete_prefixe = None
            vg_delete_suffixe = None
            vg_add_suffixe = None
            vg_add_prefixe = None
            # dans le cas d un filtre nom.* ou nom.txt supprime la partie a droite du point
            if len(list_fichiers_entree) == 1 :
                fichier_out = str(vg_output_file).rsplit('.',1)
                nom_fic = fichier_out[0]
                ext_fic = fichier_out[1]
                if vg_verbeux : print "Changement du nom de fichier en sortie option -o : " + nom_fic
            else :
                print "Plus d un fichier a traiter !!! option -o incompatible"
                print_error(vg_bl)

        if (vg_R and vg_O) : #REGEX a remplacer par un masque de substitution
            if vg_verbeux : print "Mode REGEX replace..."
            if vg_verbeux : print "REGEX : " + vg_regex
            rg=re.compile(vg_regex)
            a_remplacer=rg.findall(nom_fic)
            if vg_verbeux : print "A remplacer : " + ', '.join(a_remplacer)
            if not a_remplacer : print "REGEX non trouvee dans le nom du fichier, il garde son nom d origine"
            nom_fic=rg.sub(vg_replace, nom_fic)
            if vg_verbeux : print "nom_fichier remplacer : " + nom_fic

        if vg_delete_prefixe <> None : #suppr le prefixe
            if vg_verbeux : print "Mode supprime prefixe..."
            if nom_fic.startswith(vg_delete_prefixe):
                nom_fic = nom_fic[len(vg_delete_prefixe):]
                if vg_verbeux : print "Suppression du prefixe : " + nom_fic
            else :
                print "Erreur le filtre de prefixe n'est pas correct - prefixe absent du nom de fichier"
                print_error(vg_bl)
            if len(nom_fic) == 0 :
                print "Erreur le fichier resultat ne porte plus de nom apres la suppression du prefixe"
                print_error(vg_bl)

        if vg_delete_suffixe <> None : #suppr le suffixe
            if vg_verbeux : print "Mode supprime suffixe..."
            if nom_fic.endswith(vg_delete_suffixe):
                nom_fic = nom_fic.rstrip(vg_delete_suffixe)
                if vg_verbeux : print "Suppression du suffixe : " + nom_fic
            else :
                print "Erreur le filtre de suffixe n'est pas correct - suffixe absent du nom de fichier"
                print_error(vg_bl)
            if len(nom_fic) == 0 :
                print "Erreur le fichier resultat ne porte plus de nom apres la suppression du suffixe"
                print_error(vg_bl)

        if vg_add_suffixe <> None : #ajout d un suffixe
            if vg_verbeux : print "Mode ajout suffixe..."
            if vg_verbeux : print "Traitemenent de la chaine DATE dans le suffixe"
            vl_add_suffixe=vg_add_suffixe
            while "DATE" in vl_add_suffixe :
                vl_add_suffixe = vg_add_suffixe.replace("DATE", calcul_date(i))
            nom_fic = nom_fic + vl_add_suffixe
            if vg_verbeux : print "Ajout du suffixe : " + nom_fic

        if vg_add_prefixe <> None : # ajout d un prefixe
            if vg_verbeux : print "Mode ajout prefixe..."
            if vg_verbeux : print "traitemenent de la chaine DATE dans le prefixe"
            vl_add_prefixe=vg_add_prefixe
            while "DATE" in vl_add_prefixe :
                vl_add_prefixe = vg_add_prefixe.replace("DATE", calcul_date(i))
            nom_fic = vl_add_prefixe + nom_fic
            if vg_verbeux : print "Ajout du prefixe : " + nom_fic

        if vg_UPPER : 
            nom_fic = nom_fic.upper()
            if vg_verbeux : print "Mode UPPER..."
        if vg_lower :
            nom_fic = nom_fic.lower()
            if vg_verbeux : print "Mode lower..."

        if vg_extension == False : # reconstruit le nom du fichier
            if vg_verbeux : print "Reconstruction nom + extension : " + nom_fic + " + " + ext_fic
            nom_final = nom_fic + "." + ext_fic
        else :
            nom_final = nom_fic

        if vg_verbeux : print "Resultat du traitement du nom de fichier : " + nom_final
        nom_final=che_fic+os.sep+nom_final
        list_fichiers_sortie.append(str(nom_final))

    return list_fichiers_sortie

def fonction_rename(input, output):
    try :
        move(input, output)
    except :
        print "Erreur lors du rename"
        print_error(vg_bl)
    if vg_verbeux : print "la commande rename a reussie"

def fonction_copy(input, output):
    try:
        copyfile(input,output)
    except IOError , (errno,strerror):
        print "Ecriture impossible dans le répertoire de destination"
        print "I/O error (", str(errno), ") : ",str(strerror)
        if errno == 28 :
            print "FS Full : Suppresion de la copie"
            if os.path.isfile(output) == True :
                os.remove(output)
        print_error(vg_bl)
    except :
        print "Erreur lors de la copie"
        print_error(vg_bl)
    if vg_verbeux : print "la commande copyfile a reussie"

def verif_existence_fichier(fichier): # sort en erreur dans le cas ou le fichier existe ou un dossier du meme temps
        if vg_verbeux : print "Verif existence du fichier : " + str(fichier)
        if os.path.isfile(fichier) == True and vg_force != 1 :
            print "Erreur fichier : " + str(fichier) + " deja present"
            print_error(vg_bl)
        if os.path.isdir(fichier) == True :
            print "Erreur un dossier porte deja ce nom : "+ str(fichier)
            print_error(vg_bl)
        if os.path.islink(fichier) == True :
            print "Erreur un lien symbolique porte deja ce nom : "+ str(fichier)
            print_error(vg_bl)

def verif_existence_dir(dossier): # sort en erreur dans le cas ou le dossier n existe pas
        if vg_verbeux : print "Verif existence du dossier : " + str(dossier)
        if os.path.exists(dossier) == False :
            print "Erreur dossier : " + str(dossier) + " absent"
            print_error(vg_bl)
        if os.access(dossier,os.R_OK) == False :
            print "Erreur de droits !!! le dossier ne peut-etre lu : " + str(dossier)
            print_error(vg_bl)

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
            print_error(vg_bl)

def execute_rename(list_in, list_out):
    print "Debut d execution du renomage"

    if len(list_in) <> len(list_out) :
        print "Erreur lors de la constitution des listes de fichiers"
        print "Le nombre de fichiers en entree et en sortie est different"
        print_error(vg_bl)

    if vg_output_file <> None :
        print "Traitement du fichier"
        if len(list_out) == 1 :
            input = list_in[0]
            output = list_out[0]
            verif_existence_fichier(output) # verifie l existence du fichier avant traitement
            if vg_suppression:
                fonction_rename(input,output)
                print "Rename du fichier : " + str(input) + " vers : " + str(output) + " reussie"
            else:
                fonction_copy(input,output)
                print "Copie du fichier : " + str(input) + " vers : " + str(output) + " reussie"
        else :
            print "Plus d un fichier a traiter !!! option -o imcompatible"
            print_error(vg_bl)
    else :
        print "Traitement des : ", str(len(list_out)), " fichiers"
        for i in range(len(list_out)) :
            input = list_in[i]
            output = list_out[i]
            verif_existence_fichier(output) # cas d un fichier portant le meme nom en sortie
            if vg_suppression:
                fonction_rename(input,output)
                print "Rename du fichier : " + str(input) + " vers : " + str(output) + " reussie"
            else:
                fonction_copy(input,output)
                print "Copie du fichier : " + str(input) + " vers : " + str(output) + " reussie"
    print "Traitement des : ", str(len(list_out)), " fichiers termine"
    return True

def valorisation_var_system(chemin): # permet de valoriser des $ sous unix ou % sous windows
    resultat = os.path.expandvars(chemin)
    if vg_verbeux : print "Resultat de la valorisation " + str(resultat)
    return resultat


#*****************************************************************************************************************************  #
# definition des fonctions par system d exploitation
#*****************************************************************************************************************************  #

def lancement_windows():

    global vg_input_directory

    # Valorise les variables d environnement system
    vg_input_directory=valorisation_var_system(vg_input_directory)

    # verification de l existence des dossiers input et output
    verif_existence_dir(vg_input_directory)
    p_verif_chemin_dangeureux(vg_input_directory,vg_secure)

    # fabrique la liste des fichiers a traiter
    list_fichiers_entree = generation_liste_fichiers_en_entree()

    if vg_verbeux : print "liste des fichiers a traiter : " + str(list_fichiers_entree)
    resultat = verification_fichiers_en_entree(vg_input_directory, list_fichiers_entree)

    if resultat <> True :
        print "Erreur lors de la verification des parametres sur les fichiers d entree"
        print_error(vg_bl)

    # verification de l option TIMESTAMP dans les options add suffixe et add prefixe
    gestion_timestamp()

    # fabrique la liste des fichiers en sortie
    list_fichiers_sortie = constitution_liste_fichiers_export(list_fichiers_entree)

    # execute le rename
    if (execute_rename(list_fichiers_entree, list_fichiers_sortie) == True):
        code_retour_fonction = 0

    # retourne le code retour de l execution de la commande
    return code_retour_fonction

def lancement_hpux():
    return lancement_windows()

def lancement_solaris():
    return lancement_windows()

def lancement_linux():
    return lancement_windows()

#*****************************************************************************************************************************  #
# Main
#*****************************************************************************************************************************  #
if __name__ == "__main__":
    # Variables du programme principal
    
    # Affiche la version
    print version + "\n"
    
    # Affiche la commande lancee
    print "Execution de la commande : " + str(sys.argv)

    #*****************************************************************************************************************************  #
    # Lancement de la commande selon la plateforme utilisee
    #*****************************************************************************************************************************  #

    if __SYSTEM == "win32":
            print "Liste des parametres : "
            if (param_lg_commande() != True):
                print_error(vg_bl)
            code_retour = lancement_windows()
    elif __SYSTEM == "hp-ux11":
            print "Liste des parametres : "
            if (param_lg_commande() != True):
                print_error(vg_bl)
            code_retour = lancement_hpux()
    elif __SYSTEM == "linux2":
            print "Liste des parametres : "
            if (param_lg_commande() != True):
                print_error(vg_bl)
            code_retour = lancement_linux()
    elif __SYSTEM == "solaris":
            print "Liste des parametres : "
            if (param_lg_commande() != True):
                print_error(vg_bl)
            code_retour = lancement_solaris()
    else:
            print "Plateforme inconnue - sortie en CR 3"
            print_error(vg_bl)


    #######################################
    # Verification du code retour         #
    #######################################
    if code_retour not in (0, None):
            print "ping: Erreur inattendue - sortie en CR 3"
            print_error(vg_bl)

    #######################################
    # Fin du Programme avec code_retour   #
    #######################################
    print "Fin du programme - code retour : " + str(code_retour)
    sys.exit(code_retour)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
