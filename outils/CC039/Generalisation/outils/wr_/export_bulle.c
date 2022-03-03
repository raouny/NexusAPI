/************************************************************
 * Nom : export_bulle.c
 * Langage : C
 * Auteur : Guillaume MICHON 21/08/2009 (v 1.0 - Création initiale)
 * Modif. : Guillaume MICHON 05/10/2009 (v 1.1 - Fournit le ruid en paramètre supplémentaire au script suivant)
 * Modif. : Guillaume MICHON 24/02/2010 (v 1.2)
 *               * Ajout message d'erreur en cas d'échec du execvp
 *               * Correction bug du new_argv : doit se terminer par un NULL
 * Modif. : Guillaume MICHON 09/09/2010 (v 1.3)
 *               * Correction bug "!"
 *
 * Description :
 *    Script Client pour SE Transfert en bulle internet
 *    Wrapper pour le setuid
 *
 * Paramètres & retour : Voir le script appelé
 ***********************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>
#include <string.h>

int main(int argc, char *argv[]) {
   int i;
   char **new_argv;

   /* Changement des uid d'exécution */
   uid_t ruid;  /* Réel */
   uid_t euid;  /* Effectif */
   uid_t suid;  /* Sauvé */
   getresuid(&ruid, &euid, &suid);
   setreuid(geteuid(),geteuid());
   setregid(getegid(),getegid());

   /* Ajout du ruid dans le tableau des arguments */
   new_argv = calloc(argc+2, sizeof(char*));
   new_argv[0] = calloc(15, sizeof(char));
   new_argv[1] = calloc(10, sizeof(char));
   sprintf(new_argv[0], "export_bulle.pl");
   sprintf(new_argv[1], "%d", ruid);
   for (i=1 ; i<argc ; i++) {
      new_argv[i+1] = calloc(strlen(argv[i])+1, sizeof(char));
      strcpy(new_argv[i+1], argv[i]);
   }
   new_argv[argc+1] = (char *)NULL;

   if (execvp("export_bulle.pl", new_argv) == -1) {
      perror("Impossible de lancer export_bulle.pl ");
      return 3;
   }
}
