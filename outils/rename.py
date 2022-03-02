#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
# 
#****************************    Fiche signaletique shell  encodage: iso-8859-15    ****************************************    #
# Nom du programme : rename.py    But du programme : Renomage de fichiers - Version minimum de l'interpreteur python : 2.4
#***********************************************    Syntaxe    **************************************************************   #
# rename.py -i input_file -o output_file -d input_directory -p output_directory -s (suppression) -c (copy / option par defaut)
#            -a add_suffixe -b add_prefixe -e delete_suffixe -r delete_prefixe
#**********************************************    Historique    *************************************************************  #
# Version       Date            AUTEUR          ENTREPRISE      Commentaires
# 2.0           10/06/2011      C.CHAPUT        La Poste        Creation
# 2.1           04/07/2011      C.CHAPUT        La Poste        Ajout compression, gestion extension suite anomalie mineure
# 2.2           05/07/2011      C.CHAPUT        La Poste        Modification du message d aide suite a anomalie mineure
# 2.3           07/07/2011      C.CHAPUT        La Poste        Modification dans le cas d'un FS deja FULL
# 2.4           07/07/2011      C.CHAPUT        La Poste        Sortie en code retour 3 dans le cas d un dossier portant portant le 
#                                                               nom du fichier de sortie - idem pour un lien symbolique
# 2.5           28/11/2011      C.CHAPUT        La Poste        Ajout d une securite sur le nom des dossier option -w et gestion de la date
# 2.6           26/04/2012      C.CHAPUT / CCO  La Poste        Modification du fonctionnement de l'option -o suite à une anomalie
#                                                               Ajout de l'option bouchon dans la ligne de commande
# 2.7           19/06/2013      C.CHAPUT        La Poste        Ajout de 2 options pour le format de Timestamp --aaaammjj et --jjhhmmss
# 2.8           03/10/2013      C.CHAPUT        La Poste        Gestion d erreur dans un cas de pb de droits
# 2.9           24/12/2013      C.CHAPUT        La Poste        Ajout du dossier backup et bkp pour l option -w
# 3.0           16/01/2013      C.CHAPUT        La Poste        Calcul de la retention -t sur le mtime pour linux unix
# 3.1           12/01/2015      R.SAVIGNY       PIXON           Ajout option [-f|--force] Force l'ecrasement des fichiers cibles s'ils existent deja
# 3.2           12/08/2015      R.SAVIGNY       PIXON           I08079305  : Prise en compte fichier deja compresse (non pertinent)
#                                                               Detail de l'utilisation des caracteres speciaux sous unix/linux
# 3.3           17/05/2016      R.SAVIGNY       PIXON           Ajout traitement exception OSError pour la fonction shutil.move()
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

# -------------------------

# Definition des variables systeme
__SYSTEM = sys.platform
__PYTHON_VERSION = sys.version

# Version du CC a completer
version = "rename.py v3.2 - python "+__PYTHON_VERSION+" - "+__SYSTEM

# code retour ordo
vg_bl=3
vg_wg=1

#*****************************************************************************************************************************  #
# Variables globales
#*****************************************************************************************************************************  #
vg_input_file=None
vg_output_file=None
vg_input_directory=None
vg_output_directory=None
vg_suppression=True
vg_copy=False
vg_add_suffixe=None
vg_add_prefixe=None
vg_delete_suffixe=None
vg_delete_prefixe=None
vg_time=None
vg_zipfile=False
vg_secure=True
vg_aaaammjj=False
vg_jjhhmmss=False
vg_verbeux=False # Mode Verbeux permet un debuggage plus precis / l option -v n affiche pas les parametres en entree
vg_force=0
#*****************************************************************************************************************************  #
# Definitions des fonctions locales
#*****************************************************************************************************************************  #

def test_options():
        print "Test des arguments passes en entree du script ... "

        if ( vg_input_file and vg_input_directory and vg_output_directory) == None:
                print "*** un argument est manquant ***"
                printusage(vg_bl)
        if vg_aaaammjj == True and vg_jjhhmmss == True :
                print "l'option aaaammjj ne fonctionne pas en meme temps que jjhhmmss"
                printusage(vg_bl)
        if vg_verbeux :  print ("Les parametres obligatoires sont renseignes")

