String branchName = "main"
String gitCredentials = "RaounyGit"
String repoUrl = "https://github.com/raouny/NexusAPI.git"
String tag = "${TAG}"

node {

  stage('Clone repo Git') {
      echo 'Création du dossier de sortie'
      sh 'mkdir -p /var/lib/jenkins/workspace/buildFolder'

      echo 'Cloning files from (branch: "' + branchName + '" )'
      dir('/var/lib/jenkins/workspace/buildFolder') {
          git branch: branchName, url: repoUrl
      }     
  } 
   stage('Vérifications des script') {

      echo 'Vérification des scripts présents'
      sh 'sleep 2'
      }  

    stage('Téléchargement des archives') {
      echo 'Téléchargement des archives  (version: "' + tag + '" )'
      sh 'python "/var/lib/jenkins/workspace/buildFolder/Scripts/handleJson.py" "/var/lib/jenkins/workspace/buildFolder/output/response.json" ' + tag
      }     
  }
