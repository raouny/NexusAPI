#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

#****************************    Fiche signaletique shell  encodage: iso-8859-15    ****************************************    #
# Nom du programme : ref_liv_ordos.py    But du programme : Maquette     Version minimum de l'interpreteur python : 2.4
#***********************************************    Syntaxe    **************************************************************   #
#  ref_liv_ordos.py --IP 221.128.10.250 --user <login> --pwd <password> -d <dossier> -v <version> --env <environnement> --phase <ppd||prd> [--debug]
#**********************************************    Historique    *************************************************************  #
# Version       Date            AUTEUR          ENTREPRISE      Commentaires
# 1.0           19/07/2017      Z.BEN ALI       La Poste        Création du script
#**********************************************    Codes retour    ***********************************************************  #
# code 0: Normal - Code retour normal : L enchainement est poursuivi
# code 1: Warning - Detection d une anomalie : L enchainement peut etre poursuivi
# code 3: Critique - Erreur Critique
# code 3: Exemple d erreur - Erreur parametres incorrects
# code > 3 : Traitement en erreur avec un code retour particulier
#*****************************************************************************************************************************  #

# bonnes pratiques :
# ------------------

# Cas des constantes :
#    Tout en majuscule
#    Separer les mots par des underscore
#    Donner des noms simples et descriptifs
#    N'utiliser que des lettres [a-z][A-Z] et [0-9]

# Cas des variables :
#    Premiere lettre en minuscule
#    Melange de minuscule, majuscule avec la premiere lettre de chaque mot en majuscule
#    Donner des noms simples et descriptifs
#    Variable d'une seule lettre e eviter au maximum sauf dans des cas precis et locaux (tour de boucle)
#    N'utiliser que des lettres [a-z][A-Z] et [0-9]

#    pour debuter une variable :
#    vg_ Variable Globale
#    vl_ Variable Locale

# Cas des fonctions et procedures :

#    Premiere lettre en majuscule
#    Melange de minuscule, majuscule avec la premiere lettre de chaque mot en majuscule
#    Donner des noms simples et descriptifs
#    Eviter les acronymes hormis les communs (Xml, Url, Html)
#    N'utiliser que des lettres [a-z][A-Z] et [0-9]
#    Mettre un commentaire en dessous por decrire la fonction / procedure

#    pour debuter une fonction prefixer par :
#    f_ pour les fonctions
#    p_ pour les procedures

# Syntaxe des parametres transmis au script

#  -x     option obligatoire passee en argument
# [-x]    option optionnelle passe en argument
# <x>     champ obligatoire
# |       separe des options correspond a un ou
# (text)  message de description


# ____________________________


# Constantes : nom et version du script
__NOM_SCRIPT="ref_liv_ordos.py"
__VERSION_SCRIPT="1.0"


# Import des modules python
import os
import sys
import platform
import getopt
import os.path
import glob
#import string
import datetime
import socket
from string import ascii_uppercase
import time
import subprocess
import re


# Mode Bouchon mis en place pour les besoins du CCO: False ou True
vg_Bouchon_CCO = False
vg_Code_Retour_Bouchon_CCO = 5 # Code retour dans le cas de l'utilisation du mode bouchon
# Fin du parametrage du mode bouchon

# Definition des constantes systemes
__SYSTEM = sys.platform
__PYTHON_VERSION = sys.version

# Definition des constantes code retour VTOM
CR_WG = 1 # code retour warning
CR_BL = 3 # code retour bloquant
CR_OK = 0 # code retour bonne execution

# Definitions des variables globales :
vg_Debug = False
vg_Param_v = ""
vg_Param_d = ""
vg_Param_ccx=""
vg_Param_env=""
vg_chemin=""
vg_Param_phase=""

#chemin afin de recuperer le vtexport
chemin_export="/wav01/absyss/vtom55/backup/exports"


########################################################################################## variable pour le montage reseau
#variable de repertoire de destination
chemin_W="\Liv_Ordos"
#chemin_W="\DEPOT"
chemin_U="/DSL2/Liv_Ordos"
#chemin_U="/DSL2/DEPOT"
chemin_L="/Liv_Ordos"
#chemin_L="/DEPOT"

