pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "2022bcs0209harshitha/mlops-app"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python Virtual Environment') {
            steps {
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('Train Model') {
            steps {
                sh '''
                . venv/bin/activate
                python scripts/train.py
                '''
            }
        }

        stage('Read Accuracy') {
    steps {
        script {
            def metrics = readJSON file: 'outputs/results.json'
            env.CURRENT_ACCURACY = metrics.r2.toString()
            echo "Current R2 (used as accuracy): ${env.CURRENT_ACCURACY}"
        }
    }
}


        stage('Compare Accuracy') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'best-accuracy', variable: 'BEST_ACC')]) {
                        if (env.CURRENT_ACCURACY.toFloat() > BEST_ACC.toFloat()) {
                            echo "New model is better. Will build Docker image."
                            env.BUILD_IMAGE = "true"
                        } else {
                            echo "Model did not improve. Skipping Docker build/push."
                            env.BUILD_IMAGE = "false"
                        }
                    }
                }
            }
        }

        stage('Build Docker Image') {
            when {
                expression { env.BUILD_IMAGE == "true" }
            }
            steps {
                sh """
                docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} .
                docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${DOCKER_IMAGE}:latest
                """
            }
        }

        stage('Push Docker Image') {
            when {
                expression { env.BUILD_IMAGE == "true" }
            }
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                    sh """
                    echo \$PASS | docker login -u \$USER --password-stdin
                    docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}
                    docker push ${DOCKER_IMAGE}:latest
                    """
                }
            }
        }
    }

  post {
    always {
        archiveArtifacts artifacts: 'app/artifacts/**, outputs/**', allowEmptyArchive: true
    }
}

