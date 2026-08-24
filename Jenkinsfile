// CI pipeline (lint -> test -> sonarqube -> docker build -> trivy -> ecr push)
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    environment {
        AWS_REGION      = 'us-east-1'
        ECR_REPO        = 'fastapi-cicd-pipeline'
        AWS_ACCOUNT_ID  = credentials('aws-account-id')
        ECR_REGISTRY    = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        SONAR_SCANNER_HOME = tool 'sonar-scanner'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.IMAGE_TAG = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
                    }
                }
            }

        stage('Install & Lint') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --no-cache-dir -r requirements-dev.txt
                    black --check app tests
                    flake8 app tests
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    . .venv/bin/activate
                    pytest -v --junitxml=test-results.xml
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('sonarqube-server') {
                    sh """
                        ${SONAR_SCANNER_HOME}/bin/sonar-scanner \
                          -Dsonar.projectKey=fastapi-cicd-pipeline \
                          -Dsonar.sources=app \
                          -Dsonar.tests=tests \
                          -Dsonar.python.version=3.12
                    """
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Docker Build') {
            steps {
                script {
                    docker.build("${ECR_REPO}:${env.IMAGE_TAG}")
                }
            }
        }

        stage('Trivy Scan') {
            steps {
                sh """
                    trivy image --severity HIGH,CRITICAL --exit-code 1 --no-progress ${ECR_REPO}:${env.IMAGE_TAG}
                """
            }
        }

        stage('Push to ECR') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-creds']]) {
                    sh """
                        aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}
                        docker tag ${ECR_REPO}:${env.IMAGE_TAG} ${ECR_REGISTRY}/${ECR_REPO}:${env.IMAGE_TAG}
                        docker push ${ECR_REGISTRY}/${ECR_REPO}:${env.IMAGE_TAG}
                    """
                }
            }
        }
    }

    post {
        success {
            echo "CI pipeline completed: ${ECR_REPO}:${env.IMAGE_TAG}"
        }
        failure {
            echo "Pipeline failed, please check the console logs."
        }
        always {
            sh 'docker image prune -f || true'
        }
    }
}
