#!/bin/ksh

# Script d'import/export de fichier
# V 1.0 - AB - Script initial
# V 1.1 - AB - Traitement de fichiers multiple
# V 1.2 - AB - Sécurisation par contrôle des ACL, ajout de traces et amélioration de l'affichage
# V 1.3 - AB - Correction d'un bug si aucune rétention n'était demandé + Ajout de l'option -f du rm pour supprimer un fichier + amélioration des traces de debug

#------------------------------------------------------------------------------------------------------------#
# Initialisation des variables globales
#------------------------------------------------------------------------------------------------------------#
typeset REP_SOURCE=""
typeset REP_CIBLE=""
typeset REP_ARCHIVE=""
typeset ACTION=""
typeset FICHIER=""
typeset RETOUR_FINAL="0"
typeset -i DEBUG=0
typeset -i RETENTION=0
typeset -i T_RET=0
typeset -i V_RET=0
typeset -i NB_FIC=0

#------------------------------------------------------------------------------------------------------------#
# Ecriture de l'entête
#------------------------------------------------------------------------------------------------------------#
time=$(date '+%d/%m/%Y %H:%M:%S')
echo "*******************************************************************"
echo "* Script d'import/export de fichier pour l'ITaaS                  *"
echo "*******************************************************************"
echo "Début du script le ${time}"
echo "*******************************************************************"
echo ""

#------------------------------------------------------------------------------------------------------------#
# Utilisation
#------------------------------------------------------------------------------------------------------------#
Utilisation()
{
    echo 'Utilisation du script :
transf.sh -I|-E -f <fichier> [-s <repertoire_source> -d <repertoire_destinataire>] [-R <repertoire_archives> (-t <temps_retention> -v <nombre_version>)]
Avec    -I ou -E : <Obligatoire> Import ou Export
        L import se fait depuis $TRANSFERT/import vers $DONNEES/export par defaut
        L export se fait depuis $DONNEES/export vers $TRANSFERT/export par defaut
    -s : Répertoire source ou se trouve le fichier a transferer (Ecrase les valeurs par defaut)
    -d : Répertoire cible ou déposer le fichier a transferer (Ecrase les valeurs par defaut)
    -R : Répertoire ou seront placées les archives - Active l archivage
    -t : Temps de rétention en jours de l archivage
    -v : Temps de rétention en nombre de version de l archivage
    -D : Mode debug, affiche des informations supplémentaires
    -h : Affiche cette aide
    '
    
    SortieScript "3"
}

#------------------------------------------------------------------------------------------------------------#
# Tracer
#------------------------------------------------------------------------------------------------------------#
Tracer()
{
    message=$1
    deb=$2
    if [ "$deb" == "1" ]
    then
        if [ $DEBUG -eq 1 ]
        then 
            echo "# ${message}"
        fi
    else 
        echo "# ${message}"
    fi
}

#------------------------------------------------------------------------------------------------------------#
# Gestion erreur
#------------------------------------------------------------------------------------------------------------#
SortieScript()
{
    time=$(date '+%d/%m/%Y %H:%M:%S')
    echo "*******************************************************************"
    echo "Sortie du script en code retour $1"
    echo "Fin d éxécution du script le ${time}"
    echo "*******************************************************************"
    exit "$1"
}

