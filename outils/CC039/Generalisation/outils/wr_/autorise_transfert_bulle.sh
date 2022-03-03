#!/bin/bash
#############################################################
# Nom : autorise_transfert_bulle.sh
# Langage : bash
# Auteur : Guillaume MICHON 23/03/2010 (v 1.0 - Création initiale)
# Modif. : Guillaume MICHON 26/07/2011 (v 1.1 - Interdiction de lancement pour root)
#
# Description :
#     Préparation d'un compte pour l'autoriser à transférer dans les bulles internet
#
# Utilisation (en root) : autorise_transfert_bulle.sh <compte>
#############################################################


# Constantes
ERREUR_WARNING=1
ERREUR_ARG=2
ERREUR_FATALE=3
FIC_TRAVAIL=/etc/sudoers.wr_
FIC_SAV=/etc/sudoers.sav_wr_

if [ "$1" = "" ] ; then
    echo "Utilisation : $0 <compte>"
    exit $ERREUR_ARG
fi

compte="$1"
ligne="transfert   ALL = ($compte)NOPASSWD: /usr/bin/rsync, /usr/bin/test, /bin/ls, /usr/bin/du"

# Vérifications de base
if id | grep root >/dev/null 2>&1 ; then true ; else
    echo "Ce script doit être lancé en root."
    exit $ERREUR_FATALE
fi

if [ "$compte" = "root" ] ; then
    echo "Ce script ne doit pas être lancé pour le compte root"
    exit $ERREUR_FATALE
fi

if getent passwd $compte >/dev/null 2>&1 ; then true ; else
    echo "Compte $compte inconnu."
    exit $ERREUR_ARG
fi

if grep "$ligne" /etc/sudoers >/dev/null 2>&1 ; then
    echo "Compte déjà autorisé à effectuer des transferts."
    exit $ERREUR_WARNING
fi

# Copie initiale de travail et de sauvegarde
cp -a /etc/sudoers $FIC_TRAVAIL
if [ $? -ne 0 ] ; then
    echo "Erreur de copie de /etc/sudoers vers $FIC_TRAVAIL"
    exit $ERREUR_FATALE
fi
cp -a /etc/sudoers $FIC_SAV
if [ $? -ne 0 ] ; then
    echo "Erreur de copie de /etc/sudoers vers $FIC_SAV"
    exit $ERREUR_FATALE
fi

# Ajout de la ligne et vérification de la syntaxe
echo "$ligne" >> $FIC_TRAVAIL
/usr/sbin/visudo -cf $FIC_TRAVAIL
if [ $? -ne 0 ] ; then
    echo "Erreur de modification de $FIC_TRAVAIL, visudo a trouvé une erreur (cf message d'erreur plus haut)."
    exit $ERREUR_FATALE
fi

# Remplacement final du fichier
mv -f $FIC_TRAVAIL /etc/sudoers
if [ $? -ne 0 ] ; then
    echo "Erreur de déplacement final de $FIC_TRAVAIL vers /etc/sudoers."
    exit $ERREUR_FATALE
fi

echo "Procédure terminée avec succès."
exit 0

