pipeline {
    agent any
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
    }
    
    triggers {
        cron('H 2 * * *')
    }
    
    environment {
        PYTHON = 'python3'
        VENV_DIR = 'venv'
        REPORTS_DIR = 'reports'
    }
    
    stages {
        stage('Setup') {
            steps {
                echo '=========================================='
                echo 'Setting up test environment'
                echo '=========================================='
                
                sh 'rm -rf ${REPORTS_DIR} || true'
                sh 'mkdir -p ${REPORTS_DIR}'
                sh 'mkdir -p instance'
                
                sh '''
                    ${PYTHON} -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                '''
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo 'Installing Python dependencies...'
                sh '''
                    . ${VENV_DIR}/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Setup Test Database') {
            steps {
                echo 'Creating test database with sample data...'
                sh '''
                    . ${VENV_DIR}/bin/activate
                    python3 tests/setup_test_db.py
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                echo '=========================================='
                echo 'Running Flask-Todo Test Suite'
                echo '=========================================='
                
                sh '''
                    . ${VENV_DIR}/bin/activate
                    
                    pytest tests/ \
                        --html=${REPORTS_DIR}/test_report.html \
                        --self-contained-html \
                        --junitxml=${REPORTS_DIR}/junit.xml \
                        --cov=app \
                        --cov-report=html:${REPORTS_DIR}/coverage \
                        --cov-report=xml:${REPORTS_DIR}/coverage.xml \
                        --json-report \
                        --json-report-file=${REPORTS_DIR}/test_report.json \
                        -v || true
                '''
            }
        }
        
        stage('Publish Reports') {
            steps {
                echo 'Publishing test results...'
                
                // JUnit test results (this always works)
                junit testResults: 'reports/junit.xml', allowEmptyResults: false
                
                // Archive all reports as artifacts
                archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true
                
                echo 'Reports available in build artifacts'
            }
        }
    }
    
    post {
        always {
            echo 'Build complete!'
        }
        success {
            echo '✅ All tests passed successfully!'
        }
        failure {
            echo '❌ Some tests failed - check reports in artifacts'
        }
    }
}