def printusage(err):
#   Affiche le message d utilisation du script
    print r"""
    Usage de la commande : 
    rename.py -i <input_file> -p <input_directory> -d <output_directory>
            [-o <output_file>] (dans le cas d un seul fichier)
            [-c] (ne supprime pas l original)
            [-a <add_suffixe>]
            [-b <add_prefixe>]
            [-e <delete_suffixe>]
            [-r <delete_prefixe>]
            [-t <fichiers de + de x jours>] (date de derniere modification)
            [-z] (mode compression)
            [-w] (desactive le mode secure)
                (A utiliser dans le cas ou les dossiers ne contiennent pas les chaines de caracteres suivantes :
                    TEMP, TMP, TRACE, LOG, DONNEE, DUMP, AUDIT, TRANSFERT,
                    TRAVAIL, SVDB, EXPORT, IMPORT, DATA, DIAG, SAS, ENVOI, RECU)
            [--aaaammjj] (Modifie le format du TimeStamp par defaut : aaaammjj)
            [--jjhhmmss] (Modifie le format du TimeStamp par defaut : jjhhmmss)

    Les parametres suivants sont obligatoires :
            -i, -p, -d
    
    L option -o est possible seulement dans le cas d un fichier a traite
    Elle annule -a -b -e -r et le nom specifie doit etre complet (avec son extension)

    La chaine TIMESTAMP est valorisee dans le cas des options -o -a -b -z
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

def param_lg_commande(char_os):
    # Gestion des arguments passes en parametre de la ligne de commandes

    global vg_input_file
    global vg_output_file
    global vg_input_directory
    global vg_output_directory
    global vg_suppression
    global vg_copy
    global vg_add_suffixe
    global vg_add_prefixe
    global vg_delete_suffixe
    global vg_delete_prefixe
    global vg_time
    global vg_zipfile
    global vg_secure
    global vg_aaaammjj
    global vg_jjhhmmss
    global vg_verbeux  # utiliser pour le debuggage
    global vg_force

    nombre_d_element = arguments = None

    ind_i = ind_o = ind_p = ind_d = ind_c = ind_a = ind_b = ind_e = ind_r = ind_t = ind_z =ind_w = 0
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:o:p:d:a:b:e:r:t:vzwhcfB:", ["help","bouchon=","aaaammjj","jjhhmmss","force"])

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
            print "mode bouchon"
            print_error(int(a))
        elif o in ("-f", "--force"):
            print "mode force"
            vg_force = 1
        elif o == ("-i"):
            if ind_i >= 1 :
                print "Parametre -i en double ..."
                print_error(vg_bl)
            vg_input_file = a
            if vg_verbeux : print "nom du fichier en entree : " + str(vg_input_file)
            ind_i +=1
        elif o == ("-o"):
            if ind_o >= 1 :
                print "Parametre -o en double ..."
                print_error(vg_bl)
            vg_output_file = a
            if vg_verbeux : print "nom du fichier en sortie : " + str(vg_output_file)
            ind_o +=1
        elif o == ("-p"):
            if ind_p >= 1 :
                print "Parametre -p en double ..."
                print_error(vg_bl)
            vg_input_directory = a
            if vg_input_directory[len(vg_input_directory)-1] == char_os :
                if vg_verbeux : print "suppression de : " + str(char_os) + " en fin de repertoire"
                vg_input_directory = vg_input_directory.rstrip(char_os)
            if vg_verbeux : print "nom du reperoire en entree : " + str(vg_input_directory)
            ind_p +=1
        elif o == ("-d"):
            if ind_d >= 1 :
                print "Parametre -d en double ..."
                print_error(vg_bl)
            vg_output_directory = a
            if vg_output_directory[len(vg_output_directory)-1] == char_os :
                if vg_verbeux : print "suppression de : " + str(char_os) + " en fin de repertoire"
                vg_output_directory = vg_output_directory.rstrip(char_os)
            if vg_verbeux : print "nom du repertoire en sortie : " + str(vg_output_directory)
            ind_d +=1
        elif o == ("-c"):
            if ind_c >= 1 :
                print "Parametre -c en double ..."
                print_error(vg_bl)
            vg_suppression = False
            vg_copy = True
            if vg_verbeux : print "mode copie actif"
            ind_c +=1
        elif o == ("-a"):
            if ind_a >= 1 :
                print "Parametre -a en double ..."
                print_error(vg_bl)
            vg_add_suffixe = a
            if vg_verbeux : print "ajout du suffixe : " + str(vg_add_suffixe)
            ind_a +=1
        elif o == ("-b"):
            if ind_b >= 1 :
                print "Parametre -b en double ..."
                print_error(vg_bl)
            vg_add_prefixe = a
            if vg_verbeux : print "ajout du prefixe : " + str(vg_add_prefixe)
            ind_b +=1
        elif o == ("-e"):
            if ind_e >= 1 :
                print "Parametre -e en double ..."
                print_error(vg_bl)
            vg_delete_suffixe = a
            if vg_verbeux : print "suppression du suffixe : " + str(vg_delete_suffixe)
            ind_e +=1
        elif o == ("-r"):
            if ind_r >= 1 :
                print "Parametre -r en double ..."
                print_error(vg_bl)
            vg_delete_prefixe = a
            if vg_verbeux : print "suppression du prefixe : " + str(vg_delete_prefixe)
            ind_r +=1
        elif o == ("-t"):
            if ind_t >= 1 :
                print "Parametre -t en double ..."
                print_error(vg_bl)
            vg_time = int(a)
            if vg_verbeux : print "mode retention de : " + str(vg_time) + "j actif"
            ind_t +=1
        elif o == ("-z"):
            if ind_z >= 1 :
                print "Parametre -z en double ..."
                print_error(vg_bl)
            vg_zipfile = True
            if vg_verbeux : print "mode compress actif"
            ind_z +=1
        elif o == ("-w"):
            if ind_w >= 1 :
                print "Parametre -w en double ..."
                print_error(vg_bl)
            vg_secure = False
        elif o == ("--aaaammjj"):
            vg_aaaammjj=True
            if vg_verbeux : print "mode aaaammjj actif"
        elif o == ("--jjhhmmss"):
            vg_jjhhmmss=True
            if vg_verbeux : print "mode jjhhmmss actif"
        elif o == ("-v"):
            vg_verbeux = True
            if vg_verbeux : print "mode verbeux actif"
        else:
            assert False, "option invalide !!!"

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

def listdirectory(path, filtre, char_os):
    # lit les fichiers dans un dossier avec un filte
    fichier=[] # liste retournee
  
    try :
        os.chdir(os.path.realpath(path+char_os))
    except OSError:
        print ("Erreur lors de l acces au dossier : "+str(os.path.realpath(path+char_os)))
        print_error(vg_bl)
    l = glob.glob(filtre)
    if vg_verbeux : print str(l)

    if vg_time <> None : # evite de recalculer a chaque iteration la retention
        if (vg_output_file<> None): # cas de l'option -o valoriser dans le cas de la retention
            print "L'option -o n est pas compatible avec la gestion de retention"
            print_error(vg_bl)
        date_du_jour = datetime.datetime.now()
        date_retention = date_du_jour - datetime.timedelta(days=vg_time) # calcul de la retention
        if vg_verbeux : print "Date limite de retention : " , date_retention.ctime() #.strftime("%Y%m%d%H%M%S)

    for i in l:
        mon_fic = str(os.path.realpath(path)+char_os+i)
        if vg_verbeux : print "test si fichier existe : " , mon_fic
        if os.path.isfile(mon_fic) == True :
            if vg_time <> None : # gestion de la retention de fichier
                if __SYSTEM == "win32": # cas windows on calcule la date sur la creation et la modification
#                date_du_fichier = datetime.datetime.fromtimestamp(os.stat(mon_fic).st_mtime)
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
                    fichier.append(mon_fic)
                    if vg_verbeux : print "fichier plus ancien - ajout du fichier : " , str(mon_fic)
                else:
                    if vg_verbeux : print "fichier :" , mon_fic,"-", str(date_du_fichier), "trop recent - ignore" , date_retention.ctime()
                    print "fichier ignore : " , mon_fic,"-", str(date_du_fichier), "car trop recent"
            else :
                fichier.append(mon_fic)
                if vg_verbeux : print "ajout du fichier : " , str(mon_fic)
        else:
            if vg_verbeux : print mon_fic, " n est pas un fichier"
    return fichier

def gestion_timestamp():
    # Valorise la variable TIMESTAMP si présente dans la chaine
    global vg_add_suffixe
    global vg_add_prefixe
    global vg_output_file
    global vg_time

    print "Recherche de la variable TIMESTAMP dans les prefixes et suffixes"
    
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

def generation_liste_fichiers_en_entree(char_os):
    # retourne la liste des fichiers a traiter
    path = vg_input_directory + char_os + vg_input_file
    print "Recherche des fichiers presents : " + str(path)
    list_fichiers = listdirectory(vg_input_directory, vg_input_file, char_os)
    if len(list_fichiers) !=0 :
        return list_fichiers
    else :
        print "Aucun fichier a traiter"
        print "Sortie en code warning 1"
        sys.exit(vg_wg)

def verification_fichiers_en_entree(list_fichiers):
    # Verifie les attributs des fichiers en entree
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

def constitution_liste_fichiers_export(list_fichiers_entree, char_os ):
    # print "Taille du fichier (en octets) : " + str(os.path.getsize(i))
    global vg_add_suffixe
    global vg_add_prefixe
    global vg_delete_prefixe
    global vg_delete_suffixe

    list_fichiers_sortie=[]

    print "Preparation des fichiers en sortie"
    for i in list_fichiers_entree :
        if vg_verbeux : print "Traitement du fichier : " + str(i)
        nom_fic = str(os.path.basename(i)).rsplit('.',1)
        if vg_verbeux : print "Nom fichier : " ,nom_fic, len(nom_fic)

        # recupere le nom du fichier a traiter sans le chemin

        if vg_output_file <> None : # desactive les prefixe et suffixe
            if vg_verbeux : print "desactivation des suffixes et prefixe"
            vg_delete_prefixe = None
            vg_delete_suffixe = None
            vg_add_suffixe = None
            vg_add_prefixe = None

        if vg_delete_prefixe <> None : #suppr le prefixe
            if nom_fic[0].startswith(vg_delete_prefixe):
#                nom_fic[0] = nom_fic[0].lstrip(vg_delete_prefixe)
                nom_fic[0] = nom_fic[0][len(vg_delete_prefixe):]
                if vg_verbeux : print "Suppression du prefixe : " + str(nom_fic[0])
            else :
                print "Erreur le filtre de prefixe n'est pas correct - prefixe absent du nom de fichier"
                print_error(vg_bl)
            if len(str(nom_fic[0])) == 0 :
                print "Erreur le fichier resultat ne porte plus de nom apres la suppression du prefixe"
                print_error(vg_bl)

        if vg_delete_suffixe <> None : #suppr le suffixe
            if nom_fic[0].endswith(vg_delete_suffixe):
#                nom_fic[0] = nom_fic[0].rstrip(vg_delete_suffixe)
                nom_fic[0] = nom_fic[0][0:-len(vg_delete_suffixe)]
                if vg_verbeux : print "Suppression du suffixe : " + str(nom_fic[0])
            else :
                print "Erreur le filtre de suffixe n'est pas correct - suffixe absent du nom de fichier"
                print_error(vg_bl)
            if len(str(nom_fic[0])) == 0 :
                print "Erreur le fichier resultat ne porte plus de nom apres la suppression du suffixe"
                print_error(vg_bl)

        if vg_output_file <> None : #gere le cas d un nouveau nom
            # dans le cas d un filtre nom.* ou nom.txt supprime la partie a droite du point
            if len(list_fichiers_entree) == 1 :
                partie_nom = str(vg_output_file).split('.')
                nom_fic = partie_nom
                if vg_verbeux : print "Changement du nom de fichier en sortie option -o : " + str(partie_nom[0])
            else :
                print "Plus d un fichier a  traiter !!! option -o imcompatible"
                print_error(vg_bl)

        if vg_add_suffixe <> None : #ajout d un suffixe
            nom_fic[0] = str(nom_fic[0] + vg_add_suffixe)
            if vg_verbeux : print "Ajout du suffixe : " + str(nom_fic[0])

        if vg_add_prefixe <> None : # ajout d un prefixe
            nom_fic[0] = str(vg_add_prefixe + nom_fic[0])
            if vg_verbeux : print "Ajout du prefixe : " + str(nom_fic[0])

        nom_final = string.join(nom_fic,'.') # reconstruit le nom du fichier
        if vg_verbeux : print "Resultat du traitement du nom de fichier : " + str(nom_final)
        list_fichiers_sortie.append(str(nom_final))

    return list_fichiers_sortie


def fonction_copy(input, output):
    if vg_zipfile == True and zipfile.is_zipfile(input) == False :
        try:
            file = zipfile.ZipFile(str(output)+".zip","w")
            print "Compression en cours"
            file.write(input, os.path.basename(input), zipfile.ZIP_DEFLATED)
            file.close()
        except IOError , (errno,strerror):
            print "Ecriture impossible dans le répertoire de destination"
            print "I/O error (", str(errno), ") : ",str(strerror)
            if errno == 28 :
                print "FS Full : Suppresion de la copie"
                if os.path.isfile(output) == True :
                    os.remove(str(output)+".zip")
            print_error(vg_bl)
        except zipfile.LargeZipFile:
            print "Fichier trop gros ... necessite une version 64bits"
            print_error(vg_bl)
        except :
            print "Erreur lors de la compression"
            print_error(vg_bl)
        if vg_verbeux : print "la commande de compression a reussie"
        print "Compression du fichier : " + str(input) + " vers : " + str(output) + ".zip reussie"
    else:
        if (input != output) :
            try:
                if input != output : copyfile(input,output)
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
            print "Copie du fichier : " + str(input) + " vers : " + str(output) + " reussie"
        if vg_verbeux : print "la commande copyfile a reussie"

def fonction_move(input, output):
    if vg_zipfile == True and zipfile.is_zipfile(input) == False :
        try :
            file = zipfile.ZipFile(str(output)+".zip","w")
            print "Compression en cours"
            file.write(input, os.path.basename(input), zipfile.ZIP_DEFLATED)
            file.close()
            os.remove(input)
        except IOError , (errno,strerror):
            print "Ecriture impossible dans le répertoire de destination"
            print "I/O error (", str(errno), ") : ",str(strerror)
            print_error(vg_bl)
        except zipfile.LargeZipFile:
            print "Fichier trop gros ... necessite une version 64bits"
            print_error(vg_bl)
        except :
            print "Erreur lors de la compression"
            print_error(vg_bl)
        print "Compression du fichier : " + str(input) + " vers : " + str(output) + ".zip reussie"
    else :
        if (input != output) :
            try :
                move(input, output)
            except IOError , (errno,strerror):
                print "Ecriture impossible dans le répertoire de destination"
                print "I/O error (", str(errno), ") : ",str(strerror)
                if errno == 28 :
                    print "FS Full : Suppresion de la copie"
                    if os.path.isfile(output) == True :
                        os.remove(output)
                print_error(vg_bl)
            except OSError, why :
                print "Erreur lors du move :",str(why)
                print_error(vg_bl)
            except :
                print "Erreur lors du move"
                print_error(vg_bl)
            print "Rename du fichier : " + str(input) + " vers : " + str(output) + " reussie"
        if vg_verbeux : print "la commande movefile a reussie"

def verif_existence_fichier(fichier): # sort en erreur dans le cas ou le fichier existe ou un dossier du meme temps
        if vg_verbeux : print "Verif existence du fichier : " + str(fichier)
        if os.path.isfile(fichier) == True and vg_force != 1 and zipfile.is_zipfile(fichier) == False :
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

def execute_rename(list_in, list_out, char_os):
    print "Debut d execution du renommage / copie"

    if len(list_in) <> len(list_out) :
        print "Erreur lors de la constitution des listes de fichiers"
        print "Le nombre de fichiers en entree et en sortie est different"
        print_error(vg_bl)

    if vg_output_file <> None :
        print "Traitement du fichier"
        if len(list_out) == 1 :
            input = list_in[0]
            output = vg_output_directory + char_os + list_out[0]
            verif_existence_fichier(output) # verifie l existence du fichier avant traitement
            if vg_copy == True :
                fonction_copy(input,output)
            else:
                fonction_move(input,output)
        else :
            print "Plus d un fichier a  traiter !!! option -o imcompatible"
            print_error(vg_bl)
    else :
        print "Traitement des : ", str(len(list_out)), " fichiers"
        for i in range(len(list_out)) :
            input = list_in[i]
            output = vg_output_directory + char_os + list_out[i]
            verif_existence_fichier(output) # cas d un fichier portant le meme nom en sortie
            if vg_copy == True :
                fonction_copy(input,output)
            else :
                fonction_move(input,output)
    print "Traitement des : ", str(len(list_out)), " fichiers termine"
    return True

#def valorisation_var_system(chemin): # permet de valoriser des $ sous unix ou % sous windows
#    commande = "echo " + chemin
#    f_output = os.popen(commande)
#    result= ''.join(f_output.readline())
#    if vg_verbeux : print "Resultat de la valorisation " , str(chemin), " - " , str(result)
#    return result[:-1]

def valorisation_var_system(chemin): # permet de valoriser des $ sous unix ou % sous windows
    resultat = os.path.expandvars(chemin)
    if vg_verbeux : print "Resultat de la valorisation " + str(resultat)
    return resultat


#*****************************************************************************************************************************  #
# definition des fonctions par system d exploitation
#*****************************************************************************************************************************  #

def lancement_windows(char_os):

    global vg_input_directory
    global vg_output_directory

    # Valorise les variables d environnement system
    vg_input_directory=valorisation_var_system(vg_input_directory)
    vg_output_directory=valorisation_var_system(vg_output_directory)

    # verification de l existence des dossiers input et output
    verif_existence_dir(vg_input_directory)
    p_verif_chemin_dangeureux(vg_input_directory,vg_secure)
    verif_existence_dir(vg_output_directory)

    # fabrique la liste des fichiers a traiter
    list_fichiers_entree = generation_liste_fichiers_en_entree(char_os)
    # Fonction de l'os

    if vg_verbeux : print "liste des fichiers a traiter : " + str(list_fichiers_entree)
    resultat = verification_fichiers_en_entree(list_fichiers_entree)

    if resultat <> True :
        print "Erreur lors de la verification des parametres sur les fichiers d entree"
        print_error(vg_bl)

    # verification de l option TIMESTAMP dans les options add suffixe et add prefixe
    gestion_timestamp()

    # fabrique la liste des fichiers en sortie
    list_fichiers_sortie = constitution_liste_fichiers_export(list_fichiers_entree, char_os)

    # execute le rename
    if (execute_rename(list_fichiers_entree, list_fichiers_sortie, char_os) == True):
        code_retour_fonction = 0

    # retourne le code retour de l execution de la commande
    return code_retour_fonction

def lancement_hpux(char_os):
    return lancement_windows(char_os)

def lancement_solaris(char_os):
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
    
    # Affiche la commande lancee
    print "Execution de la commande : " + str(sys.argv)

    #*****************************************************************************************************************************  #
    # Lancement de la commande selon la plateforme utilisee
    #*****************************************************************************************************************************  #

    if __SYSTEM == "win32":
            char_os = "\\"
            print "Liste des parametres : "
            if ( param_lg_commande(char_os) != True):
                print_error(vg_bl)
            code_retour = lancement_windows(char_os)
    elif __SYSTEM == "hp-ux11":
            char_os = "/"
            print "Liste des parametres : "
            if ( param_lg_commande(char_os) != True):
                print_error(vg_bl)
            code_retour = lancement_hpux(char_os)
    elif __SYSTEM == "linux2":
            char_os = "/"
            print "Liste des parametres : "
            if ( param_lg_commande(char_os) != True):
                print_error(vg_bl)
            code_retour = lancement_linux(char_os)
    elif __SYSTEM == "solaris":
            char_os = "/"
            print "Liste des parametres : "
            if ( param_lg_commande(char_os) != True):
                print_error(vg_bl)
            code_retour = lancement_solaris(char_os)
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
