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
           git  url: 'https://github.com/raouny/NexusAPI.git'

       }
    }
    }
}