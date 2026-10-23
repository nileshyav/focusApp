pipeline {
    agent any

    options {
        buildDiscarder(logRotator(numToKeepStr: '30'))
        disableConcurrentBuilds()
        timestamps()
    }

    parameters {
        string(
            name: 'AWS_ACCOUNT_ID',
            defaultValue: '',
            description: '12-digit AWS Account ID hosting the Amazon ECR registry (e.g., 123456789012)'
        )
        string(
            name: 'AWS_REGION',
            defaultValue: 'us-east-1',
            description: 'AWS Region for Amazon ECR (e.g., us-east-1, eu-west-1)'
        )
        string(
            name: 'ECR_REPO_NAME',
            defaultValue: 'ai-project-1',
            description: 'Name of the Amazon ECR repository'
        )
        string(
            name: 'GIT_REPO_URL',
            defaultValue: '',
            description: 'Optional: Public GitHub HTTPS Clone URL. If left empty, Jenkins uses SCM checkout from the job configuration.'
        )
        string(
            name: 'GIT_BRANCH',
            defaultValue: 'main',
            description: 'Git branch to build'
        )
    }

    environment {
        DOCKER_BUILDKIT = '1'
        ECR_REGISTRY    = "${params.AWS_ACCOUNT_ID}.dkr.ecr.${params.AWS_REGION}.amazonaws.com"
        IMAGE_URI       = "${params.AWS_ACCOUNT_ID}.dkr.ecr.${params.AWS_REGION}.amazonaws.com/${params.ECR_REPO_NAME}"
    }

    stages {
        stage('Validate Parameters') {
            steps {
                script {
                    if (!params.AWS_ACCOUNT_ID?.trim()) {
                        error("Parameter AWS_ACCOUNT_ID is required. Please provide a valid 12-digit AWS Account ID.")
                    }
                    if (!params.AWS_REGION?.trim()) {
                        error("Parameter AWS_REGION is required.")
                    }
                    if (!params.ECR_REPO_NAME?.trim()) {
                        error("Parameter ECR_REPO_NAME is required.")
                    }
                }
            }
        }

        stage('Checkout Source Code') {
            steps {
                script {
                    if (params.GIT_REPO_URL?.trim()) {
                        echo "Checking out repository from: ${params.GIT_REPO_URL} (branch: ${params.GIT_BRANCH})"
                        git branch: params.GIT_BRANCH, url: params.GIT_REPO_URL
                    } else {
                        echo "Checking out repository via Jenkins default SCM"
                        checkout scm
                    }

                    // Extract the 7-character short commit hash for immutable artifact tagging
                    env.GIT_COMMIT_SHORT = sh(
                        script: 'git rev-parse --short HEAD',
                        returnStdout: true
                    ).trim()

                    echo "Target build commit: ${env.GIT_COMMIT_SHORT}"
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building multi-stage Docker image..."
                    echo "Target Tags: ${env.IMAGE_URI}:${env.GIT_COMMIT_SHORT} and ${env.IMAGE_URI}:latest"

                    sh """
                        docker build \
                            -t ${env.IMAGE_URI}:${env.GIT_COMMIT_SHORT} \
                            -t ${env.IMAGE_URI}:latest \
                            .
                    """
                }
            }
        }

        stage('Push Image to AWS ECR') {
            steps {
                script {
                    echo "Logging into Amazon ECR in ${params.AWS_REGION} using EC2 IAM Role..."
                    sh """
                        aws ecr get-login-password --region ${params.AWS_REGION} | \
                        docker login --username AWS --password-stdin ${env.ECR_REGISTRY}
                    """

                    echo "Pushing immutable commit tag: ${env.IMAGE_URI}:${env.GIT_COMMIT_SHORT}"
                    sh "docker push ${env.IMAGE_URI}:${env.GIT_COMMIT_SHORT}"

                    echo "Pushing latest tag: ${env.IMAGE_URI}:latest"
                    sh "docker push ${env.IMAGE_URI}:latest"
                }
            }
        }
    }

    post {
        success {
            echo "Successfully built and pushed ${env.IMAGE_URI}:${env.GIT_COMMIT_SHORT} and ${env.IMAGE_URI}:latest to AWS ECR."
        }
        failure {
            echo "Pipeline failed during build or push to AWS ECR. Please review the console logs above."
        }
    }
}
