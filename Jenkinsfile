pipeline {
  agent any

  environment {
    IMAGE = "2022bcs0209harshitha/mlops-app:latest"

    HOST_PORT = "8000"
    CONTAINER_PORT = "8000"
    CONTAINER_NAME = "wine_infer_${env.BUILD_NUMBER}"

    // Your app health is GET /
    HEALTH_URL = "http://127.0.0.1:${HOST_PORT}/"

    // Your predict endpoint
    PREDICT_URL = "http://127.0.0.1:${HOST_PORT}/predict"
  }

  stages {

    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Pull Docker Image') {
      steps {
        sh '''
          set -e
          echo "Pulling image: ${IMAGE}"
          docker pull ${IMAGE}
        '''
      }
    }

    stage('Run Inference Container') {
      steps {
        sh '''
          set -e
          echo "Starting container ${CONTAINER_NAME}..."
          docker run -d --rm --name ${CONTAINER_NAME} -p ${HOST_PORT}:${CONTAINER_PORT} ${IMAGE}
          docker ps | grep ${CONTAINER_NAME}
        '''
      }
    }

    stage('Wait for Service Readiness') {
      steps {
        sh '''
          set -e
          echo "Waiting for readiness at ${HEALTH_URL}..."
          timeout 60 bash -c 'until [ "$(curl -s -o /dev/null -w "%{http_code}" ${HEALTH_URL})" = "200" ]; do sleep 2; done'
          echo "Service is READY."
        '''
      }
    }

    stage('Valid Request Test') {
      steps {
        sh '''
          set -e
          echo "VALID request body:"
          cat tests/valid.json
          echo ""

          RESP=$(curl -s -w "\\n%{http_code}" -H "Content-Type: application/json" -d @tests/valid.json ${PREDICT_URL})
          BODY=$(echo "$RESP" | head -n 1)
          CODE=$(echo "$RESP" | tail -n 1)

          echo "Status Code: $CODE"
          echo "Response Body: $BODY"

          if [ "$CODE" -lt 200 ] || [ "$CODE" -ge 300 ]; then
            echo "FAIL: Expected 2xx for valid request"
            exit 1
          fi

          python3 - << PY
import json, sys
body = """$BODY"""
try:
    data = json.loads(body)
except Exception as e:
    print("FAIL: Response is not valid JSON:", e)
    sys.exit(1)

# Validate required fields returned by your app.py
for k in ["name", "roll_no", "wine_quality"]:
    if k not in data:
        print(f"FAIL: Missing key '{k}' in response. Keys:", list(data.keys()))
        sys.exit(1)

# Validate wine_quality is int
wq = data["wine_quality"]
if not isinstance(wq, int):
    print("FAIL: wine_quality is not int:", type(wq), wq)
    sys.exit(1)

print("PASS: Valid inference OK. wine_quality =", wq, "name =", data["name"], "roll_no =", data["roll_no"])
PY
        '''
      }
    }

    stage('Invalid Request Test') {
      steps {
        sh '''
          set -e
          echo "INVALID request body:"
          cat tests/invalid.json
          echo ""

          RESP=$(curl -s -w "\\n%{http_code}" -H "Content-Type: application/json" -d @tests/invalid.json ${PREDICT_URL})
          BODY=$(echo "$RESP" | head -n 1)
          CODE=$(echo "$RESP" | tail -n 1)

          echo "Status Code: $CODE"
          echo "Response Body: $BODY"

          # FastAPI validation usually returns 422 for bad body
          if [ "$CODE" -ge 200 ] && [ "$CODE" -lt 300 ]; then
            echo "FAIL: Expected error code for invalid request, got 2xx"
            exit 1
          fi

          python3 - << PY
import json, sys
body = """$BODY"""
try:
    data = json.loads(body)
except:
    if not body.strip():
        print("FAIL: Empty error body")
        sys.exit(1)
    print("PASS: Invalid request returned non-JSON error body (acceptable).")
    sys.exit(0)

# FastAPI error format usually has "detail"
msg = data.get("detail", "")
if not msg:
    print("FAIL: No meaningful error message found.")
    sys.exit(1)

print("PASS: Invalid request returned meaningful error detail.")
PY
        '''
      }
    }

    stage('Stop Container') {
      steps {
        sh '''
          echo "Stopping container..."
          docker stop ${CONTAINER_NAME} || true
        '''
      }
    }
  }

  post {
    always {
      sh '''
        echo "Cleanup: stop container if still running..."
        docker stop ${CONTAINER_NAME} || true
      '''
    }
  }
}
