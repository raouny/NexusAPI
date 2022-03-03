#!/usr/bin/perl
#############################################################
# Nom : export_bulle.pl
# Langage : Perl 5
# Auteur : Guillaume MICHON 21/08/2009 (v 1.0 - Création initiale)
# Modif. : Guillaume MICHON 05/10/2009 (v 1.1 - Utilisation de l'uid du compte appelant pour le passer au script export_su
#                                               + refus d'exécution si le compte lanceur n'est pas $COMPTE_TRANSFERT)
# Modif. : Guillaume MICHON 24/02/2010 (v 1.2 - Passage en itération 2)
#               * Suppression de NFS et de l'utilisation du script export
#               * Utilisation du mécanisme de transfert Rsync over SSH
# Modif. : Guillaume MICHON 27/07/2011 (v 1.3 - Durcissement)
#
# Description :
#     Script Client pour SE Transfert en bulle internet
#     Pour fonctionner correctement, ce script doit tourner avec
#       les droits du compte "transfert"
#
# Paramètres : uid du compte appelant, puis 4 variables d'"environnement" HOME, WR_OUTIL, DONNEES et TRACES, puis :
#      * paramètres obligatoires (voir usage)
#      * ou --log-only <ligne à logger>
# Config : En dur pour le moment
#############################################################

use Cwd;
use Sys::Hostname;

# Paramètres de configuration par défaut
$MTBI = "mtbi";
$COMPTE_MTBI_CLIENT = "mtbi_client";
$COMPTE_MTBI = "mtbi";
$CHEMIN_MTBI = "/usr/bin/export_mtbi";
$COMPTE_TRANSFERT = "transfert";
$LOG_AGE_GZIP = 1; # Age d'un fichier de log avant "gzippage"
$LOG_AGE_MAX = 15; # Age d'un fichier de log gzippé avant suppression

# Premiers paramètres
$UID = shift(@ARGV);
$HOME = shift(@ARGV);
$WR_OUTIL = shift(@ARGV);
$DONNEES = shift(@ARGV);
$TRACES = shift(@ARGV);
&usage unless ($UID && $HOME && $WR_OUTIL && $DONNEES && $TRACES);
&forbidden("uid") unless ($UID =~ /^\d+$/);
&forbidden("HOME") unless ($HOME =~ /^[-_ \/\w\.]+$/);
&forbidden("WR_OUTIL") unless ($WR_OUTIL =~ /^[-_ \/\w\.]+$/);
&forbidden("DONNEES") unless ($DONNEES =~ /^[-_ \/\w\.]+$/);
&forbidden("TRACES") unless ($TRACES =~ /^[-_ \/\w\.]+$/);

# Constantes globales
$CONF = "$WR_OUTIL/conf";
@this_time = localtime();
$DATE = sprintf("%04d%02d%02d", $this_time[5]+1900, $this_time[4]+1, $this_time[3]);
$FICLOG = "export_$DATE.log";
$FICLOG_MASQUE = "export_*.log";
$ERREUR_WARNING = 1;
$ERREUR_ARG = 2;
$ERREUR_FATALE = 3;
$NUM = -1;
@PARAMS = @ARGV;



# usage : Ecrit une aide sur la sortie d'erreur et quitte
# Paramètres : Aucun
# Retourne : Rien
sub usage {
    print STDERR "Service de transfert (export). Paramètres : [-S <sous-rep>] <chemin/masque> [<retention en jours> <nb de versions à conserver>]\n";
    print STDERR "Le paramètre -S <sous-rep> déposera les fichiers dans un sous-répertoire sur la cible\n";
    print STDERR "L'argument <chemin> peut être un chemin complet décrivant le fichier dans son répertoire source, ou juste un nom de fichier\n";
    print STDERR "S'il s'agit d'un simple nom de fichier, il sera transféré à partir de $DONNEES/export\n";
    print STDERR "Si un masque est fourni pour <chemin>, celui-ci doit être protégé par des simples quotes pour éviter les interprétations par le shell\n\n";
    print "$NUM\n";
    exit $ERREUR_ARG;
}

# forbidden : Quitte le programme suite à la détection de caractères interdits dans les paramètres
sub forbidden {
    ($var, @trash) = @_;
    print STDERR "Caractères interdits dans le paramètre '$var'. Annulation.\n";
    print "$NUM\n";
    exit $ERREUR_ARG;
}


# log : Ecrit la chaine de caractères fournie en la préfixant de la date et heure
sub log {
    @lignes = @_;
    foreach $ligne_log (@lignes) {
        $ligne_log =~ s/\s*$//;
        print FICLOG localtime()." - $ligne_log\n";
    }
}
sub openLog {
    unless (open(FICLOG, ">>$TRACES/$FICLOG")) {
        print "$NUM\n";
        print STDERR "Impossible d'ouvrir $TRACES/$FICLOG en écriture\n";
        exit $ERREUR_FATALE;
    }
}

# purgeFiles : Supprime les fichiers correspondant à un masque dans un répertoire
# Paramètres :
#   * Chemin du répertoire
#   * Masque du filtre de fichiers
#   * Age maximal avant gzip
#   * Age maximal d'un fichier gzippé avant suppression
sub purgeFiles {
    ($trace_dir, $file_mask, $gzip_age, $rm_age) = @_;
    $current_dir = getcwd();
    chdir($trace_dir);

    @file_list = glob($FICLOG_MASQUE.".gz");
    foreach $file (@file_list) {
        @file_stat = stat($file);
        $file_mtime = $file_stat[9];  # Date au format epoch
        if ( ($EPOCH - $file_mtime)/86400 > $rm_age ) {
            unlink($file);
        }
    }

    @file_list = glob($FICLOG_MASQUE);
    foreach $file (@file_list) {
        @file_stat = stat($file);
        $file_mtime = $file_stat[9];  # Date au format epoch
        if ( ($EPOCH - $file_mtime)/86400 > $gzip_age ) {
            `/bin/gzip '$file'`;
        }
    }
}
 