#Variables pour les parametres
vg_adrIP = ""
vg_Password = ""
vg_User = ""
vg_DMZ = False


#variables du montage reseau
#vg_DossierMont = "/mnt/DSL_CC"
vg_DossierMont = "/mnt/DSL_Liv_Ordos"
vg_ParaWind= "/USER:"
vg_LecteurLibre = ""
vg_WReseaux = "\\DSL2"
vg_OReseaux = "/DSL2"
vg_Reseaux = "DSL2"
Code_Retour_Cmd = -1


# Version du CC a completer
__VERSION = __NOM_SCRIPT + "  v" + __VERSION_SCRIPT + " - python "+__PYTHON_VERSION+" - "+__SYSTEM

#*****************************************************************************************************************************  #
# Definitions des fonctions et procedures
#*****************************************************************************************************************************  #
def p_Debug(chaine):
    # affiche la chaine lorsque l option debug est positionnee a True
    if vg_Debug : print str(chaine)

def p_Test_Options_Script(arguments):
    # tests les arguments passes en parametres au script
    p_Debug("Tests des arguments du script")

    if arguments == [] :
        print "*** un argument est manquant ***"
        p_Print_Usage(CR_BL)

	
    p_Debug("Debut de p_Test_Options")
    p_Test_Option_Dossier()
    p_Test_Option_Version()
    p_Test_Option_Environnement()
    p_Test_Option_IP()
    p_Test_Option_Login()
    p_Test_Option_Password()
    p_Test_Option_Phase()
    p_Debug("Fin de p_Test_Options")


def p_Test_Option_Dossier():
    global vg_Param_d
    global vg_Param_ccx

    p_Debug("Debut de p_Test_Option_Dossier") 
   #le champ -d doit etre renseigne obligatoirement
    if vg_Param_d == "" :
        print "*** Le nom de dossier n a pas ete indique ***"
        p_Print_Usage(CR_BL)

    #on vérifie si le ccx est renseigne entre parenthese
    cr_commande=vg_Param_d.find('(')	

    if cr_commande==-1 :
        #si le ccx n a pas de parenthese ouvrante (
        print "*** Le code appli <ccx> n a pas etait renseigne entre parenthese dans le nom de dossier ***"
        p_Print_Usage(CR_BL)
    else :
        cr_commande=vg_Param_d.find(')')
        #si le ccx n a pas de parenthese fermante )
        if cr_commande==-1 :
            print "*** La parenthese du ccx n a pas ete referme dans le nom de dossier ***"
            p_Print_Usage(CR_BL)

        else :

            #On recupere le ccx a partir du nom de dossier
            recuperation_ccx=vg_Param_d.split('(')
            recup_ccx=recuperation_ccx[1].split(')')
            vg_Param_ccx=recup_ccx[0].lower()

            #on verifie que le ccx contient bien 3 caracteres           	
            if len(vg_Param_ccx)!=3 :
                print "*** Dans le nom de dossier, le code appli ccx doit avoir obligatoirement 3 caracteres entre () ***"
                p_Print_Usage(CR_BL)
                
            else :
            #on verifie qu il n y a rien apres le ccx         	                
                if recup_ccx[1]!= '':
                    print recup_ccx[1]
                    print "*** Dans le nom de dossier, il ne faut rien mettre apres le ccx.  ***"
                    p_Print_Usage(CR_BL)

                else :
                    # on renomme le nom de dossier pour qu il respecte la norme NOM_APPLI(ccx)         	                  
                    recup_nom_appli=recuperation_ccx[0].replace(' ','_')
                    vg_Param_d=recup_nom_appli+'('+vg_Param_ccx+')'

                    #on verifie qu il n y a aucun caractere accentue
                    accent=re.findall("([*&éèçàùÄËÏÖÜâêîôû])",vg_Param_d)

                    if accent != [] :
                        print "*** Dans le nom de dossier, les accents ne sont pas autorises. Tout doit etre en majuscule. "
                        p_Print_Usage(CR_BL)

    p_Debug("Fin de p_Test_Option_Dossier")

