pipeline {
  agent any

  environment {
    // DockerHub image that already exists
    IMAGE = "2022bcs0209harshitha/mlops-app:latest"

    // FastAPI app uses port 8000 inside container
    CONTAINER_PORT = "8000"

    // Unique container name per build
    CONTAINER_NAME = "wine_infer_${env.BUILD_NUMBER}"

    // IMPORTANT: use a fixed network that BOTH Jenkins and inference containers can join
    // Create it once on your PC:  docker network create jenkins_net
    NET = "jenkins_net"

    // Health endpoint is GET /
    HEALTH_URL = "http://${CONTAINER_NAME}:${CONTAINER_PORT}/"

    // Predict endpoint is POST /predict
    PREDICT_URL = "http://${CONTAINER_NAME}:${CONTAINER_PORT}/predict"
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

    stage('Ensure Docker Network') {
      steps {
        sh '''
          set -e
          echo "Ensuring docker network exists: ${NET}"
          docker network inspect ${NET} >/dev/null 2>&1 || docker network create ${NET}
        '''
      }
    }

    stage('Run Inference Container') {
      steps {
        sh '''
          set -e
          echo "Starting container ${CONTAINER_NAME} on network ${NET}..."
          docker run -d --rm --name ${CONTAINER_NAME} --network ${NET} ${IMAGE}
          docker ps | grep ${CONTAINER_NAME}
        '''
      }
    }

    stage('Wait for Service Readiness') {
      steps {
        sh '''
          set -e
          echo "Readiness URL: ${HEALTH_URL}"

          echo "---- Debug: DNS resolution ----"
          getent hosts ${CONTAINER_NAME} || true

          echo "---- Debug: Container logs (last 50 lines) ----"
          docker logs --tail 50 ${CONTAINER_NAME} || true

          echo "---- Debug: Try curl once (may fail if not ready) ----"
          curl -i ${HEALTH_URL} || true

          echo "---- Waiting for HTTP 200 (timeout 120s) ----"
          timeout 120 bash -c 'until [ "$(curl -s -o /dev/null -w "%{http_code}" ${HEALTH_URL})" = "200" ]; do sleep 2; done'

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

# Your app returns these keys
for k in ["name", "roll_no", "wine_quality"]:
    if k not in data:
        print(f"FAIL: Missing key '{k}'. Keys:", list(data.keys()))
        sys.exit(1)

# wine_quality should be int
wq = data["wine_quality"]
if not isinstance(wq, int):
    print("FAIL: wine_quality is not int:", type(wq), wq)
    sys.exit(1)

print("PASS: Valid inference OK -> wine_quality =", wq, "| name =", data["name"], "| roll_no =", data["roll_no"])
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

          # For invalid body FastAPI usually returns 422 (or any 4xx)
          if [ "$CODE" -ge 200 ] && [ "$CODE" -lt 300 ]; then
            echo "FAIL: Expected error for invalid request but got 2xx"
            exit 1
          fi

          python3 - << PY
import json, sys
body = """$BODY"""
try:
    data = json.loads(body)
except Exception as e:
    print("FAIL: Error response not JSON:", e)
    sys.exit(1)

# FastAPI validation error has "detail"
if "detail" not in data:
    print("FAIL: Expected 'detail' field in error response. Keys:", list(data.keys()))
    sys.exit(1)

print("PASS: Invalid request produced validation error (detail present).")
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
        echo "Post cleanup..."
        docker stop ${CONTAINER_NAME} || true
      '''
    }
  }
}
