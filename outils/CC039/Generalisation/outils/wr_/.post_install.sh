BASE_DIR=/procedure/outils/exploitation/wr_
VERSION_CC=02_00_16
PROG="export_bulle import_bulle"
USER=transfert
GROUP=transfert


echo "######################################################"
echo "Post-installation outils XM_"
echo "* Vérification de la présence du compte '$USER'"
if grep "^$USER:" /etc/passwd >/dev/null 2>&1 ; then
    echo "OK: Compte '$USER' present"
    for file in $PROG ; do
        SETUID_PROG=$BASE_DIR/$VERSION_CC/$file
        echo "* Mise en place du setuid/setgid/owner bit sur '$SETUID_PROG'..."
        if chown $USER:$GROUP $SETUID_PROG && chmod ug+s $SETUID_PROG ; then
            echo "TERMINE"
        else
            echo "ERREUR, code retour $?"
        fi
    done
else
    echo "WARNING: Compte '$USER' absent, il devrait être présent si c'est une machine en bulle internet"
fi
echo "######################################################"

