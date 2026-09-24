import re

with open('docker-compose.yml', 'r') as f:
    content = f.read()

# Replace backend environment with env_file
content = re.sub(r'    environment:\n(?:      - .*\n)+', '    env_file:\n      - ./backend/.env\n', content)

# Append prometheus and grafana
observability = """
  # ---------------------------------------------------------------------------
  # Prometheus
  # ---------------------------------------------------------------------------
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
    depends_on:
      - backend

  # ---------------------------------------------------------------------------
  # Grafana
  # ---------------------------------------------------------------------------
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
"""
content += observability

with open('docker-compose.yml', 'w') as f:
    f.write(content)