#------------------------------------------------------------------------------------------------------------#
# Verification des options passes en parametre
#------------------------------------------------------------------------------------------------------------#
VerifierOption()
{
    echo "***********************************"
    Tracer "Verification et traitement des options passées au script" "0"
    
    # Verification lie au action, pour definir les repertoires source et cible
    if [ "$FICHIER" = "" ]
    then
        Tracer "Aucune fichier défini pour le transfert, l'option -f est obligatoire et doit être renseignée" "0"
        echo "***********************************"
        echo ""
        Utilisation
    fi
    if [ "$ACTION" = "" ]
    then
        Tracer "Aucune action definie pour le transfert, veuillez utiliser soit l'option -E ou -I" "0"
        echo "***********************************"
        echo ""
        Utilisation
    elif [ "$ACTION" = "import" ]
    then
        if [ "$REP_SOURCE" = "" ]
        then
            if [ -n "$TRANSFERT" ]
            then
                REP_SOURCE="$TRANSFERT/import"
            else
                Tracer 'ERR - La variable $TRANSFERT n existe pas' "0"
                echo "***********************************"
                echo ""
                SortieScript "3"
            fi
        fi
        if [ "$REP_CIBLE" = "" ]
        then
            if [ -n "$DONNEES" ]
            then
                REP_CIBLE="$DONNEES/import"
            else
                Tracer 'ERR - La variable $DONNEES n existe pas' "0"
                echo "***********************************"
                echo ""
                SortieScript "3"
            fi
        fi
    elif [ "$ACTION" = "export" ]
    then
        if [ "$REP_SOURCE" = "" ]
        then
            if [ -n "$DONNEES" ]
            then
                REP_SOURCE="$DONNEES/export"
            else
                Tracer 'ERR - La variable $DONNEES n existe pas' "0"
                echo "***********************************"
                echo ""
                SortieScript "3"
            fi
        fi
        if [ "$REP_CIBLE" = "" ]
        then
            if [ -n "$TRANSFERT" ]
            then
                REP_CIBLE="$TRANSFERT/export"
            else
                Tracer 'ERR - La variable $TRANSFERT n existe pas' "0"
                echo "***********************************"
                echo ""
                SortieScript "3"
            fi
        fi
    fi
    Tracer "Le script est en mode $ACTION" "1"
    Tracer "Le repertoire source est : $REP_SOURCE" "0"
    Tracer "Le repertoire cible est : $REP_CIBLE" "0"
    
    # Verification pour la retention
    if [ $RETENTION -eq 1 ]
    then
        if [ $T_RET -eq 0 -a $V_RET -eq 0 ]
        then
            Tracer "Aucun element de retention defini, on ne supprime pas d'archive" "0"
        else
            Tracer "Le fichier sera retenu avec ${T_RET} jour(s) ou ${V_RET} version(s) (Si egal a 0, ne sera pas pris en compte)" "0"
        fi
    else
        if [ $T_RET -ne 0 -o $V_RET -ne 0 ]
        then
            Tracer "WARN - Option de retention detectée, mais aucun répertoire d archive n est defini." "0"
            RETOUR_FINAL="1"
        fi
    fi
    Tracer "Fin de la verifications des options : OK" "0"
    echo "***********************************"
    echo ""
}

