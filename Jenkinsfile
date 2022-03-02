pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo 'Building..'
            }
        }
        stage('Test') {
            steps {
                echo 'Testing..'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying....'
            }
        }
       stage('Checkout') {
      steps {
           node {
    dir('RepoOne') {
        git url: 'https://github.com/raouny/NexusAPI.git'
    }


    sh('. RepoOne/build.sh')

}

       }
    }
    }
}