#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

#****************************    Fiche signaletique shell  encodage: iso-8859-15    ****************************************    #
# Nom du programme : cc_mail.py    But du programme : Maquette     Version minimum de l'interpreteur python : 2.4
#***********************************************    Syntaxe    **************************************************************   #
#                       cc_mail.py -a param -e param -s param
#**********************************************    Historique    *************************************************************  #
# Version       Date            AUTEUR          ENTREPRISE      Commentaires
# 1.0           12/09/2013      A.LUVISON       La Poste        Creation
# 2.0		18/05/2020	F.MAIRE		La Poste	Ajout authentification - Expéditeur/MDP par défaut pour admin.vtom
#                                                               Serveur SMTP par défaut : smtp.com1.intra.laposte.fr:25
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

#  -x     option oligatoire passee en argument
# [-x]    option optionnelle passe en argument
# <x>     champ obligatoire
# |       separe des options correspond a un ou
# (text)  message de description


# ____________________________


# Constantes : nom et version du script
__NOM_SCRIPT="cc_mail.py"
__VERSION_SCRIPT="2.0"


# Import des modules python
import os
import sys
import platform
import getopt
import re
import os.path
import glob
import string
import smtplib

# Import des modules clients ou fonctions globales
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText 
from email.MIMEBase import MIMEBase
from email import Encoders
from smtplib import SMTPException

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
vg_Param_d = None
vg_Pjointe = ""
vg_Sujet = ""
vg_Expediteur = "admin.vtom@laposte.fr"
vg_Destinataire = ""
vg_Texte = ""
vg_Smtp = "smtp.com1.intra.laposte.fr:25"
vg_Mdp = "rkqmw9Xv9]3G0+Y"


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

    p_Test_Option_Destinataire()
    p_Test_Option_Sujet()
    p_Test_Smtp()
    p_Debug("Fin de p_Test_Options")

def p_Test_Option_Destinataire():
    global vg_Destinataire
    #le champ -a doit etre renseigne obligatoirement
    if vg_Destinataire == "" :
        print "*** Veuillez indiquer un destinataire ***"
        p_Print_Usage(CR_BL)

    p_Debug("Fin de p_Test_Option_Destinataire")

def p_Test_Option_Expediteur():
    global vg_Expediteur
    #le champ -a doit etre renseigne obligatoirement
    if vg_Expediteur == "" :
        print "*** Veuillez indiquer un expediteur ***"
        p_Print_Usage(CR_BL)

    p_Debug("Fin de p_Test_Option_Expediteur")

def p_Test_Option_Sujet():
    global vg_Sujet
    #le champ -a doit etre renseigne obligatoirement
    if vg_Sujet == "" :
        print "*** Veuillez indiquer un sujet ***"
        p_Print_Usage(CR_BL)

    p_Debug("Fin de p_Test_Option_Sujet")

def p_Test_Option_Smtp():
    global vg_Smtp
    #le champ -a doit etre renseigne obligatoirement
    if vg_Smtp == "" :
        print "*** Veuillez indiquer un serveur SMTP et le PORT ***"
        p_Print_Usage(CR_BL)

    elif vg_Smtp:
        try :
            serveur = smtplib.SMTP(vg_Smtp)
        except :
            coderr = 111
            print "*** Le serveur SMTP/PORT specifie ne repond pas ***"
            p_Print_Usage(CR_BL)

    p_Debug("Fin de p_Test_Option_Smtp")

def p_Test_Smtp():
    global vg_Smtp
    if vg_Smtp:
        try :
            serveur = smtplib.SMTP(vg_Smtp)
        except :
            coderr = 111
            print "*** Le serveur SMTP/PORT specifie ne repond pas ***"
            p_Print_Usage(CR_BL)

    p_Debug("Fin de p_Test_Smtp")
	

