pipeline {
    agent any

    environment {
        REPO_URL     = 'https://github.com/nileshyav/focusApp.git'
        BRANCH       = 'master'
        DOCKER_IMAGE = 'inilesh/todoapp'
    }

    stages {
        stage('Checkout') {
            steps {
                // Stage 1: Checkout from GitHub using Jenkins Git plugin
                git branch: env.BRANCH, url: env.REPO_URL

                script {
                    env.GIT_COMMIT_SHORT = sh(
                        script: 'git rev-parse --short HEAD',
                        returnStdout: true
                    ).trim()
                }
            }
        }

        stage('Build Image') {
            steps {
                // Stage 2: Directly build and tag the Docker Hub repository image
                sh """
                    docker build \
                        -t ${DOCKER_IMAGE}:${GIT_COMMIT_SHORT} \
                        -t ${DOCKER_IMAGE}:latest \
                        .
                """
            }
        }

        stage('Push to DockerHub') {
            steps {
                // Stage 3: Authenticate and push to Docker Hub repository
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-cred',
                    usernameVariable: 'DOCKERHUB_USER',
                    passwordVariable: 'DOCKERHUB_PASS'
                )]) {
                    sh """
                        echo "\$DOCKERHUB_PASS" | docker login -u "\$DOCKERHUB_USER" --password-stdin
                        docker push ${DOCKER_IMAGE}:${GIT_COMMIT_SHORT}
                        docker push ${DOCKER_IMAGE}:latest
                        docker logout
                    """
                }
            }
        }
    }
}