#------------------------------------------------------------------------------------------------------------#
# Vérification avant transfert
#------------------------------------------------------------------------------------------------------------#
# Verification des ACL des repertoires
VerifierRepertoire()
{
    echo "***********************************"
    Tracer "Verification de la présence et des droits des repertoires avant transfert" "0"

    # Vérification du repertoire source et du fichier
    Tracer "Vérification du repertoire source ${REP_SOURCE}" "1"
    
    if [ -d "${REP_SOURCE}" ]
    then
        if [ -r "${REP_SOURCE}" ]
        then 
            if [ -x "${REP_SOURCE}" ]
            then
                if [ -w "${REP_SOURCE}" ]
                    then
                    Tracer "Repertoire source OK" "1"   
                else
                    Tracer "ERR - Le repertoire ${REP_SOURCE} n'est pas accessible en écriture" "0"
                    echo "***********************************"
                    echo ""
                    SortieScript "3"
                fi
            else
                Tracer "ERR - Le repertoire ${REP_SOURCE} n'est pas accessible en execution" "0"
                echo "***********************************"
                echo ""
                SortieScript "3"
            fi
        else
            Tracer "ERR - Le repertoire ${REP_SOURCE} n'est pas accessible en lecture" "0"
            echo "***********************************"
            echo ""
            SortieScript "3"
        fi
    else
        Tracer "ERR - Le repertoire ${REP_SOURCE} n'existe pas" "0"
        echo "***********************************"
        echo ""
        SortieScript "3"
    fi
    
    # Vérification du repertoire d'archive si besoin
    if [ $RETENTION -eq 1 ]
    then
        Tracer "Verification du repertoire d'archive" "1"
        if [ -d "${REP_ARCHIVE}" ]
        then
            if [ -r "${REP_ARCHIVE}" ]
            then 
                if [ -w "${REP_ARCHIVE}" ]
                then 
                    if [ -x "${REP_ARCHIVE}" ]
                    then Tracer "Repertoire d'archive OK" "1"
                    else
                        Tracer "ERR - Le repertoire ${REP_ARCHIVE} n'est pas accessible en execution" "0"
                        echo "***********************************"
                        echo ""
                        SortieScript "3"
                    fi
                else
                    Tracer "ERR - Le repertoire ${REP_ARCHIVE} n'est pas accessible en ecriture" "0"
                    echo "***********************************"
                    echo ""
                    SortieScript "3"
                fi
            else
                Tracer "ERR - Le repertoire ${REP_ARCHIVE} n'est pas accessible en lecture" "0"
                echo "***********************************"
                echo ""
                SortieScript "3"
            fi
        else
            Tracer "ERR - Le repertoire ${REP_ARCHIVE} n'existe pas" "0"
            echo "***********************************"
            echo ""
            SortieScript "3"
        fi

    fi
    
    # Vérification du repertoire cible
    Tracer "Vérification du repertoire cible ${REP_CIBLE}" "1"
    if [ -d "${REP_CIBLE}" ]
    then
        if [ -r "${REP_CIBLE}" ]
        then 
            if [ -x "${REP_CIBLE}" ]
            then
                if [ -w "${REP_CIBLE}" ]
                then Tracer "Repertoire cible OK" "1"
                else
                    Tracer "ERR - Le repertoire ${REP_CIBLE} n'est pas accessible en ecriture" "0"
                    echo "***********************************"
                    echo ""
                    SortieScript "3"
                fi
            else
                Tracer "ERR - Le repertoire ${REP_CIBLE} n'est pas accessible en execution" "0"
                echo "***********************************"
                echo ""
                SortieScript "3"
            fi
        else
            Tracer "ERR - Le repertoire ${REP_CIBLE} n'est pas accessible en lecture" "0"
            echo "***********************************"
            echo ""
            SortieScript "3"
        fi
    else
        Tracer "ERR - Le repertoire ${REP_CIBLE} n'existe pas" "0"
        echo "***********************************"
        echo ""
        SortieScript "3"
    fi
    
    Tracer "Fin de la verifications des repertoires : OK" "0"
    echo "***********************************"
    echo ""
}

# Compare la taille du fichier au repertoire passer en parametre
VerifierEspace() 
{
    typeset -i TAILLE_DIS
    typeset -i TAILLE_FIC
    typeset -i i=1
    
    fichier=$1
    repertoire=$2
    
    ret_df=$(df $repertoire | tail -1)
    TAILLE_FIC=$(ls -l $REP_SOURCE/$fichier | cut -d " " -f5)
    TAILLE_FIC=TAILLE_FIC/1024
    
    for mot in $ret_df
    do
        if [ $i -eq 4 ]
        then
            TAILLE_DIS=$mot
            break
        fi
        i+=1    
    done
    
    if [ $TAILLE_FIC -ge $TAILLE_DIS ]
    then 
            Tracer "ERR - Impossible de créer le fichier ${fichier} sous ${repertoire}
    Espace disponible : ${TAILLE_DIS}
    Taille du fichier : ${TAILLE_FIC}" "0"
        return 1
    else 
        Tracer "Il y a assez de place disponible sur le repertoire ${repertoire} : 
    Espace disponible : ${TAILLE_DIS}
    Taille du fichier : ${TAILLE_FIC}" "1"
        return 0
    fi  
}

# Verifier la non-presence du fichier dans le repertoire cible
VerifierPresence()
{
    fichier=$1
    
    Tracer "Verification de la non-présence du fichier dans le repertoire cible" "1"
    
    if [ -f $REP_CIBLE/$fichier ]
    then
        Tracer "ERR - Le fichier ${fichier} existe déjà dans $REP_CIBLE" "0"
        return 1
    else
        Tracer "Le fichier ${fichier} n'existe pas dans $REP_CIBLE" "1"
        return 0
    fi
}