def p_Test_Option_Version():
    global vg_Param_v

    p_Debug("Debut de p_Test_Option_Version") 
    #le champ -v doit etre renseigne obligatoirement
    if vg_Param_v == "" :
        print "*** Le numero de version n a pas ete indiquee ***"
        p_Print_Usage(CR_BL)
    p_Debug("Fin de p_Test_Option_Version")



def p_Test_Option_Environnement():
    global vg_Param_env

    p_Debug("Debut de p_Test_Option_Environnement") 
    #le champ --env doit etre renseigne obligatoirement
    if vg_Param_env == "" :
        print "*** L'environnement n'a pas ete d'indiquee ***"
        p_Print_Usage(CR_BL)
    p_Debug("Fin de p_Test_Option_Environnement")

def p_Test_Option_IP():
    global vg_adrIP

    p_Debug("Debut de p_Test_Option_IP") 
    #le champ --IP doit etre renseigne obligatoirement
    if vg_adrIP == "" :
        print "*** L'adresse IP  n a pas ete indiquee ***"
        p_Print_Usage(CR_BL)
    p_Debug("Fin de p_Test_Option_IP")	

def p_Test_Option_Login():
    global vg_User

    p_Debug("Debut de p_Test_Option_Login") 
    #le champ --user ou -u doit etre renseigne obligatoirement
    if vg_User == "" :
        print "*** Le login n a pas ete indiquee ***"
        p_Print_Usage(CR_BL)
    p_Debug("Fin de p_Test_Option_Login")
	
def p_Test_Option_Password():
    global vg_Password

    p_Debug("Debut de p_Test_Option_Password") 
    #le champ --pwd ou -p doit etre renseigne obligatoirement
    if vg_Password == "" :
        print "*** Le password n a pas ete indiquee ***"
        p_Print_Usage(CR_BL)
    p_Debug("Fin de p_Test_Option_Password")	

def p_Test_Option_Phase():
    global vg_Param_phase

    p_Debug("Debut de p_Test_Option_Phase") 
    #le champ -v doit etre renseigne obligatoirement
    if vg_Param_phase == "" :
        print "*** La phase n a pas etait renseigne : 'PRD' pour prod ou 'PPD' pour pre prod ***"		
        p_Print_Usage(CR_BL)



    if vg_Param_phase not in ('prd','ppd') :
        print "*** La phase renseignee est incorrecte. Valeurs possibles : 'prd' pour prod ou 'ppd' pour pre prod ***"
        p_Print_Usage(CR_BL)

		

    p_Debug("Fin de p_Test_Option_Phase")
	
	
def p_Print_Usage(err):
#   Affiche le message d utilisation du script
#   quitte le programme avec le code retour passe en argument
    print r"""
    Usage de la commande :
    ref_liv_ordos.py --IP 221.128.10.250 --user <login> --pwd <password> -d <NOM_APPLI(ccx)> -v <version> --env <environnement> --phase <prd||ppd> [--debug]
    
	Aide :
	ref_liv_ordos.py -h

    Sous UNIX / Linux le caractere * doit etre remplace par \*

    Options obligatoires : 

     Info lecteur reseau   ---------------------------------
    -s / --IP "Adresse IP DSL" :  Adresse IP du serveur source (DSL) au
                             format xxx.xxx.xxx.xxx

    -u / --user "login"    : Utilisateur de connexion au serveur source (DSL)
    -p / --pwd "password"  : Mot de passe de l'utilisateur de connexion
                             au serveur source (DSL)
    Variables       -----------------------------------------
    -d | --dossier	"dossier"   : dossier sous le format "NOM_DE_L_APPLI(ccx_)"
                    ATTENTION : pas d'accent !!!!
                                    Nom de l appli en MAJUSCULES 
                                    ccx en minuscule et obligatoirement en 3 caractères
		                          Il ne faut pas oublier de mettre les guilemets

    -v | --version :  version donnee par le CCO
    --env	   : Environnement de l appli 
    --phase	   : phase en indiquant si on est en : PPD pré prod  
                                           ou en : PRD prod

    **********************************************************
    Options optionnelles :

    [-h | --help] : produit l'aide suivante
    [--debug]     : mode verbose - permet de debugger
    [-B | --bouchon=<code retour>]   : bouchon CCO

    """
    print("Sortie code erreur : "+str(err))
    sys.exit(err)



