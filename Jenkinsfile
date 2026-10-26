pipeline {
    agent any

    environment {
        DOCKER_BUILDKIT = '1'
        DOCKER_IMAGE    = 'inilesh/todoapp'
    }

    stages {
        stage('Prepare') {
            steps {
                script {
                    // Extract short Git commit hash from the repository checked out by Jenkins
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

        stage('Update Manifest in Git') {
            environment {
                GIT_REPO_NAME = 'focusApp'
                GIT_USER_NAME = 'nileshyav'
            }
            steps {
                script {
                    // Stage 4: Update image tag in k8s/deployment.yaml and push to GitHub for Argo CD
                    withCredentials([string(credentialsId: 'github_secret', variable: 'GITHUB_TOKEN')]) {
                        sh """
                            git config user.email "nileshyaduvanshi@outlook.com"
                            git config user.name "${GIT_USER_NAME}"

                            # Replace existing image tag with the new immutable commit hash
                            sed -i "s|image: ${DOCKER_IMAGE}:.*|image: ${DOCKER_IMAGE}:${GIT_COMMIT_SHORT}|" k8s/deployment.yaml

                            git add k8s/deployment.yaml
                            git commit -m "ci: update deployment image tag to ${GIT_COMMIT_SHORT} [skip ci]" || echo "No changes to commit"
                            git push https://${GIT_USER_NAME}:${GITHUB_TOKEN}@github.com/${GIT_USER_NAME}/${GIT_REPO_NAME}.git HEAD:master
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            // Post Cleanup: Remove local Docker images and dangling layers to save disk space
            sh """
                docker rmi ${DOCKER_IMAGE}:${GIT_COMMIT_SHORT} || true
                docker rmi ${DOCKER_IMAGE}:latest || true
                docker image prune -f || true
            """
        }
    }
}