# Verifier les ACL du fichier a transferer
VerifierFichier()
{
    fichier=$1
    
    Tracer "Verification du fichier a importer" "1"
    
    if [ -f $REP_SOURCE/$fichier  ]
    then
        Tracer "Le fichier ${fichier} existe sous ${REP_SOURCE}" "1"
        if [ -r $REP_SOURCE/$fichier ]
        then
            Tracer "Le fichier ${fichier} est accessible en lecture" "1"
            if [ -w $REP_SOURCE/$fichier ]
            then
                Tracer "Le fichier ${fichier} est accessible en écriture" "1"
                return 0
            else
                Tracer "ERR - Le fichier ${fichier} n'est pas accessible en écriture" "0"
                return 1
            fi
        else
            Tracer "ERR - Le fichier ${fichier} n'est pas accessible en lecture" "0"
            return 1
        fi
    else 
        Tracer "ERR - Le fichier ${fichier} n'existe pas sous ${REP_SOURCE}" "0"
        return 1
    fi
}

#------------------------------------------------------------------------------------------------------------#
# Archive de fichier
#------------------------------------------------------------------------------------------------------------#
Archiver()
{
    typeset -i version=0
    typeset -i fin=0
    
    fichier=$1
    Tracer "*** Archivage du fichier ${fichier} dans ${REP_ARCHIVE}" "0"
    VerifierEspace "${fichier}" "${REP_ARCHIVE}"
    if [ $? = "0" ]
    then
        now=$(date '+%Y%m%d%H%M%S')
        cp $REP_SOURCE/$fichier $REP_ARCHIVE/SAVE$now.$fichier
        if [ $? != "0" ]
        then
            Tracer "ERR - Impossible de créer une archive du fichier dans le repertoire ${REP_ARCHIVE}" "0"
            RETOUR_FINAL="3"
            fin=1
        fi
        
        if [ $T_RET -gt 0 -o $V_RET -gt 0 ]
        then
            if [ $T_RET -gt 0 ]
            then
                Tracer "Suppression des archives de plus de ${T_RET} jour(s)" "0"
                for fich_a_suppr in $(find "$REP_ARCHIVE" -name "SAVE*.${fichier}" -mtime +"$T_RET")
                do
                    Tracer "Suppression du fichier ${fich_a_suppr}" "0"
                    rm -f $fich_a_suppr
                    if [ $? != "0" ]
                    then
                        Tracer "WARN - Erreur lors de la suppression du fichier ${fich_a_suppr}" "0"
                        RETOUR_FINAL="1"
                    fi
                done
            fi
            if [ $V_RET -gt 0 ]
            then
                Tracer "Suppression des archives de plus de ${V_RET} version(s)" "0"
                version=$V_RET+1
                for fich_a_suppr in $(ls -1t $REP_ARCHIVE/SAVE*.$fichier | tail -n +$version)
                do
                    Tracer "Suppression du fichier ${fich_a_suppr}" "0"
                    rm -f $fich_a_suppr
                    if [ $? != "0" ]
                    then
                        Tracer "WARN - Erreur lors de la suppression du fichier ${fich_a_suppr}" "0"
                        RETOUR_FINAL="1"
                    fi
                done
            fi
        fi
    else
        RETOUR_FINAL="3"
        fin=1
    fi
    Tracer "*** Fin de l'archivage" "0"
    return $fin
}