### Récupération des paramètres positionnels ###
# Gestion du paramètre --log-only : s'il est présent, on se contente de logger
# le contenu de la ligne de commande
if ($ARGV[0] eq "--log-only") {
    shift(@ARGV);
    &openLog();
    &log("@ARGV");
    exit 0;
}
# Autres paramètres
if ($ARGV[0] eq "-S") {
    shift(@ARGV);
    $sous_rep = shift(@ARGV);
    &forbidden("sous_rep") unless ($sous_rep =~ /^[-_ \/\w\.]+$/);
    $sous_rep = "-S '$sous_rep'";
}
$masque_fichier = shift(@ARGV);
$retention = 0 unless ($retention = shift(@ARGV));
$versions = 0 unless ($versions = shift(@ARGV));
&usage unless ($masque_fichier);
&usage unless (scalar(@ARGV) == 0);
&forbidden("fichier") unless ($masque_fichier =~ /^[-_ \/\w\.\*\?]+$/);
&forbidden("retention") unless ($retention =~ /^\d+$/);
&forbidden("versions") unless ($versions =~ /^\d+$/);

### Vérification du compte d'exécution ###
unless (getpwuid($>) eq $COMPTE_TRANSFERT) {
    print "$NUM\n";
    print STDERR "Script lançable uniquement sous le compte $COMPTE_TRANSFERT\n";
    exit $ERREUR_FATALE;
}

### Ouverture du log ###
&openLog();
&log("##### Appel avec paramètres : @PARAMS #####");
# Rotation des logs précédents
&log("Rotation éventuelle des logs précédents (compression à $LOG_AGE_GZIP jours et suppression à $LOG_AGE_MAX jours)");
&purgeFiles($TRACES, $FICLOG_MASQUE, $LOG_AGE_MAX, $LOG_AGE_GZIP);


### Préparation des paramètres d'appel au master ###
# Fichier et répertoire source
@liste_rep = split(/\//, $masque_fichier);
if (scalar(@liste_rep) == 1) {
    # Le fichier fourni n'a pas de chemin, on part donc du principe qu'il est à exporter à partir de $DONNEES/export
    $rep_donnees = "$DONNEES/export";
}
else {
    # Le fichier est fourni avec son chemin, on le copiera donc à partir de l'endroit indiqué
    $masque_fichier = pop(@liste_rep);
    $rep_donnees = join("/", @liste_rep);
}

# Hostname
$hostname = hostname();
if ($hostname =~ /^([^\.]+)\./) {
    $hostname = $1;
}

# Compte applicatif
$compte = getpwuid($UID);
if ($compte eq "root") {
    print "$NUM\n";
    print STDERR "Appel non autorisé par le compte root\n";
    exit $ERREUR_FATALE;
}
if ($compte eq "") {
    print "$NUM\n";
    print STDERR "Appel à partir d'un compte inconnu\n";
    exit $ERREUR_FATALE;
}

# Ligne complète des options de la ligne de commande
$parametres_mtbi = "$sous_rep -s '$hostname' -r '$rep_donnees' -f '$masque_fichier' -u '$compte'";



### Lancement du script de transfert ###
&log("Appel du script master pour le transfert effectif...");
&log("Commande lancée : ( (/usr/bin/ssh -l '$COMPTE_MTBI_CLIENT' '$MTBI' /usr/bin/sudo -u '$COMPTE_MTBI' '$CHEMIN_MTBI' $parametres_mtbi ; /bin/echo \"cr: \$?\") | /bin/sed -e 's/^stdout: /') 2>&1");
@tout_retour = `( (/usr/bin/ssh -l '$COMPTE_MTBI_CLIENT' '$MTBI' /usr/bin/sudo -u '$COMPTE_MTBI' '$CHEMIN_MTBI' $parametres_mtbi ; /bin/echo "cr: \$?") | /bin/sed -e 's/^/stdout: /') 2>&1`;
for (@tout_retour) {
    if (s/stdout: //) {
        if (s/cr: //) {
            $cr = $_; $cr =~ s/\s*$//;
        } else {
            push(@lignes_out, $_);
        }
    } else {
        if ($_ !~ /#######################/ && $_ !~ /non autorises sont interdits/) {
            push(@lignes_err, $_);
        }
    }
}
&log("Stdout :"); &log(@lignes_out);
&log("Stderr :"); &log(@lignes_err);
&log("Code retour : $cr");

# Affichage de la sortie d'erreur dans tous les cas
foreach $ligne (@lignes_err) {
    print STDERR $ligne;
}

# Interprétation du retour - gestion des erreurs imprévues
if ($cr < 0 || $cr > 3 || scalar(@lignes_out) == 0) {
    print "$NUM\n";
    print STDERR "Erreur d'appel au master\n";
    &log("Erreur appel au master!#!".localtime()."!#!$NUM!#!$hostname!#!$rep_donnees/$masque_fichier");
    exit $ERREUR_FATALE;
}

# Interprétation du retour - ID
$NUM = shift(@lignes_out);
$NUM =~ s/\s*$//;
print "$NUM\n$rep_donnees\n";
foreach $ligne (@lignes_out) {
    print $ligne;
}

# Gestion du cas d'erreur pur et simple
if ($cr != 0 && $cr != $ERREUR_WARNING) {
    &log("Transfert KO!#!".localtime()."!#!$NUM!#!$hostname!#!$rep_donnees/$masque_fichier");
    exit $cr;
}

exit $cr;

