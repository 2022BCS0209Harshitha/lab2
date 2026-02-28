pipeline {
  agent any

  environment {
    IMAGE = "2022bcs0209harshitha/mlops-app:latest"
    CONTAINER_PORT = "8000"
    CONTAINER_NAME = "wine_infer_${env.BUILD_NUMBER}"
    NET = "jenkins_net_${env.JOB_NAME}"

    // IMPORTANT: use container DNS name inside the same Docker network
    HEALTH_URL = "http://${CONTAINER_NAME}:${CONTAINER_PORT}/"
    PREDICT_URL = "http://${CONTAINER_NAME}:${CONTAINER_PORT}/predict"
  }

  stages {

    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Pull Docker Image') {
      steps {
        sh '''
          set -e
          docker pull ${IMAGE}
        '''
      }
    }

    stage('Create Docker Network') {
      steps {
        sh '''
          set -e
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
          echo "Waiting for readiness at ${HEALTH_URL}..."
          timeout 90 bash -c 'until [ "$(curl -s -o /dev/null -w "%{http_code}" ${HEALTH_URL})" = "200" ]; do sleep 2; done'
          echo "Service is READY."
        '''
      }
    }

    stage('Valid Request Test') {
      steps {
        sh '''
          set -e
          echo "VALID request:"
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
data = json.loads(body)

for k in ["name", "roll_no", "wine_quality"]:
    if k not in data:
        print("FAIL: Missing key", k, "Keys:", list(data.keys()))
        sys.exit(1)

if not isinstance(data["wine_quality"], int):
    print("FAIL: wine_quality not int:", type(data["wine_quality"]), data["wine_quality"])
    sys.exit(1)

print("PASS: wine_quality =", data["wine_quality"], "name =", data["name"], "roll_no =", data["roll_no"])
PY
        '''
      }
    }

    stage('Invalid Request Test') {
      steps {
        sh '''
          set -e
          echo "INVALID request:"
          cat tests/invalid.json
          echo ""

          RESP=$(curl -s -w "\\n%{http_code}" -H "Content-Type: application/json" -d @tests/invalid.json ${PREDICT_URL})
          BODY=$(echo "$RESP" | head -n 1)
          CODE=$(echo "$RESP" | tail -n 1)

          echo "Status Code: $CODE"
          echo "Response Body: $BODY"

          if [ "$CODE" -ge 200 ] && [ "$CODE" -lt 300 ]; then
            echo "FAIL: Expected error for invalid request but got 2xx"
            exit 1
          fi

          python3 - << PY
import json
body = """$BODY"""
data = json.loads(body)
if "detail" not in data:
    raise SystemExit("FAIL: Expected 'detail' in error response")
print("PASS: Invalid request produced validation error detail.")
PY
        '''
      }
    }

    stage('Stop Container') {
      steps {
        sh '''
          docker stop ${CONTAINER_NAME} || true
        '''
      }
    }
  }

  post {
    always {
      sh '''
        docker stop ${CONTAINER_NAME} || true
        docker network rm ${NET} || true
      '''
    }
  }
}