#------------------------------------------------------------------------------------------------------------#
# Transfert de fichier
#------------------------------------------------------------------------------------------------------------#
Transferer()
{
    typeset archive_ok="0"
    
    fichier=$1
    
    echo "***********************************"
    Tracer "Transfert du fichier ${fichier} de ${REP_SOURCE} vers ${REP_CIBLE}" "0"
    VerifierFichier "${fichier}"
    if [ $? = "0" ]
    then
        VerifierPresence "${fichier}"
        if [ $? = "0" ]
        then
            VerifierEspace "${fichier}" "${REP_CIBLE}"
            if [ $? = "0" ]
            then
                Tracer "Copie du fichier ${REP_SOURCE}/${fichier} vers ${REP_CIBLE}/${fichier}.tmp" "1"
                cp  $REP_SOURCE/$fichier $REP_CIBLE/$fichier.tmp
                if [ $? == "0" ]
                then
                    Tracer "Renommage du fichier temporaire" "1"
                    mv  $REP_CIBLE/$fichier.tmp $REP_CIBLE/$fichier
                    if [ $? == "0" ]
                    then
                        if [ $RETENTION -eq 1 ]
                        then
                            if [[ $T_RET -ne 0 || $V_RET -ne 0 ]]
                            then 
                                Archiver "$fichier"
                                archive_ok="$?"
                            fi
                        fi
                        if [ $archive_ok != "1" ]
                        then
                            Tracer "Suppression du fichier d'origine" "1"
                            rm -f $REP_SOURCE/$fichier
                            if [ $? != "0" ]
                            then
                                Tracer "ERR - Impossible de supprimmer le fichier d'origine" "0"
                                RETOUR_FINAL="3"
                            else
                                Tracer "Fin du transfert du fichier ${fichier}" "0"
                            fi
                        else
                            Tracer "ERR - L'archivage du fichier a été demandé, mais a échoué, il n'y donc pas eu de suppression du fichier d'origine" "0"
                        fi
                    else
                        Tracer "ERR - Impossible de renommer le fichier temporaire dans le repertoire cible" "0"
                        rm $REP_CIBLE/$fichier.tmp
                        RETOUR_FINAL="3"
                    fi
                else
                    Tracer "ERR - Impossible de copier le fichier d'origine dans le repertoire cible" "0"
                    RETOUR_FINAL="3"
                fi
            else
                RETOUR_FINAL="3"
            fi
        else
            RETOUR_FINAL="3"
        fi
    else
        RETOUR_FINAL="3"
    fi
    echo "***********************************"
    echo ""
}

#------------------------------------------------------------------------------------------------------------#
# Main
#------------------------------------------------------------------------------------------------------------#
while getopts "IEf:s:d:R:t:v:Dh" opt; do
    case "$opt" in
    I|E)
        if [ "$ACTION" == "" ]
        then
            if [ "$opt" == "I" ]
            then
                ACTION="import"
            else
                ACTION="export"
            fi
        else
            Tracer "L'option -I ou -E est exclusif, ne pas indiquer les deux" "0"
            Utilisation
        fi
        ;;
    f)
        FICHIER=$OPTARG
        ;;
    s)
        REP_SOURCE=$OPTARG
        ;;
    d)
        REP_CIBLE=$OPTARG
        ;;
    R)
        RETENTION=1
        REP_ARCHIVE=$OPTARG
        ;;
    t)
        if let $OPTARG 2>/dev/null
        then
            T_RET=$OPTARG
        else
            Tracer "L'option -t doit être un entier numérique" "0"
        fi
        ;;
    v)
        if let $OPTARG 2>/dev/null
        then
            V_RET=$OPTARG
        else
            Tracer "L'option -t doit être un entier numérique" "0"
        fi
        ;;
    D)
        DEBUG=1
        ;;
    h)
        Utilisation
        ;;
    :)
        Tracer "L'option $OPTARG requiert un argument" "0"
        Utilisation
        ;;
    \?)
        Tracer "Option inconnu $OPTARG" "0"
        Utilisation
        ;;
    *)
        Tracer "Erreur dans les arguments" "0"
        Utilisation
    esac
done


VerifierOption
VerifierRepertoire
if [ -f $REP_SOURCE/$FICHIER ]
then
    for fichierAvecRep in $REP_SOURCE/$FICHIER
    do
        fichier=`basename $fichierAvecRep`
        Transferer "$fichier"
    done
else
    Tracer "ERR - Aucun fichier a traiter" "0"
    echo ""
    RETOUR_FINAL="3"
fi

SortieScript $RETOUR_FINAL