def f_IP_Validation(Adresse_Ip): # fonction qui verifie si l'adresse ip donn? en parametre a bien un format valide et joignable( trois points et quatre nombres)

    try:
        socket.inet_pton(socket.AF_INET, Adresse_Ip)

    except AttributeError:  # famille d'adresse non valide

        try:
            socket.inet_aton(Adresse_Ip)

        except socket.error:
            return False

        return Adresse_Ip.count('.') == 3

    except socket.error:  # format d'adresse non valide
        return False

    return True




def p_Print_Error(mesg, num):
    # retourne le message d erreur et sort en code retour
    print mesg
    print "Sortie en code retour " + str(num)
    sys.exit(num)

def p_Param_Lg_Commande(params):
    # Gestion des arguments passes en parametre de la ligne de commandes
    global vg_Bouchon_CCO
    global vg_Code_Retour_Bouchon_CCO
    global vg_Param_v
    global vg_Debug
    global vg_Param_d
    global vg_Param_ccx
    global vg_Param_env
    global vg_Param_phase

    global vg_adrIP
    global vg_User
    global vg_Password
    global vg_DMZ

    try:
        opts, args = getopt.getopt(params, "d:v:B:hs:u:p:z", ["help", "debug","bouchon=","dossier=","version=","env=","IP=","user=","pwd=","DMZ","phase="])

    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        p_Print_Usage(CR_BL)

    for o, a in opts:
        if o in ("--help","-h"):
            p_Print_Usage(CR_BL)
        elif o in ("-d","--dossier"):
            vg_Param_d = a.upper()       
	elif o in ("-v","--version"):
	    vg_Param_v = a
        elif o in ("--env"):
            vg_Param_env = a
        elif o in ("--bouchon","-B"): # UTILISER POUR LE MODE BOUCHON
            vg_Bouchon_CCO = True
            vg_Code_Retour_Bouchon_CCO = int(a)
            p_Print_Error("Mode bouchon",vg_Code_Retour_Bouchon_CCO)
        elif o in ("--debug"):
            vg_Debug = True
            p_Debug("Mode DEBUG Actif")

        elif o in ("-s","--IP") :
            vg_adrIP = a
            if f_IP_Validation(vg_adrIP) :
                p_Debug("Format IP valide")
            else :
                print("Adresse IP renseignee non joignable ou format non valide")
                p_Print_Usage(CR_BL)
        elif o in ("-p","--pwd") :
            vg_Password = a
        elif o in ("-u","--user") :
            vg_User = a
        elif o in ("-z", "--DMZ") :
            vg_DMZ = True
        elif o in ("--phase"):
            vg_Param_phase = a.lower()
        else:
            assert False, "option invalide"


    # affiche un message d erreur en cas de params incorrects
    p_Test_Options_Script(params)




