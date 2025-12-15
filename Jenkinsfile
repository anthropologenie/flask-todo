pipeline {
    agent any
    
    options {
        // Keep last 10 builds
        buildDiscarder(logRotator(numToKeepStr: '10'))
        // Timeout if build takes more than 30 minutes
        timeout(time: 30, unit: 'MINUTES')
        // Timestamps in console output
        timestamps()
    }
    
    triggers {
        // Schedule: Run daily at 2 AM
        cron('0 2 * * *')
        // Or run on every push to main branch
        // pollSCM('H/5 * * * *')  // Check SCM every 5 minutes
    }
    
    environment {
        // Python version (adjust based on your Jenkins setup)
        PYTHON = 'python3'
        // Virtual environment directory
        VENV_DIR = 'venv'
        // Reports directory
        REPORTS_DIR = 'reports'
    }
    
    stages {
        stage('Setup') {
            steps {
                echo '=========================================='
                echo 'Setting up test environment'
                echo '=========================================='
                
                // Clean previous reports
                sh 'rm -rf ${REPORTS_DIR} || true'
                sh 'mkdir -p ${REPORTS_DIR}'
                
                // Create virtual environment
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
                        -v \
                        -m "not slow" || true
                '''
            }
        }
        
        stage('Generate Reports') {
            steps {
                echo 'Publishing test results and coverage reports...'
                
                // Publish JUnit test results
                junit testResults: 'reports/junit.xml', allowEmptyResults: false
                
                // Publish HTML reports
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports',
                    reportFiles: 'test_report.html',
                    reportName: 'Pytest HTML Report',
                    reportTitles: 'Test Execution Report'
                ])
                
                // Publish coverage report
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports/coverage',
                    reportFiles: 'index.html',
                    reportName: 'Coverage Report',
                    reportTitles: 'Code Coverage Report'
                ])
                
                // Publish coverage to Jenkins (if Cobertura plugin installed)
                // cobertura coberturaReportFile: 'reports/coverage.xml'
            }
        }
    }
    
    post {
        always {
            echo 'Cleaning up...'
            // Archive test artifacts
            archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true
            
            // Clean workspace (optional)
            // cleanWs()
        }
        
        success {
            echo '✅ All tests passed successfully!'
            
            // Send email notification on success (configure email settings first)
            // emailext(
            //     subject: "✅ Jenkins Build Success: ${env.JOB_NAME} - Build #${env.BUILD_NUMBER}",
            //     body: """
            //         Build Status: SUCCESS
            //         Job: ${env.JOB_NAME}
            //         Build Number: ${env.BUILD_NUMBER}
            //         Build URL: ${env.BUILD_URL}
            //         
            //         All tests passed successfully!
            //         
            //         View reports:
            //         - Test Report: ${env.BUILD_URL}Pytest_20HTML_20Report/
            //         - Coverage: ${env.BUILD_URL}Coverage_20Report/
            //     """,
            //     to: 'your-email@example.com'
            // )
        }
        
        failure {
            echo '❌ Some tests failed!'
            
            // Send email notification on failure
            // emailext(
            //     subject: "❌ Jenkins Build Failed: ${env.JOB_NAME} - Build #${env.BUILD_NUMBER}",
            //     body: """
            //         Build Status: FAILED
            //         Job: ${env.JOB_NAME}
            //         Build Number: ${env.BUILD_NUMBER}
            //         Build URL: ${env.BUILD_URL}
            //         
            //         Some tests failed. Please check the reports.
            //         
            //         View reports:
            //         - Test Report: ${env.BUILD_URL}Pytest_20HTML_20Report/
            //         - Console Output: ${env.BUILD_URL}console
            //     """,
            //     to: 'your-email@example.com'
            // )
        }
        
        unstable {
            echo '⚠️ Build is unstable - some tests may have warnings'
        }
    }
}