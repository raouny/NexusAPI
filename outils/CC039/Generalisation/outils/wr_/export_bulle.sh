#!/bin/bash
#############################################################
# Nom : export_bulle.sh
# Langage : bash
# Auteur : Guillaume MICHON 21/08/2009 (v 1.0 - Création initiale)
# Modif. : Guillaume MICHON 05/10/2009 (v 1.1 - Conservation $DONNEES si déjà existant dans l'environnement)
# Modif. : Guillaume MICHON 24/02/2010 (v 1.2 - Passage en itération 2 : intégration pré et post-transfert, suppression de $TRANSFERT)
# Modif. : Guillaume MICHON 27/07/2011 (v 1.3 - Correction de la gestion de la rétention dans le pré-transfert)
#
# Description :
#     Script Client pour SE Transfert en bulle internet
#
# Paramètres, config, etc : $WR_OUTIL/export_bulle.pl
#############################################################

ERREUR_WARNING=1
ERREUR_ARG=2
ERREUR_FATALE=3
HOSTNAME=$(/bin/hostname | /usr/bin/cut -d. -f1)
DATE=$(/bin/date +%Y%m%d%H%M%S)
# Mémorisation des paramètres
if [ "$1" = "-S" ] ; then
    sous_rep=$2
    shift 2
fi
masque_fichier="$1"
retention="$2"
versions="$3"
if [ "$sous_rep" != "" ] ; then arg_sous_rep="-S $sous_rep" ; fi
if [ "$versions" = "" ] ; then versions=0 ; fi
if [ "$retention" = "" ] ; then retention=0 ; fi
# Vérification du format numérique pour $versions et $retention
if echo "$versions" | grep '^[0-9][0-9]*$' >/dev/null ; then true ; else
    echo -1
    echo "Le nombre de versions doit être un nombre" >&2
    exit $ERREUR_ARG
fi
if echo "$retention" | grep '^[0-9][0-9]*$' >/dev/null ; then true ; else
    echo -1
    echo "La rétention doit être un nombre" >&2
    exit $ERREUR_ARG
fi

# Fonction log
log() {
    $WR_OUTIL/export_bulle "$HOME" "$WR_OUTIL" "$DONNEES" "$TRACES" --log-only $*
}

### Chargement de l'environnement ###
# Mémorisation de la variable d'environnement $DONNEES pour restitution après l'import du .profile
donnees="$DONNEES"
export HOME=/home/transfert
. $HOME/.profile
export PATH=$PATH:$WR_OUTIL
# Restitution de $DONNEES si elle existait auparavant
if [ -n "$donnees" ] ; then
    export DONNEES="$donnees"
fi

### Vérification des droits sur le répertoire source ###
nom_fichier=$(basename "$masque_fichier")
if [ "$nom_fichier" = "$masque_fichier" ] ; then
    rep_source=$DONNEES/export
else
    rep_source=$(dirname "$masque_fichier")
fi
if [ -d "$rep_source" -a -r "$rep_source" -a -w "$rep_source" -a -x "$rep_source" ] ; then true ; else
    echo -1
    echo "Droits insuffisants sur $rep_source. Corrigez les droits ou changez le chemin du fichier, ou modifiez la variable d'environnement \$DONNEES" >&2
    exit $ERREUR_FATALE
fi

### Pré-transfert : si une rétention est demandée, on sauvegarde les fichiers locaux ###
if [ $retention -gt 0 ] ; then
    cd "$rep_source"
    for f in $nom_fichier ; do
        if cp "$f" "$DATE.$f" ; then true ; else
            echo -1
            echo "Erreur de copie préalable de la rétention de $rep_donnees/$f" >&2
            exit $ERREUR_FATALE
        fi
    done
    cd -
fi


### Appel initial du script de transfert ###
if [ ! -x $WR_OUTIL/export_bulle ] ; then
    echo -1
    echo "Script de transfert introuvable, vérifiez la variable d'environnement \$WR_OUTIL" >&2
    exit 3
fi

# Appel effectif et traitement d'erreur
i=-1
while read ligne ; do # La ligne de commande source du while est définie après le done
    i=$(($i + 1))
    if [ $i -eq 0 ] ; then
        # La première ligne contient l'ID de transfert
        NUM=$ligne
        echo $NUM
    elif [ $i -eq 1 ] ; then
        # La deuxième ligne contient le chemin local de réception des fichiers
        rep_donnees="$ligne"
    else
        tab_ligne[$i-2]="$ligne"
    fi
# La ligne ci-dessous est un petit trick Bash pour éviter les pipes et les subprocess associés
# (qui amènent des problèmes de scope pour les variables)
done < <( $WR_OUTIL/export_bulle $arg_sous_rep "$HOME" "$WR_OUTIL" "$DONNEES" "$TRACES" "$1" "$2" "$3" ; echo $? )

# La dernière ligne contient le code retour de la commande
if [ $i -ge 2 ] ; then
    cr=${tab_ligne[$i-2]}
    nb_ligne=$(($i - 2))
else
    # Cas particulier : s'il n'y a eu que deux lignes de retour, cela signifie que le script
    # appelé a rencontré une erreur et n'a pas affiché le répertoire de données. Donc le CR a été mémorisé
    # dans la variable $rep_donnees.
    cr=$rep_donnees
    nb_ligne=0
fi
if [ $cr -eq $ERREUR_ARG ] ; then
    i=0
    while [ $i -lt $nb_ligne ] ; do
        echo ${tab_ligne[$i]}
        i=$(($i + 1))
    done
    exit $cr
fi


### Gestion post-transfert ###
cd / # Pour éviter d'être dans un répertoire où le paramètre "*$fichier" du find serait interprété d'abord par le shell
i=0
# L'appel au MTBI a retourné une liste de fichiers traités : un par ligne
while [ $i -lt $nb_ligne ] ; do
    fichier="${tab_ligne[$i]}"
    # Purge des fichiers excédentaires : parmi les fichiers dépassant le nombre de $versions,
    # on supprime les fichiers de plus de $retention jours
    fic_temp="/tmp/export_bulle.$$.tmp"
    find "$rep_donnees" -name "*.$fichier" -mtime +$retention -print > $fic_temp
    for fichier_test in $(cd "$rep_donnees" && /bin/ls -1t *.$fichier 2>/dev/null | tail -n +$versions) ; do
        if grep $fichier_test $fic_temp >/dev/null ; then
            log "Suppression de l'ancienne version $rep_donnees/$fichier_test ..."
            if rm -f "$rep_donnees/$fichier_test" ; then true ; else
                log "Problème de suppression de l'ancienne version $rep_donnees/$fichier_test"
                echo "Warning : Problème de suppression de l'ancienne version $rep_donnees/$fichier_test" >&2
                cr=$ERREUR_WARNING
            fi
        else
            log "Le fichier $rep_donnees/$fichier_test date de moins de $retention jours : pas de suppression"
        fi
    done
    rm -f $fic_temp
    i=$(($i + 1))
done

# Compte-rendu final
message="Transfert OK"
if [ $cr -eq $ERREUR_WARNING ] ; then
    message="$message avec warning"
fi

heure=$(date +"%a %b %d %H:%M:%S %Y")
log "$message!#!$heure!#!$NUM!#!$HOSTNAME!#!$masque_fichier"
exit $cr