def f_Montage_Ressource_DSL(IP,USER,PWD,OS_System): # fonction qui monte la ressource reseau selon l'os

    # Gestion des arguments passes en parametre de la ligne de commandes
    global vg_chemin
	
    if OS_System == "windows" : # monte le DSL sur avec une lettre qui n'est pas utilise et renvoie le vg_chemin
         global vg_LecteurLibre
         p_Debug("\nFonction de montage de ressource")
         vg_Lecteur = list(ascii_uppercase) # rempli un tableau avec l'alphabet en majuscule
         vg_Lecteur.reverse() # commence le tableau par la dernier case pour commencer par le Z
         p_Debug(vg_Lecteur)

         for indice, lect in enumerate(vg_Lecteur) :
              p_Debug("test des lecteurs pour monter le DSL sur un emplacement libre")
              connexion = "net use"+" "+vg_Lecteur[indice]+": "+"\\\\"+IP+vg_WReseaux+" "+PWD+" "+vg_ParaWind+USER+" 2> Nul" + " > Nul"
              p_Debug(connexion)
              Code_Retour_Cmd = os.system(connexion)

              if Code_Retour_Cmd == 0 :
                   break

         if Code_Retour_Cmd == 0 : # boucle qui recupere la lettre libre pour une utilisation ulterieur
            p_Debug("recuperation du lecteur libre : ")
            vg_LecteurLibre = vg_Lecteur[indice]+":"
            p_Debug("Lecteur libre =  "+vg_LecteurLibre)
            vg_chemin = vg_LecteurLibre+chemin_W
            p_Debug("vg_chemin du DSL : "+vg_chemin)
            #os.system("dir " + vg_LecteurLibre)
            return vg_chemin

         else :
            print("Lecteur libre non defini, probleme de montage reseau. verifiez si vous avez donne les bonnes donnees de connexion\n")
            print("Vous devez avoir les droits administrateur afin de monter un lecteur reseau \n")

            sys.exit(CR_BL)



    elif OS_System == "linux" or OS_System == "hpux" : # creer un dossier de montage et monte le DSL dedans et renvoie le vg_chemin 

        if os.path.isdir(vg_DossierMont) == False :
            cmd = " mkdir -p"+" "+vg_DossierMont+" > /dev/null" +" 2> /dev/null"
            p_Debug("commande passee pour la creation du dossier de montage du DSL : "+str(cmd))
            Code_Retour_Cmd = os.system(cmd)

            if Code_Retour_Cmd == 0 :
                p_Debug("Dossier de Montage du DSL cree")

            else :
                print("code retour cmd "+ str(Code_Retour_Cmd))
                print("Dossier de Montage du DSL non cree")
                sys.exit(CR_BL)

        else :
            p_Debug("Dossier de montage deja present, poursuite du programme")


        if OS_System == "linux" :
            p_Debug("montage pour serveur linux")
            cmd = "mount -t cifs -o"+" "+"username="+vg_User+","+"password="+vg_Password+" "+vg_adrIP+":"+vg_Reseaux+" "+vg_DossierMont+" > /dev/null" +" 2> /dev/null"
 
        if OS_System == "hpux" :
            p_Debug("montage pour serveur hp-ux")
            cmd = "mount -F nfs -o rw,username="+vg_User+","+"password="+vg_Password+" "+vg_adrIP+":"+vg_OReseaux+" "+vg_DossierMont #+" > /dev/null" +" 2> /dev/null"

        p_Debug("commmande passee pour le montage du DSL : "+cmd)
        Code_Retour_Cmd = os.system(cmd)

        if Code_Retour_Cmd == 0 :
            p_Debug("Lecteur reseau DSL monte")

            if OS_System == "linux": vg_chemin = vg_DossierMont+chemin_L
            else : vg_chemin = vg_DossierMont+chemin_U

            p_Debug("vg_chemin du DSL : "+vg_chemin)
            return vg_chemin

        else :
            print(Code_Retour_Cmd)
            print("******************")
            print("une erreur s'est produite dans le montage du DSL, verifiez qu'il n'est pas deja monte\n")
            cmd = " rmdir"+" "+vg_DossierMont+" > /dev/null" +" 2> /dev/null"
            p_Debug("commande passee pour la suppression du dossier de montage : "+ str(cmd))
            Code_Retour_Cmd = os.system(cmd)

            if Code_Retour_Cmd == 0 :
                p_Debug("dossier de montage supprime")
                sys.exit(CR_BL)

            else :
                p_Debug("le dossier de montage DSL n'a pas ete supprime correctement")
                sys.exit(CR_BL)


    else :
        print "systeme non pris en charge"
        sys.exit(CR_BL)


