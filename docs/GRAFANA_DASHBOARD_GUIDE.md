# Guide Dashboard Temps Réel avec Grafana

**Projet:** Promo Load Analyzer - Phase 2
**Date:** 2025-10-28
**Objectif:** Implémenter un dashboard temps réel pour monitorer les tests de charge K6

---

## Table des Matières

1. [Architecture & Fonctionnement](#architecture--fonctionnement)
2. [Avantages pour le Projet](#avantages-pour-le-projet)
3. [Technologies & Stack](#technologies--stack)
4. [Options d'Implémentation](#options-dimplémentation)
5. [Plan d'Implémentation Détaillé](#plan-dimplémentation-détaillé)
6. [Configuration Pas à Pas](#configuration-pas-à-pas)
7. [Dashboards Disponibles](#dashboards-disponibles)
8. [Intégration avec le Code Existant](#intégration-avec-le-code-existant)
9. [Sécurité & Production](#sécurité--production)
10. [Troubleshooting](#troubleshooting)

---

## Architecture & Fonctionnement

### Vue d'Ensemble

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   K6 Tests   │─────▶│   InfluxDB   │─────▶│   Grafana    │◀────│ Marketing    │
│  (Python)    │      │  (Time Series│      │  (Dashboard) │     │ Team Browser │
└──────────────┘      │   Database)  │      └──────────────┘      └──────────────┘
                      └──────────────┘
```

### Flux de Données en Temps Réel

1. **K6 exécute un test** avec `--out influxdb`
2. **Métriques envoyées en streaming** vers InfluxDB toutes les 1s (configurable)
3. **InfluxDB stocke** les métriques avec timestamps précis (séries temporelles)
4. **Grafana interroge** InfluxDB et affiche les données avec rafraîchissement automatique
5. **L'utilisateur voit** les graphiques se mettre à jour en temps réel (SSE - Server-Sent Events)

### Métriques Capturées

K6 envoie automatiquement vers InfluxDB :

- **Response Times:** p95, p99, avg, min, max
- **Request Rates:** requests/sec, failed requests
- **Error Rates:** % erreurs HTTP, codes de statut
- **Virtual Users:** nombre de VUs actifs
- **Throughput:** données reçues/envoyées
- **Checks:** taux de succès des validations
- **Custom Tags:** testid, environment, promo_type, etc.

---

## Avantages pour le Projet

### Pour l'Équipe Marketing (Non-Technique)

✅ **Visualisation en temps réel** : Voir immédiatement si le site ralentit
✅ **Dashboard simple** : Jauges colorées (vert/orange/rouge) sans terme technique
✅ **Détection précoce** : Stopper un test destructif avant dommage
✅ **Historique visuel** : Comparer plusieurs promos Black Friday sur graphiques
✅ **Alertes automatiques** : Notification Slack si erreur > 5%

### Pour l'Équipe Technique

✅ **Debugging facilité** : Corréler charge K6 avec métriques serveur (CPU, RAM)
✅ **Analyse post-mortem** : Rejouer visuellement un test après incident
✅ **Capacité planning** : Identifier le point de rupture exact (VUs max)
✅ **Multi-tests** : Comparer PROD vs PREPROD sur un seul écran
✅ **Intégration CI/CD** : Dashboard accessible par toute l'équipe

---

## Technologies & Stack

### Composants Requis

| Composant | Version | Rôle | Ressources |
|-----------|---------|------|------------|
| **InfluxDB** | 2.x (ou 1.8+) | Base de données de séries temporelles | ~500MB RAM, 10GB disque |
| **Grafana** | 10.x+ | Plateforme de visualisation | ~200MB RAM |
| **K6** | 0.47+ | Load testing (déjà installé) | Déjà présent |
| **xk6-output-influxdb** | Latest | Extension K6 pour InfluxDB 2.x | Build Go requis |

### Options de Déploiement

#### Option 1 : Docker Compose (RECOMMANDÉ pour début)
- ✅ Setup rapide (5-10 min)
- ✅ Isolation des services
- ✅ Facile à détruire/recréer
- ❌ Nécessite Docker Desktop (macOS) ou Docker Engine

#### Option 2 : Binaires Natifs (Performance Max)
- ✅ Meilleure performance
- ✅ Intégration système native
- ❌ Configuration manuelle
- ❌ Moins portable

#### Option 3 : Grafana Cloud (SaaS)
- ✅ Zéro maintenance infrastructure
- ✅ Haute disponibilité
- ❌ Coût (gratuit jusqu'à 50GB/mois)
- ❌ Dépendance externe

---

## Options d'Implémentation

### Comparaison Détaillée

| Critère | Docker Compose | Natif | Grafana Cloud |
|---------|----------------|-------|---------------|
| **Setup Time** | 10 min | 30 min | 5 min |
| **Complexité** | Faible | Moyenne | Très faible |
| **Performance** | Bonne | Excellente | Bonne |
| **Coût** | Gratuit | Gratuit | Gratuit < 50GB |
| **Maintenance** | Faible | Moyenne | Nulle |
| **Production Ready** | ⚠️ Avec tuning | ✅ | ✅ |
| **Contrôle Total** | ✅ | ✅ | ❌ |
| **Backup Local** | ✅ | ✅ | ❌ |

### Recommandation pour Promo Load Analyzer

**Phase 2 MVP (Développement) :**
→ **Docker Compose** (rapidité, isolation, facilité)

**Phase 2 Production (Black Friday) :**
→ **Grafana Cloud** (zéro downtime, alerting intégré, partage facile avec équipe)

**Phase 3 (Long terme) :**
→ **Natif sur serveur dédié** (contrôle total, historique illimité)

---

## Plan d'Implémentation Détaillé

### Phase 2.1 - Setup Infrastructure (2-3h)

**Objectifs :**
- Infrastructure Grafana + InfluxDB fonctionnelle
- Premier test K6 visible en temps réel
- Dashboard de base importé

**Tâches :**
1. Créer `docker-compose.yml` avec InfluxDB 2.x + Grafana
2. Configurer volumes persistants pour données
3. Builder K6 avec extension `xk6-output-influxdb`
4. Tester connexion K6 → InfluxDB
5. Importer dashboard K6 officiel (ID: 2587)
6. Valider visualisation temps réel

**Livrables :**
- ✅ Docker Compose opérationnel
- ✅ K6 custom build dans `/bin`
- ✅ Dashboard accessible à `http://localhost:3000`

---

### Phase 2.2 - Intégration Code Python (3-4h)

**Objectifs :**
- K6 Executor modifié pour InfluxDB output
- Tags personnalisés (testid, promo_type, environment)
- Génération automatique de testid unique

**Tâches :**
1. Modifier `src/k6_executor.py` :
   - Ajouter flag `--out xk6-influxdb=http://localhost:8086`
   - Passer variables d'environnement InfluxDB
   - Générer `testid` unique (UUID + timestamp)
   - Ajouter tags custom via `-e`

2. Créer `src/monitoring/dashboard_manager.py` :
   - Lancer/stopper Docker Compose
   - Vérifier santé InfluxDB/Grafana
   - Récupérer URL dashboard pour l'utilisateur

3. Enrichir tags K6 dans templates :
   - `testid`: UUID unique du test
   - `promo_type`: striked_price | auto_cart | manual_code
   - `environment`: prod | preprod
   - `intensity`: light | medium | heavy
   - `page_type`: product | homepage | category

**Livrables :**
- ✅ Tests K6 tagués automatiquement
- ✅ Dashboard filtrable par test/promo/environnement
- ✅ Fonction Python pour ouvrir dashboard

---

### Phase 2.3 - Dashboard Custom Marketing (4-5h)

**Objectifs :**
- Dashboard adapté au vocabulaire marketing (pas de jargon technique)
- Jauges de santé visibles (vert/orange/rouge)
- Annotations automatiques (début test, détection erreur)

**Composants Dashboard :**

1. **Panel "Santé du Site" (Gauge)**
   - Vert (A) : p95 < 1000ms, errors < 0.1%
   - Orange (B-C) : p95 < 2000ms, errors < 1%
   - Rouge (D-F) : p95 > 2000ms ou errors > 1%

2. **Panel "Utilisateurs Simultanés"**
   - Graphique temporel des VUs actifs
   - Ligne horizontale "Capacité max estimée"

3. **Panel "Temps de Réponse"**
   - Courbe p50, p95, p99
   - Seuil 2s (limite acceptable)

4. **Panel "Taux d'Erreur"**
   - % erreurs HTTP
   - Codes de statut (4xx, 5xx)

5. **Panel "Impact Promo"**
   - Comparaison baseline (sans promo) vs avec promo
   - Surcoût serveur en %

6. **Alertes Visuelles**
   - Annotation rouge si test avorté (thresholds)
   - Annotation orange si > 1% erreurs

**Livrables :**
- ✅ Dashboard JSON exporté dans `/dashboards/promo_marketing.json`
- ✅ Import automatique au démarrage Docker Compose
- ✅ Documentation utilisateur avec captures d'écran

---

### Phase 2.4 - Alerting Slack (2-3h)

**Objectifs :**
- Notifications Slack en cas d'anomalie
- Canal dédié `#load-testing-alerts`
- Messages avec contexte (URL, promo, erreur)

**Scénarios d'Alerte :**

| Condition | Sévérité | Message Slack |
|-----------|----------|---------------|
| Erreurs > 5% | 🔴 CRITICAL | "Test **SONY GM-1** : 12% erreurs sur ipln.fr. Arrêt immédiat recommandé." |
| p95 > 3000ms | 🟠 WARNING | "Test **Panasonic S5** : Temps réponse dégradé (p95: 3.2s). Site ralenti." |
| Test avorté | 🟠 WARNING | "Test **BF Landing** : Arrêt automatique (threshold dépassé)." |
| Test complété | 🟢 SUCCESS | "Test **Homepage PREPROD** : Grade A (97/100). 🎉" |

**Implémentation :**
1. Ajouter Grafana Contact Point (Slack webhook)
2. Créer Alerting Rules dans Grafana
3. Enrichir alertes avec tags K6 (context)
4. Tester avec test volontairement en échec

**Livrables :**
- ✅ Alertes configurées dans Grafana
- ✅ Webhook Slack opérationnel
- ✅ Tests d'alerte validés

---

### Phase 2.5 - Bouton Stop d'Urgence (3-4h)

**Objectifs :**
- Dashboard avec bouton "STOP TEST" cliquable
- Communication bidirectionnelle Grafana ↔ K6
- Arrêt gracieux du test en cours

**Architecture Technique :**

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Grafana    │─────▶│ Python API   │─────▶│  K6 Process  │
│  (Button)    │ HTTP │  (Flask)     │ KILL │  (PID tracked│
└──────────────┘      └──────────────┘      └──────────────┘
```

**Implémentation :**

1. **API Flask** (`src/monitoring/control_api.py`) :
   ```python
   @app.route('/api/tests/stop', methods=['POST'])
   def stop_current_test():
       pid = redis.get('current_k6_pid')
       os.kill(pid, signal.SIGINT)  # Graceful stop
       return {"status": "stopped"}
   ```

2. **Grafana Panel** (Button Plugin) :
   - URL: `http://localhost:5000/api/tests/stop`
   - Confirmation modale : "Arrêter le test en cours ?"
   - Retour visuel : Annotation "Test arrêté manuellement"

3. **K6 Executor** modifié :
   - Sauvegarder PID dans Redis/fichier
   - Handler SIGINT pour export métriques avant fermeture

**Livrables :**
- ✅ API Flask démarrée avec Docker Compose
- ✅ Bouton Stop fonctionnel dans dashboard
- ✅ Test d'arrêt validé (métriques exportées)

---

## Configuration Pas à Pas

### Étape 1 : Docker Compose Setup

Créer `docker-compose.monitoring.yml` :

```yaml
version: '3.8'

services:
  influxdb:
    image: influxdb:2.7
    container_name: promo-influxdb
    ports:
      - "8086:8086"
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=admin
      - DOCKER_INFLUXDB_INIT_PASSWORD=adminpassword
      - DOCKER_INFLUXDB_INIT_ORG=promo-analyzer
      - DOCKER_INFLUXDB_INIT_BUCKET=k6-metrics
      - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=my-super-secret-token
    volumes:
      - influxdb-data:/var/lib/influxdb2
      - influxdb-config:/etc/influxdb2
    healthcheck:
      test: ["CMD", "influx", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  grafana:
    image: grafana/grafana:10.2.3
    container_name: promo-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource
      - GF_DASHBOARDS_DEFAULT_HOME_DASHBOARD_PATH=/etc/grafana/provisioning/dashboards/k6-dashboard.json
    volumes:
      - grafana-data:/var/lib/grafana
      - ./dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana-datasources.yml:/etc/grafana/provisioning/datasources/influxdb.yml
    depends_on:
      influxdb:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Optional: Control API for emergency stop
  control-api:
    build: ./src/monitoring
    container_name: promo-control-api
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock  # Access to host Docker
    depends_on:
      - grafana

volumes:
  influxdb-data:
  influxdb-config:
  grafana-data:
```

### Étape 2 : Grafana Data Source Config

Créer `grafana-datasources.yml` :

```yaml
apiVersion: 1

datasources:
  - name: InfluxDB-K6
    type: influxdb
    access: proxy
    url: http://influxdb:8086
    jsonData:
      version: Flux
      organization: promo-analyzer
      defaultBucket: k6-metrics
      tlsSkipVerify: true
    secureJsonData:
      token: my-super-secret-token
    isDefault: true
    editable: false
```

### Étape 3 : Builder K6 avec Extension

```bash
# Installer xk6
go install go.k6.io/xk6/cmd/xk6@latest

# Builder K6 custom
xk6 build --with github.com/grafana/xk6-output-influxdb \
  --output ./bin/k6-influxdb

# Vérifier
./bin/k6-influxdb version
```

### Étape 4 : Modifier K6 Executor

Créer `src/monitoring/influxdb_config.py` :

```python
from dataclasses import dataclass
import uuid
from datetime import datetime

@dataclass
class InfluxDBConfig:
    """Configuration for K6 InfluxDB output"""

    organization: str = "promo-analyzer"
    bucket: str = "k6-metrics"
    token: str = "my-super-secret-token"
    addr: str = "http://localhost:8086"
    push_interval: str = "1s"
    insecure: bool = False

    def to_env_vars(self) -> dict[str, str]:
        """Convert to K6 environment variables"""
        return {
            "K6_INFLUXDB_ORGANIZATION": self.organization,
            "K6_INFLUXDB_BUCKET": self.bucket,
            "K6_INFLUXDB_TOKEN": self.token,
            "K6_INFLUXDB_ADDR": self.addr,
            "K6_INFLUXDB_PUSH_INTERVAL": self.push_interval,
            "K6_INFLUXDB_INSECURE": str(self.insecure).lower(),
        }

def generate_test_id(promo_name: str = "") -> str:
    """Generate unique test ID for filtering in Grafana"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_uuid = str(uuid.uuid4())[:8]

    if promo_name:
        safe_name = promo_name.lower().replace(" ", "_")[:20]
        return f"{safe_name}_{timestamp}_{short_uuid}"

    return f"test_{timestamp}_{short_uuid}"
```

Modifier `src/k6_executor.py` :

```python
from monitoring.influxdb_config import InfluxDBConfig, generate_test_id

class K6Executor:
    def __init__(self, influx_enabled: bool = False):
        self.influx_enabled = influx_enabled
        self.influx_config = InfluxDBConfig() if influx_enabled else None

    def run_test(
        self,
        script_path: str,
        promo_name: str = "",
        environment: str = "preprod",
        promo_type: str = "unknown",
        **kwargs
    ) -> dict:
        """Execute K6 test with optional InfluxDB streaming"""

        # Generate unique test ID
        test_id = generate_test_id(promo_name)

        # Build K6 command
        cmd = ["./bin/k6-influxdb", "run"]

        # Add InfluxDB output if enabled
        if self.influx_enabled:
            cmd.extend([
                "--out", f"xk6-influxdb={self.influx_config.addr}",
                "--tag", f"testid={test_id}",
                "--tag", f"environment={environment}",
                "--tag", f"promo_type={promo_type}",
                "--tag", f"promo_name={promo_name}",
            ])

        # Add JSON export for Python analysis (keep existing)
        cmd.extend([
            "--summary-export", f"/tmp/k6_results_{test_id}.json"
        ])

        cmd.append(script_path)

        # Prepare environment variables
        env = os.environ.copy()
        if self.influx_enabled:
            env.update(self.influx_config.to_env_vars())

        # Execute K6
        logger.info(f"Starting K6 test: {test_id}")
        logger.info(f"Dashboard: http://localhost:3000/d/k6?var-testid={test_id}")

        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Track PID for emergency stop
        self._save_current_pid(process.pid, test_id)

        stdout, stderr = process.communicate()

        if process.returncode != 0:
            raise K6ExecutionError(f"K6 failed: {stderr.decode()}")

        return {
            "test_id": test_id,
            "exit_code": process.returncode,
            "dashboard_url": f"http://localhost:3000/d/k6?var-testid={test_id}",
        }

    def _save_current_pid(self, pid: int, test_id: str):
        """Save current K6 PID for emergency stop"""
        with open("/tmp/current_k6.pid", "w") as f:
            f.write(f"{pid}\n{test_id}")
```

### Étape 5 : Démarrer les Services

```bash
# Démarrer InfluxDB + Grafana
docker compose -f docker-compose.monitoring.yml up -d

# Vérifier santé
docker compose ps

# Accéder Grafana
open http://localhost:3000
# Login: admin / admin
```

### Étape 6 : Importer Dashboard K6

```bash
# Dashboard officiel K6 (ID: 2587)
curl -X POST http://localhost:3000/api/dashboards/import \
  -H "Content-Type: application/json" \
  -u admin:admin \
  -d '{
    "dashboard": {
      "id": null,
      "uid": "k6-official",
      "title": "K6 Load Testing Results"
    },
    "folderId": 0,
    "inputs": [{
      "name": "DS_INFLUXDB",
      "type": "datasource",
      "pluginId": "influxdb",
      "value": "InfluxDB-K6"
    }],
    "overwrite": true
  }'
```

Ou manuellement :
1. Aller sur https://grafana.com/grafana/dashboards/2587
2. Copier JSON
3. Grafana UI → Dashboards → Import → Coller JSON

### Étape 7 : Premier Test

```bash
# Tester sans Python (test manuel K6)
K6_INFLUXDB_ORGANIZATION=promo-analyzer \
K6_INFLUXDB_BUCKET=k6-metrics \
K6_INFLUXDB_TOKEN=my-super-secret-token \
./bin/k6-influxdb run \
  --out xk6-influxdb=http://localhost:8086 \
  --tag testid=manual-test-001 \
  --tag environment=preprod \
  scripts/k6/product_test.js

# Voir dans Grafana
open "http://localhost:3000/d/k6-official?var-testid=manual-test-001"
```

---

## Dashboards Disponibles

### 1. K6 Load Testing Results (ID: 2587)

**Pros :**
- ✅ Dashboard officiel maintenu par Grafana
- ✅ Toutes les métriques K6 essentielles
- ✅ Compatible InfluxDB v1.x et v2.x

**Panels :**
- Virtual Users (VUs)
- Request Rate
- Response Time (p95, p99)
- Error Rate
- Throughput (data sent/received)
- Checks Pass Rate

**Import :**
```bash
grafana.com/grafana/dashboards/2587
```

### 2. Advanced K6 Dashboard (ID: 15080)

**Pros :**
- ✅ Analyse détaillée par endpoint
- ✅ Heatmaps pour distribution
- ✅ Comparaison entre tests

**Panels supplémentaires :**
- Request latency heatmap
- Top 10 slowest endpoints
- HTTP status code distribution
- Custom checks breakdown

**Import :**
```bash
grafana.com/grafana/dashboards/15080
```

### 3. Dashboard Custom "Promo Marketing" (À créer)

**Design simplifié pour non-techniques :**

```json
{
  "dashboard": {
    "title": "Promo Load Analyzer - Marketing View",
    "panels": [
      {
        "title": "🚦 Santé du Site",
        "type": "gauge",
        "targets": [{
          "query": "from(bucket: \"k6-metrics\") |> filter(fn: (r) => r._measurement == \"http_req_duration\" and r._field == \"p95\")"
        }],
        "thresholds": {
          "mode": "absolute",
          "steps": [
            {"value": 0, "color": "green"},
            {"value": 1000, "color": "yellow"},
            {"value": 2000, "color": "red"}
          ]
        }
      },
      {
        "title": "👥 Utilisateurs Simultanés",
        "type": "timeseries",
        "targets": [{
          "query": "from(bucket: \"k6-metrics\") |> filter(fn: (r) => r._measurement == \"vus\")"
        }]
      },
      {
        "title": "⏱️ Temps de Réponse",
        "type": "timeseries",
        "targets": [
          {"query": "...p50...", "alias": "Moyen"},
          {"query": "...p95...", "alias": "95% des utilisateurs"},
          {"query": "...p99...", "alias": "Worst case"}
        ]
      },
      {
        "title": "❌ Taux d'Erreur",
        "type": "stat",
        "targets": [{
          "query": "from(bucket: \"k6-metrics\") |> filter(fn: (r) => r._measurement == \"http_req_failed\")"
        }],
        "unit": "percent"
      }
    ],
    "templating": {
      "list": [
        {
          "name": "testid",
          "type": "query",
          "query": "import \"influxdata/influxdb/schema\" schema.tagValues(bucket: \"k6-metrics\", tag: \"testid\")"
        },
        {
          "name": "environment",
          "type": "custom",
          "options": ["prod", "preprod"]
        }
      ]
    }
  }
}
```

---

## Intégration avec le Code Existant

### Modifier `main.py` pour Activer Dashboard

```python
from monitoring.influxdb_config import InfluxDBConfig
from monitoring.dashboard_manager import DashboardManager

def main(args):
    # Initialize dashboard if enabled
    dashboard = None
    if args.enable_dashboard:
        dashboard = DashboardManager()
        dashboard.start_services()  # Start Docker Compose
        dashboard.wait_ready()      # Wait for Grafana health

    # Initialize K6 executor with InfluxDB
    executor = K6Executor(influx_enabled=args.enable_dashboard)

    # Run test
    result = executor.run_test(
        script_path=k6_script,
        promo_name=promo_data.get("name", ""),
        environment="prod" if "ipln.fr" in args.url else "preprod",
        promo_type=promo_data.get("type", "unknown")
    )

    # Open dashboard in browser
    if dashboard:
        dashboard.open_browser(result["dashboard_url"])
        print(f"\n📊 Dashboard: {result['dashboard_url']}")
        print("🔴 Press Ctrl+C to stop monitoring (test will continue)")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n✅ Dashboard remains available at http://localhost:3000")
```

### Créer `src/monitoring/dashboard_manager.py`

```python
import subprocess
import requests
import time
import webbrowser
from pathlib import Path
from loguru import logger

class DashboardManager:
    """Manage Grafana + InfluxDB lifecycle"""

    COMPOSE_FILE = Path(__file__).parent.parent.parent / "docker-compose.monitoring.yml"
    GRAFANA_URL = "http://localhost:3000"
    INFLUXDB_URL = "http://localhost:8086"

    def start_services(self):
        """Start Docker Compose services"""
        logger.info("Starting Grafana + InfluxDB...")

        subprocess.run(
            ["docker", "compose", "-f", str(self.COMPOSE_FILE), "up", "-d"],
            check=True,
            capture_output=True
        )

    def wait_ready(self, timeout: int = 60):
        """Wait for services to be healthy"""
        start = time.time()

        while time.time() - start < timeout:
            try:
                # Check Grafana
                resp = requests.get(f"{self.GRAFANA_URL}/api/health", timeout=2)
                if resp.status_code == 200:
                    logger.success("✅ Grafana ready")
                    return True
            except requests.RequestException:
                pass

            time.sleep(2)

        raise TimeoutError("Grafana did not become ready in time")

    def stop_services(self):
        """Stop Docker Compose services"""
        subprocess.run(
            ["docker", "compose", "-f", str(self.COMPOSE_FILE), "down"],
            check=True
        )

    def open_browser(self, url: str):
        """Open dashboard in default browser"""
        webbrowser.open(url)
```

### Ajouter Arguments CLI

Modifier `src/cli.py` :

```python
def parse_args():
    parser = argparse.ArgumentParser(...)

    # Existing args...

    # Dashboard options
    parser.add_argument(
        "--enable-dashboard",
        action="store_true",
        help="Enable real-time Grafana dashboard (requires Docker)"
    )

    parser.add_argument(
        "--dashboard-only",
        action="store_true",
        help="Only start dashboard services without running test"
    )

    return parser.parse_args()
```

### Exemple d'Usage

```bash
# Lancer test avec dashboard temps réel
python -m src.cli \
  --url "https://ipln.fr/photo-video/3867-sony-fe-50mm-f12-gm.html" \
  --intensity medium \
  --enable-dashboard

# Résultat
"""
🔍 Detecting page type...
✅ Product page detected
🎯 Scraping promotions...
✅ Found: Auto cart rule (-300.00€)
🚀 Generating K6 script...
📊 Dashboard: http://localhost:3000/d/k6?var-testid=sony_fe_50mm_20251028_143022_a3f8b2c1
⚡ Starting K6 test: sony_fe_50mm_20251028_143022_a3f8b2c1

[Dashboard s'ouvre automatiquement dans le navigateur]

Test running... Press Ctrl+C to stop monitoring
"""
```

---

## Sécurité & Production

### 1. Credentials Management

**Problème :** Token InfluxDB en clair dans `docker-compose.yml`

**Solution :**
```bash
# .env.monitoring (gitignored)
INFLUXDB_ADMIN_TOKEN=$(openssl rand -hex 32)
GRAFANA_ADMIN_PASSWORD=$(openssl rand -hex 16)

# docker-compose.yml
environment:
  - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=${INFLUXDB_ADMIN_TOKEN}
```

### 2. Network Isolation

```yaml
# docker-compose.monitoring.yml
services:
  influxdb:
    networks:
      - monitoring-net

  grafana:
    networks:
      - monitoring-net

networks:
  monitoring-net:
    driver: bridge
    internal: false  # Allow internet for plugins
```

### 3. Backup Automatique

```bash
# Cron job (daily at 3am)
0 3 * * * docker exec promo-influxdb \
  influx backup /backups/$(date +\%Y\%m\%d) \
  --token $INFLUXDB_ADMIN_TOKEN
```

### 4. Limites de Rétention

```yaml
# InfluxDB config
environment:
  - INFLUXDB_RETENTION_POLICY_DURATION=30d  # 30 jours
```

### 5. Production Checklist

- [ ] Changer tous les mots de passe par défaut
- [ ] Configurer HTTPS (Traefik/Nginx)
- [ ] Limiter accès réseau (firewall)
- [ ] Activer authentification Grafana (LDAP/OAuth)
- [ ] Backup automatique InfluxDB
- [ ] Monitoring des conteneurs (Prometheus)
- [ ] Logs centralisés (Loki)

---

## Troubleshooting

### Problème : "Connection refused" à InfluxDB

**Diagnostic :**
```bash
docker compose ps
docker logs promo-influxdb
```

**Solutions :**
- Attendre 30s (initialisation InfluxDB 2.x longue)
- Vérifier port 8086 libre : `lsof -i :8086`
- Recréer volumes : `docker compose down -v && docker compose up -d`

---

### Problème : K6 n'envoie pas de données

**Diagnostic :**
```bash
# Vérifier connexion
curl http://localhost:8086/health

# Tester manuellement
K6_INFLUXDB_ORGANIZATION=promo-analyzer \
K6_INFLUXDB_BUCKET=k6-metrics \
K6_INFLUXDB_TOKEN=my-super-secret-token \
./bin/k6-influxdb run --out xk6-influxdb=http://localhost:8086 test.js
```

**Solutions :**
- Vérifier variables d'environnement : `printenv | grep K6_INFLUX`
- Rebuild K6 : `xk6 build --with github.com/grafana/xk6-output-influxdb`
- Vérifier token InfluxDB : Aller sur http://localhost:8086

---

### Problème : Dashboard vide dans Grafana

**Diagnostic :**
```bash
# Vérifier data source
curl -u admin:admin http://localhost:3000/api/datasources

# Tester requête Flux
curl -X POST http://localhost:8086/api/v2/query \
  -H "Authorization: Token my-super-secret-token" \
  -d 'from(bucket:"k6-metrics") |> range(start: -1h)'
```

**Solutions :**
- Réimporter dashboard avec bon data source
- Vérifier organisation/bucket dans query
- Changer time range (Last 5 minutes → Last 1 hour)

---

### Problème : Docker Compose ne démarre pas

**Diagnostic :**
```bash
docker compose -f docker-compose.monitoring.yml config
docker compose logs
```

**Solutions :**
- Mettre à jour Docker Desktop (macOS)
- Libérer espace disque : `docker system prune -a`
- Vérifier syntaxe YAML : https://yamlchecker.com

---

## Ressources & Liens

### Documentation Officielle
- K6 InfluxDB Output: https://grafana.com/docs/k6/latest/results-output/real-time/influxdb/
- Grafana Dashboards: https://grafana.com/docs/grafana/latest/dashboards/
- InfluxDB 2.x: https://docs.influxdata.com/influxdb/v2/

### Dashboards Pré-construits
- K6 Official (ID: 2587): https://grafana.com/grafana/dashboards/2587
- K6 Advanced (ID: 15080): https://grafana.com/grafana/dashboards/15080
- K6 Prometheus (ID: 19665): https://grafana.com/grafana/dashboards/19665

### Extensions K6
- xk6-output-influxdb: https://github.com/grafana/xk6-output-influxdb
- xk6-dashboard: https://github.com/grafana/xk6-dashboard (alternative standalone)

### Exemples de Code
- Docker K6 + Grafana: https://github.com/luketn/docker-k6-grafana-influxdb
- K6 Samples: https://github.com/grafana/k6/tree/master/examples

---

## Next Steps

Après implémentation de cette Phase 2 :

1. **Phase 2.6 - Historique & Comparaison** (2-3h)
   - Tableau récapitulatif des tests passés
   - Comparaison visuelle baseline vs promo
   - Export CSV des métriques

2. **Phase 2.7 - Optimisation Performances** (3-4h)
   - Downsampling InfluxDB (agréger anciennes données)
   - Caching Grafana
   - Index optimisés

3. **Phase 3 - ML Prediction** (Phase future)
   - Entraîner modèle sur historique
   - Prédire capacité max avant test
   - Alertes proactives

---

**Document maintenu par l'équipe technique - Dernière mise à jour: 2025-10-28**