def p_Print_Usage(err):
#   Affiche le message d utilisation du script
#   quitte le programme avec le code retour passe en argument
    print r"""
    Usage de la commande :
    cc_mail.py -f <fichier1 fichier2 [...]> -s <"sujet"> -a <destinataire> -t <"corps du message"> -e <expediteur> -p <"mdp"> --smtp Ip:Port 


    Sous UNIX / Linux le caractere * doit etre remplace par \*

    -a <destinataire1;destinataire2;destinataire3;...>
    -s <"Le sujet de l'email"> -- ATTENTION DE BIEN METTRE LES ""
	
	[-e] <expediteur>
    [-p] <"mdp"> -- Mot de passe si besoins non obligatoire
    [-t] "corps du message" -- ATTENTION DE BIEN METTRE LES ""
    [-f] <fichier1;fichier2;fichier3;...>
    [--smtp] <adresse_srv_smtp:port>

    [--help]     : produit l'aide suivante
    [--debug]    : mode verbose - permet de debugger
    [-B | --bouchon=<code retour>]   : bouchon CCO
    """
    print("Sortie code erreur : "+str(err))
    sys.exit(err)


def f_Valorisation_Variable_System(chaine): # permet de valoriser des $ sous unix ou % sous windows
    vl_Resultat = os.path.expandvars(chaine)
    p_Debug("Resultat de la valorisation " + str(vl_Resultat))
    return vl_Resultat

def f_Replace_Backshlashs(chaine):
        # Remplace les \ des chemins Windows par des \\ lisibles par python
        # Attention la chaine ne doit pas etre vide
    vl_Resultat = ""
    if chaine != None :
       vl_Resultat = chaine.replace("\\","\\\\")
       p_Debug("Resultat du Replace_Backshlashs : "+str(vl_Resultat))
       return vl_Resultat

def p_Print_Error(mesg, num):
    # retourne le message d erreur et sort en code retour
    print mesg
    print "Sortie en code retour " + str(num)
    sys.exit(num)

def p_Param_Lg_Commande(params):
    # Gestion des arguments passes en parametre de la ligne de commandes
    global vg_Bouchon_CCO
    global vg_Code_Retour_Bouchon_CCO
    global vg_Param_d
    global vg_Sujet
    global vg_Destinataire
    global vg_Pjointe
    global vg_Texte
    global vg_Expediteur
    global vg_Smtp
    global vg_Debug
    global vg_Mdp

    try:
        opts, args = getopt.getopt(params, "e:f:s:a:d:B:t:p:", ["help", "debug","bouchon=","smtp="])

    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        p_Print_Usage(CR_BL)

    for o, a in opts:
        if o == ("--help"):
            p_Print_Usage(CR_BL)
        elif o == ("--smtp"):
            vg_Smtp = a
        elif o == ("-f"):
            vg_Pjointe = a
        elif o == ("-s"):
            vg_Sujet = str(a)
        elif o == ("-e"):
            vg_Expediteur = str(a)
        elif o == ("-a"):
            vg_Destinataire = str(a)
        elif o == ("-t"):
            vg_Texte = str(a)
        elif o == ("-p"):
            vg_Mdp = str(a)
        elif o == ("-d"):
            vg_Param_d = f_Valorisation_Variable_System(a)
        elif o in ("--bouchon","-B"): # UTILISER POUR LE MODE BOUCHON
            vg_Bouchon_CCO = True
            vg_Code_Retour_Bouchon_CCO = int(a)
            p_Print_Error("Mode bouchon",vg_Code_Retour_Bouchon_CCO)
        elif o in ("--debug"):
            vg_Debug = True
            p_Debug("Mode DEBUG Actif")
        else:
            assert False, "option invalide"



    # affiche un message d erreur en cas de params incorrects
    p_Test_Options_Script(params)

