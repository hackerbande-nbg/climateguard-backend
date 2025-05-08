pipeline {
    agent {
       label "hamster"
    }

    environment {
        ENV_FILE = '.env'
    }
    //pulls prod env vars for deployment
    //different --project-name
    //otherwise the same as run_stage.groovy
    stages {
        stage('prep') {
            steps {
                sh 'pip list'
                sh 'docker --version'
                sh 'docker compose --version'
                sh 'python3 --version'
                sh 'pip3 --version'
                sh 'pip install -r requirements_dev.txt'

            }
        }
        stage('lint python') {
            steps {
                sh 'python3 -m flake8 --config devops/flake8.ini'
            }
        }
        stage('Pull .env from Jenkins Secrets') {
            steps {
                withCredentials([file(credentialsId: 'quantum_prod_dotenv', variable: 'ENV_FILE_CONTENT')]) {
                    writeFile file: "${ENV_FILE}", text: readFile(ENV_FILE_CONTENT)
                }
            }
        }

        stage('Build and Run Docker Compose') {
            steps {
                sh 'docker compose -p quantum_prod -f docker-compose.yml up -d --build'
            }
        }
        stage('apply alembic changes') {
            steps {
                sh 'docker exec quantum_web_prod alembic upgrade head'
            }
        }
    }
}
