#/bin/ksh

#############################################################################################
# mvtraces.ksh                                                                              #
#-------------------------------------------------------------------------------------------#
# Description  : Horodatage des fichiers passes en parametres                               #
#                                                                                           #
#-------------------------------------------------------------------------------------------#
# SYNTAXE                                                                                   #
#                                                                                           #
# timestamp.ksh <fichier>     					                            #
#       <fichier>   : fichier a renommer					            #
#                                                                                           #
#############################################################################################
# v 1.0 # 03/07/08 # SM  # 								    #
#############################################################################################

SHLLNAME=$(basename $0)
VERSION=" $SHLLNAME v1.0 - sur SLES\n"

###
# Usage du shell
###
usage ()
{
   [ "$1" ] && verbose "\n$SHLLNAME: $*"

   echo -e "

   $VERSION

   timestamp.ksh <fichier>

   usage:     $SHLLNAME

   Les parametres suivants sont obligatoires:
   <fichier>   : fichier a renommer

   Les parametres suivants sont facultatifs:
	-c : conserve le fichier d'origine

   "
}

typeset cmd="mv "
typeset -i Return=0

while getopts ":c:" option
do
	case "$option" in 
		c) echo "Mode copie"
		   cmd="cp "
		   shift
		   ;;
		\?) echo "$OPTARG : option invalide"
		    usage
		    exit 3
		    ;;
	esac
done
#shift `expr $OPTIND - 1`

if [ $# -lt 1 ]
then
        usage
        exit 3
fi

#AncienNom=`basename $1`

if [ "$(dirname "${1}")" = "." ]
then
	Path="$DONNEES/import"
	Fichier=$*
else
	Path=$(dirname ${1})
	Fichier=$(basename ${1})
fi
cd $Path

echo "Traitement du fichier : $Path/$Fichier"

MV_NouveauNom=$Fichier.`date '+%Y%m%d%H%M%S'`
if [ ! -f $Path/$Fichier ]
then
	echo -e "ERREUR : le fichier source $Path/$Fichier n existe pas"
	Result=1
elif [ -f $Path/MV_NouveauNom ]
then
	echo -e "ERREUR : le fichier cible $Path/$MV_NouveauNom existe deja"
	Result=1
else
$($cmd $Fichier $MV_NouveauNom)
	if [ $? -ne 0 ]
		then
		echo -e "ERREUR: impossible de copier $Path/$Fichier vers $Path/$MV_NouveauNom"
		Return=1
	fi
fi

if [ $Return -ne 0 ]
then
        exit 3
else
        exit 0
fi