def p_Demontage_Ressource_DSL(OS_System): # fonction qui demonte de DSL et supprime les dossiers de montage pour les systeme linux et unix

        p_Debug("\nFonction de demontage des ressources reseaux")

        if OS_System == "windows" :
            time.sleep(20)
            global vg_LecteurLibre
            cmd = "net use" + " " +vg_LecteurLibre+" "+"/delete" +" /yes" #" 2> Nul" + " > Nul"
            p_Debug("demontage du DSL : " + cmd)
            Code_Retour_Cmd = os.system(cmd)

            if Code_Retour_Cmd == 0 :
                p_Debug("Demontage du DSL reussi")

            else :
                print("ERREUR lors du demontage du DSL")
                return CR_WG

        elif OS_System == "linux" or OS_System == "hpux":
            if OS_System == "linux" :
                cmd = " umount"+" -l "+vg_DossierMont #+" > /dev/null" +" 2> /dev/null"
            else :
                cmd = " umount"+" "+vg_DossierMont +" > /dev/null" +" 2> /dev/null"
            p_Debug("commande passee pour demontage du DSL : "+ str(cmd))
            Code_Retour_Cmd = os.system(cmd)

            if Code_Retour_Cmd == 0 :
                p_Debug("Demontage du DSL reussi")
                cmd = " rmdir"+" "+vg_DossierMont #+" > /dev/null" +" 2> /dev/null"
                p_Debug("commande passer pour la suppression du dossier de montage : "+str(cmd))
                Code_Retour_Cmd = os.system(cmd)

                if Code_Retour_Cmd == 0 :
                    p_Debug("Suppression du dossier de montage reussie")

                else :
                    print("ERREUR lors de la suppression du dossier de montage")
                    return CR_WG

            else :
                print("ERREUR lors du demontage du DSL")
                return CR_WG


#definition procedure creation dossier (arborescence)
def p_Creation_Dossier(OS_System,dossier,numVersion):

    #On verifie si le dossier de destination existe
    if os.path.exists(vg_chemin):

		#On se place sur le chemin de destination
        os.chdir(vg_chemin)

		#On verifie si le dossier precise en ligne de commande est present dans le repertoire
        if os.path.exists(dossier) == 0 :
            os.mkdir(dossier)
            print "Le dossier " + dossier + " a bien ete cree."
        else : print "Le dossier " + dossier + " existe deja."
		
        #On se place dans le dossier             
        os.chdir(dossier)

        #On verifie si le numero de version existe 
        if os.path.exists(vg_Param_v)== 0 :
            os.mkdir(vg_Param_v)
            print "Le dossier "+vg_Param_v+" a bien ete cree."
        else : print "Le dossier " + vg_Param_v + " existe deja."  

        #On se place dans le dossier de version 
        os.chdir(vg_Param_v)

        #On creer un dossier sous la forme ordo_<ccx>_timestamp
        timestamp= str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
        dossier_ordo= vg_Param_phase+"_"+"ordo_"+vg_Param_ccx+"_"+timestamp
        os.mkdir(dossier_ordo)
        print "Le dossier "+dossier_ordo+" a bien ete cree."

        #On se place dans le dossier ordo_<ccx>_timestamp
        os.chdir(dossier_ordo)

        #On cree un dossier Sources
        os.mkdir("Sources")

        #On se place dans le dossier Sources
        os.chdir("Sources")

        #On verifie que le chemin present dans la variable 'chemin_export' existe
        if os.path.exists(chemin_export)== 0 :
            print "Le chemin "+chemin_export+" est incorrect ou introuvable."        
            print "La copie du dernier vtexport n'a donc pas ete effectue." 
            return CR_WG

        else :
            print "Le chemin "+chemin_export+" existe."

            #on enregistre le chemin courant 
            chemin_courant=os.getcwd()
           
            #On se place dans le dossier stocke dans la variable 'chemin_export' afin de recuperer le dernier vtexport (selon l'environnement) du master vtom concerne     
            os.chdir(chemin_export)

            if OS_System == "linux" or OS_System == "hpux":

            	#on se connecte avec l utilisateur avtom01 et on effectue la conversion en .vtexport du fichier le plus recent de l environnement vg_Param_env
            	os.system("su - avtom01 --command=\"vtexport -f "+ vg_Param_env+ " > \'backup/exports/"+vg_Param_env+".vtexport\'\"")

            	#copy du fichier.vtexport généré vers le dossier Sources de Liv_Ordos
            	copy="cp "+vg_Param_env +".vtexport \'" + chemin_courant+ "\'"
            	os.system(copy)

            	#On se place dans le dossier Sources
            	os.chdir(chemin_courant)
            	os.system("ls")

            	#On fait une copy dt .vtexport et on le copie en rajoutant le timestamp dans le dossier ordo_<ccx>_timestamp
            	copy="cp "+vg_Param_env +".vtexport ../"+ vg_Param_env+"_"+timestamp+".vtexport" #\""+str(chemin_courant)+"\""
            	os.system(copy)

            if OS_System == "windows" :
            	print "Pour le moment, nous ne sommes pas en mesure de copie le vtexport avec windows."

    else :
        print "Le chemin de destination : \'"+ vg_chemin +"\' est incorrect ou introuvable"
        print "L arborescence n a pas ete effectuee"
        return CR_BL


