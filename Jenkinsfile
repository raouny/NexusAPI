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
        stage('Checkout external proj') {
        steps {
            git branch: 'my_specific_branch',
                credentialsId: 'my_cred_id',
                url: 'ssh://git@test.com/proj/test_proj.git'

            sh "ls -lat"
        }
    }
    }
}