###definition procedure envois d'email
def p_Envois_Email():
    global vg_Destinataire
    global vg_Pjointe
    global vg_Sujet
    global vg_Texte
    global vg_Expediteur
    global vg_Smtp


    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = vg_Sujet
    msg['From'] = vg_Expediteur
    msg['To'] = vg_Destinataire

    #vg_Pjointe
    if vg_Pjointe :
        vg_Pjointe_Split=vg_Pjointe.split(';')
        for i in vg_Pjointe_Split:
            if os.path.exists(i) :
                print("Sera en piece jointe : " + i)
                part1 = MIMEBase('application', "octet-stream")

                part1.set_payload( open(i,"rb").read())
                Encoders.encode_base64(part1)
                part1.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(i))

                msg.attach(part1)

            else :
                print("Cette piece jointe n'existe pas : "+i+" -> ignore")


    # Create the body of the message (a plain-text and an HTML version).

    html = str(vg_Texte)

    # Record the MIME types of both parts - text/plain and text/html.
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part2)

    # Send the message via SMTP server.

    s = smtplib.SMTP(vg_Smtp)

    try:
        # print(vg_Expediteur + ' ' + vg_Mdp)
        retour = s.login(vg_Expediteur, vg_Mdp)
        print(retour)
        print('Authentification OK')
    except:
        print('Probleme a l\'authentification :')
        print(sys.exc_info())
        sys.exit(99)

    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    s.sendmail(vg_Expediteur, vg_Destinataire.split(';'), msg.as_string())
    s.quit()


#*****************************************************************************************************************************  #
# definition des fonctions par system d exploitation
#*****************************************************************************************************************************  #

def f_Lancement_Windows(params):
    # execute la procedure d'envois email
    p_Envois_Email()
    # global code_retour_fonction si pas modifie ...
    vl_Code_Retour = 256

    # print "debut de la fonction windows"

    # la commande que je veux executer
    antibug=str(f_Replace_Backshlashs(params)) #evite l'erreur si chaine vide : TypeError: cannot concatenate 'str' and 'NoneType' objects
    vl_Commande = "echo " + antibug



    f_output = os.popen(vl_Commande)
    result= ''.join(f_output.readlines())

    # reccupere le code retour de la commande system
    vl_Return = f_output.close()

    if vl_Return == None :
        vl_Code_Retour = CR_OK
        print'Email envoyé avec succes\n'
    else:
        vl_Code_Retour = vl_Return

    # retourne le code retour de l execution de la commande
    return vl_Code_Retour

def f_Lancement_Hpux(params):
    return f_Lancement_Windows(params)

def f_Lancement_Solaris(params):
    p_Print_Error("OS non supporte", CR_BL)

def f_Lancement_Linux(params):
    return f_Lancement_Windows(params)




#*****************************************************************************************************************************  #
# Main
#*****************************************************************************************************************************  #
if __name__ == "__main__":
    # Variables du programme principal


    # Affiche la version
    print __VERSION + "\n"

    p_Param_Lg_Commande(sys.argv[1:])
    vl_Param = vg_Param_d
    # ++++++++++++++++++++++++++++++++++

    #*****************************************************************************************************************************  #
    # Lancement de la commande selon la plateforme utilisee
    #*****************************************************************************************************************************  #

    if __SYSTEM == "win32":
            vl_Code_Retour = f_Lancement_Windows(vl_Param)
    elif __SYSTEM == "hp-ux11":
            vl_Code_Retour = f_Lancement_Hpux(vl_Param)
    elif __SYSTEM == "linux2":
            vl_Code_Retour = f_Lancement_Linux(vl_Param)
    elif __SYSTEM == "solaris":
            vl_Code_Retour = f_Lancement_Solaris(vl_Param)
    else:
            p_Print_Error("PF inconnue",CR_BL)


    #######################################
    # Verification du code retour         #
    #######################################
    if vl_Code_Retour not in (0, None):
        p_Print_Error("Erreur inattendue", CR_BL)

    #######################################
    # Fin du Programme avec code_retour   #
    #######################################
    else:
        p_Print_Error("Fin du programme. " ,vl_Code_Retour)