def p_liste_dossiers_existants(OS_System):
	global vg_chemin
#   Affiche la liste des dossiers existants dans le chemin de destinations
	print("Dossiers presents dans " + vg_chemin)

	if OS_System == "windows" : os.system("dir " + vg_chemin)
	if OS_System == "linux" or OS_System == "hpux" : os.system("ls -l " + vg_chemin)


#*****************************************************************************************************************************  #
# definition des fonctions par system d exploitation
#*****************************************************************************************************************************  #


def lancement_Multi_OS(OS_System):

    # global code_retour_fonction si pas modifie ...
    code_retour = 256
	
    if OS_System == "linux" or OS_System =="windows" :
        f_Montage_Ressource_DSL(vg_adrIP,vg_User,vg_Password, OS_System)

    elif OS_System == "hpux" :
        print("A ce jour, ce systeme d exploitation ne peut copier des dossiers dans Liv_Ordos. arret du script")
        sys.exit(CR_BL)

    elif OS_System == "solaris" :
        print("Systeme pas pris en compte. arret du script")
        sys.exit(CR_BL)

    print "Repertoire actuel :"+str(vg_chemin)

    #p_liste_dossiers_existants(OS_System) 

	# execute la procedure de creation de dossier  
    p_Creation_Dossier(OS_System,vg_Param_d,vg_Param_v)


    ####################################
    # demontage du lecteur reseaux
    ####################################
    cr=p_Demontage_Ressource_DSL(OS_System)

    if cr == None :
        code_retour = CR_OK	

    # retourne le code retour de l execution de la commande
    return code_retour


#*****************************************************************************************************************************  #
# Main
#*****************************************************************************************************************************  #
if __name__ == "__main__":

    # Affiche la version
    print __VERSION + "\n"

    p_Param_Lg_Commande(sys.argv[1:])

    # ++++++++++++++++++++++++++++++++++

    #*****************************************************************************************************************************  #
    # Lancement de la commande selon la plateforme utilisee
    #*****************************************************************************************************************************  #

    if __SYSTEM == "win32":
            code_retour = lancement_Multi_OS("windows")

    elif __SYSTEM == "hp-ux11":
            code_retour = lancement_Multi_OS("hpux")

    elif __SYSTEM == "linux2":
            code_retour = lancement_Multi_OS("linux")

    elif __SYSTEM == "solaris":
            code_retour = lancement_Multi_OS("sun")
    else:
            p_Print_Error("PF inconnue",CR_BL)


    #######################################
    # Verification du code retour         #
    #######################################
    if code_retour not in (0, None):
  
        p_Print_Error("Erreur inattendue", CR_BL)

    #######################################
    # Fin du Programme avec code_retour   #
    #######################################
    else:
        p_Print_Error("Fin du programme. " ,code_retour)

