@echo off
REM Flask-Todo Test Execution Script for Jenkins (Windows)

echo ==========================================
echo Flask-Todo Test Suite Execution
echo ==========================================
echo Start Time: %date% %time%
echo.

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
)

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Create reports directory
if not exist reports mkdir reports

REM Run tests with multiple report formats
echo.
echo Running test suite...
pytest tests\ ^
    --html=reports/test_report.html ^
    --self-contained-html ^
    --junitxml=reports/junit.xml ^
    --cov=app ^
    --cov-report=html:reports/coverage ^
    --cov-report=xml:reports/coverage.xml ^
    --json-report ^
    --json-report-file=reports/test_report.json ^
    -v

echo.
echo ==========================================
echo Test Execution Completed
echo End Time: %date% %time%
echo ==========================================
echo.
echo Reports generated:
echo   - HTML Report: reports\test_report.html
echo   - JUnit XML: reports\junit.xml
echo   - Coverage HTML: reports\coverage\index.html
echo   - Coverage XML: reports\coverage.xml
echo   - JSON Report: reports\test_report.json