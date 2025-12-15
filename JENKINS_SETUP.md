# Jenkins Integration Guide for Flask-Todo Tests

## Prerequisites

### 1. Jenkins Plugins Required
Install these plugins in Jenkins:
- **Pipeline** (for Jenkinsfile support)
- **HTML Publisher Plugin** (for HTML reports)
- **JUnit Plugin** (for test results)
- **Cobertura Plugin** (optional, for coverage visualization)
- **Email Extension Plugin** (optional, for notifications)
- **Git Plugin** (if using Git repository)

### 2. Jenkins Configuration

#### A. Install Plugins
1. Go to Jenkins → Manage Jenkins → Manage Plugins
2. Click "Available" tab
3. Search and install:
   - HTML Publisher Plugin
   - JUnit Plugin
   - Pipeline
4. Restart Jenkins

#### B. Configure Python in Jenkins
1. Go to Manage Jenkins → Global Tool Configuration
2. Add Python installation or ensure Python 3.8+ is in system PATH

## Setting Up the Jenkins Job

### Option 1: Pipeline Job (Recommended)

1. **Create New Job**
   - Click "New Item"
   - Name: `flask-todo-tests`
   - Select "Pipeline"
   - Click OK

2. **Configure Job**
   - **Description**: Automated testing for Flask-Todo application
   
   - **Build Triggers**:
     - ✅ Build periodically: `H 2 * * *` (Daily at 2 AM)
     - Or: ✅ Poll SCM: `H/5 * * * *` (Every 5 minutes)
   
   - **Pipeline Section**:
     - Definition: "Pipeline script from SCM"
     - SCM: Git
     - Repository URL: `https://github.com/your-username/flask-todo`
     - Branch: `*/main`
     - Script Path: `Jenkinsfile`

3. **Save and Build**
   - Click "Save"
   - Click "Build Now"

### Option 2: Freestyle Job

1. **Create New Job**
   - Name: `flask-todo-tests-freestyle`
   - Select "Freestyle project"

2. **Source Code Management**
   - Git: Enter your repository URL
   - Branch: `*/main`

3. **Build Triggers**
   - Build periodically: `H 2 * * *`

4. **Build Steps**
   - Add build step: "Execute shell" (Linux/Mac) or "Execute Windows batch command"
   
   **For Linux/Mac:**
```bash
   #!/bin/bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ./run_tests.sh
```
   
   **For Windows:**
```batch
   python -m venv venv
   call venv\Scripts\activate.bat
   pip install -r requirements.txt
   run_tests.bat
```

5. **Post-build Actions**
   - Add: "Publish JUnit test result report"
     - Test report XMLs: `reports/junit.xml`
   
   - Add: "Publish HTML reports"
     - HTML directory: `reports`
     - Index page: `test_report.html`
     - Report title: `Pytest HTML Report`
   
   - Add: "Publish HTML reports" (again for coverage)
     - HTML directory: `reports/coverage`
     - Index page: `index.html`
     - Report title: `Coverage Report`

## Jenkins Schedule Syntax

| Schedule | Cron Expression | Description |
|----------|----------------|-------------|
| Every hour | `H * * * *` | Runs once per hour |
| Every 4 hours | `H */4 * * *` | Runs every 4 hours |
| Daily at 2 AM | `0 2 * * *` | Runs at 2:00 AM daily |
| Twice daily | `0 2,14 * * *` | Runs at 2 AM and 2 PM |
| Weekdays only | `0 8 * * 1-5` | Runs at 8 AM Mon-Fri |
| Every 5 min | `H/5 * * * *` | Runs every 5 minutes |
| Weekly on Monday | `0 1 * * 1` | Runs Monday at 1 AM |

**Note**: `H` = Hash (Jenkins distributes load by hashing job name)

## Viewing Reports in Jenkins

After build completes:

1. **Test Results**
   - Click on build number (e.g., #1)
   - Click "Test Result" in left menu
   - View pass/fail statistics

2. **HTML Report**
   - Click "Pytest HTML Report" in left menu
   - View detailed test execution report

3. **Coverage Report**
   - Click "Coverage Report" in left menu
   - View code coverage statistics

4. **Console Output**
   - Click "Console Output"
   - View full execution logs

## Email Notifications Setup

1. **Configure Email**
   - Go to Manage Jenkins → Configure System
   - Scroll to "Extended E-mail Notification"
   - Configure SMTP server settings

2. **Uncomment email blocks in Jenkinsfile**
   - Replace `your-email@example.com` with actual email
   - Customize subject and body as needed

## Troubleshooting

### Issue: "python not found"
**Solution**: Install Python or add to PATH in Jenkins configuration

### Issue: "Permission denied" on scripts
**Solution**: Make scripts executable
```bash
chmod +x run_tests.sh
```

### Issue: HTML report not showing
**Solution**: 
1. Install HTML Publisher Plugin
2. Configure Content Security Policy:
```bash
   java -Djenkins.model.DirectoryBrowserSupport.CSP="" -jar jenkins.war
```

### Issue: Virtual environment errors
**Solution**: Delete venv folder and let Jenkins recreate it:
```bash
rm -rf venv
```

## Best Practices

1. **Use separate Jenkins job for different test suites**
   - Unit tests (fast, run frequently)
   - Integration tests (slower, run less often)
   - E2E tests (slowest, run nightly)

2. **Archive artifacts**
   - Keep test reports for at least 10 builds
   - Archive test databases for debugging

3. **Set up notifications**
   - Email on failure
   - Slack/Teams integration for team visibility

4. **Monitor test trends**
   - Track test execution time
   - Monitor flaky tests
   - Review coverage trends