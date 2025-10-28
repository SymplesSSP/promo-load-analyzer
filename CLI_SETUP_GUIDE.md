# Setup Monitoring en CLI - Guide Complet

**Tout automatisé en ligne de commande, sans interface graphique.**

---

## 🚀 Installation Rapide (3 commandes)

```bash
# 1. Aller dans le projet
cd "/Volumes/GitHub_SSD/Projet K6"

# 2. Démarrer monitoring (auto-install)
./scripts/start_monitoring.sh

# 3. Tester que tout fonctionne
./scripts/test_monitoring.sh
```

**C'est tout !** ✅

---

## 📋 Prérequis

### Docker Desktop (1 fois)

```bash
# Télécharger : https://www.docker.com/products/docker-desktop/
# Ou avec Homebrew :
brew install --cask docker

# Lancer Docker Desktop
open -a Docker

# Vérifier installation
docker --version
docker compose version
```

---

## 🎯 Commandes Disponibles

### Démarrer Monitoring

```bash
./scripts/start_monitoring.sh
```

**Ce que fait ce script automatiquement :**
1. ✅ Vérifie que Docker tourne
2. ✅ Télécharge images Docker (InfluxDB + Grafana)
3. ✅ Démarre les conteneurs
4. ✅ Attend que services soient prêts (health check)
5. ✅ Ouvre Grafana dans navigateur
6. ✅ Affiche instructions d'usage

**Résultat :**
```
🚀 Starting monitoring stack (Grafana + InfluxDB)...
🐳 Starting Docker containers...
⏳ Waiting for services to be ready...
✅ Grafana is ready
✅ InfluxDB is ready
🎉 Monitoring stack is ready!

📊 GRAFANA DASHBOARD
   URL: http://localhost:3000
   Login: admin / admin

💡 USAGE
   python -m src.cli --url '...' --enable-dashboard
```

---

### Vérifier Statut

```bash
./scripts/status_monitoring.sh
```

**Affiche :**
- État Docker (running/stopped)
- État conteneurs (Grafana, InfluxDB)
- Santé services (accessible/non accessible)
- Utilisation disque
- Commandes rapides

**Exemple de sortie :**
```
🔍 Monitoring Stack Status

🐳 Docker: ✅ Running

NAMES             STATUS                  PORTS
promo-grafana     Up 2 hours             0.0.0.0:3000->3000/tcp
promo-influxdb    Up 2 hours (healthy)   0.0.0.0:8086->8086/tcp

📊 Grafana:  ✅ http://localhost:3000
🔍 InfluxDB: ✅ http://localhost:8086

💾 Disk Usage:
   InfluxDB data: 256M
   Grafana data:  45M
```

---

### Tester Installation

```bash
./scripts/test_monitoring.sh
```

**Exécute 5 tests automatiques :**
1. Docker running
2. Containers running
3. Grafana accessible
4. InfluxDB accessible
5. Bucket configuré

**Résultat :**
```
🧪 Testing monitoring stack...

Test 1/5: Docker running
   ✅ Docker is running
Test 2/5: Containers running
   ✅ Both containers are running
Test 3/5: Grafana accessible
   ✅ Grafana is accessible
Test 4/5: InfluxDB accessible
   ✅ InfluxDB is accessible
Test 5/5: InfluxDB bucket configured
   ✅ InfluxDB bucket 'k6' exists

🎉 All tests passed!
```

---

### Arrêter Monitoring

```bash
./scripts/stop_monitoring.sh
```

**Ce que fait ce script :**
1. Arrête les conteneurs Docker
2. Conserve les données (pour redémarrage)
3. Libère les ports 3000 et 8086

**Résultat :**
```
🛑 Stopping monitoring stack...
✅ Monitoring stack stopped

💡 Data is preserved in ./monitoring/ directory
   To start again: ./scripts/start_monitoring.sh
```

---

### Lancer Test avec Dashboard

```bash
# Test basique
python -m src.cli \
  --url "https://preprod.ipln.fr/votre-url" \
  --enable-dashboard

# Test complet
python -m src.cli \
  --url "https://preprod.ipln.fr/photo-video/3867-sony.html" \
  --intensity medium \
  --mode read_only \
  --enable-dashboard
```

**Pendant le test, vous voyez :**
```
📊 Dashboard: http://localhost:3000/d/k6-load-testing?var-testid=test_20251028_143022_a3f8
⚡ Starting K6 test: test_20251028_143022_a3f8

[Le dashboard se met à jour en temps réel]
```

---

## 🔧 Commandes Docker Avancées

### Voir Logs en Temps Réel

```bash
# Grafana logs
docker logs -f promo-grafana

# InfluxDB logs
docker logs -f promo-influxdb

# Tous les logs
docker compose -f docker-compose.monitoring.yml logs -f
```

### Redémarrer Services

```bash
# Redémarrer tout
docker compose -f docker-compose.monitoring.yml restart

# Redémarrer Grafana seulement
docker restart promo-grafana

# Redémarrer InfluxDB seulement
docker restart promo-influxdb
```

### Reset Complet (Supprimer Données)

```bash
# Arrêter et supprimer tout
docker compose -f docker-compose.monitoring.yml down -v

# Supprimer données locales
rm -rf monitoring/influxdb-data monitoring/grafana-data

# Redémarrer propre
./scripts/start_monitoring.sh
```

### Voir Ressources Utilisées

```bash
# CPU et RAM en temps réel
docker stats promo-grafana promo-influxdb

# Espace disque
docker system df
```

---

## 🎓 Workflow Complet

### Premier Lancement (Installation)

```bash
# 1. Installer Docker Desktop (si pas fait)
brew install --cask docker
open -a Docker

# 2. Aller dans projet
cd "/Volumes/GitHub_SSD/Projet K6"

# 3. Démarrer monitoring
./scripts/start_monitoring.sh

# 4. Attendre 30-60 secondes
# 5. Grafana s'ouvre automatiquement (http://localhost:3000)
# 6. Login: admin / admin
# 7. Dashboard "K6 Load Testing" visible
```

### Usage Quotidien

```bash
# Matin : Démarrer monitoring
./scripts/start_monitoring.sh

# Lancer tests
python -m src.cli --url "..." --enable-dashboard
python -m src.cli --url "..." --enable-dashboard
python -m src.cli --url "..." --enable-dashboard

# Voir status
./scripts/status_monitoring.sh

# Soir : Arrêter monitoring
./scripts/stop_monitoring.sh
```

### Troubleshooting

```bash
# 1. Vérifier status
./scripts/status_monitoring.sh

# 2. Tester santé
./scripts/test_monitoring.sh

# 3. Voir logs
docker logs promo-grafana
docker logs promo-influxdb

# 4. Redémarrer
docker compose -f docker-compose.monitoring.yml restart

# 5. Reset complet si problème
docker compose -f docker-compose.monitoring.yml down -v
./scripts/start_monitoring.sh
```

---

## 📊 Accès Web (après démarrage)

| Service | URL | Login | Password |
|---------|-----|-------|----------|
| **Grafana** | http://localhost:3000 | admin | admin |
| **InfluxDB** | http://localhost:8086 | admin | admin123 |

---

## 🛠️ Structure des Scripts

```
scripts/
├── start_monitoring.sh    # Démarrer (auto-install)
├── stop_monitoring.sh     # Arrêter (garde données)
├── status_monitoring.sh   # Voir état
└── test_monitoring.sh     # Tester santé
```

**Tous les scripts sont :**
- ✅ Exécutables (`chmod +x` déjà fait)
- ✅ Commentés
- ✅ Avec gestion d'erreurs
- ✅ Messages clairs

---

## 🔍 Filtrage des Tests dans Grafana

Chaque test a un **Test ID unique** :
```
test_20251028_143022_a3f8
     └─date──┘ └time┘ └uuid┘
```

**Dans Grafana :**
1. En haut du dashboard → Dropdown "Test ID"
2. Sélectionner un test spécifique
3. Ou "All" pour voir tous les tests

**CLI pour filtrer :**
```bash
# Pas de filtrage nécessaire en CLI
# Le test_id est généré automatiquement
# et passé à K6 via --tag testid=...
```

---

## 📈 Métriques Disponibles

**Envoyées automatiquement par K6 vers InfluxDB :**

| Métrique | Description | Visible dans |
|----------|-------------|--------------|
| `http_req_duration` | Temps de réponse (p95, p99) | Jauge + Graphique |
| `vus` | Utilisateurs virtuels actifs | Graphique |
| `http_req_failed` | Taux d'erreur | Jauge |
| `http_reqs` | Nombre de requêtes | Stats |
| `iterations` | Nombre d'itérations | Stats |
| `data_received` | Données reçues | Stats |
| `data_sent` | Données envoyées | Stats |

**Tags automatiques :**
- `testid` : ID unique du test
- `environment` : prod / preprod
- `intensity` : light / medium / heavy
- `page_type` : product / homepage / category

---

## 💡 Astuces CLI

### Alias Bash (optionnel)

Ajouter dans `~/.zshrc` ou `~/.bashrc` :

```bash
# Monitoring shortcuts
alias mon-start='cd "/Volumes/GitHub_SSD/Projet K6" && ./scripts/start_monitoring.sh'
alias mon-stop='cd "/Volumes/GitHub_SSD/Projet K6" && ./scripts/stop_monitoring.sh'
alias mon-status='cd "/Volumes/GitHub_SSD/Projet K6" && ./scripts/status_monitoring.sh'
alias mon-test='cd "/Volumes/GitHub_SSD/Projet K6" && ./scripts/test_monitoring.sh'

# K6 test shortcut
alias k6test='python -m src.cli --enable-dashboard'
```

Puis :
```bash
source ~/.zshrc
mon-start
k6test --url "https://..."
```

### One-liner pour Tout Démarrer

```bash
cd "/Volumes/GitHub_SSD/Projet K6" && ./scripts/start_monitoring.sh && sleep 5 && python -m src.cli --url "https://preprod.ipln.fr/photo-video/3867-sony.html" --enable-dashboard
```

---

## ❓ FAQ CLI

### "Docker is not running"

```bash
# Solution
open -a Docker
# Attendre 30 secondes
docker info
./scripts/start_monitoring.sh
```

### "Port 3000 already in use"

```bash
# Trouver processus
lsof -ti:3000

# Tuer
kill -9 $(lsof -ti:3000)

# Ou arrêter ancien monitoring
./scripts/stop_monitoring.sh

# Redémarrer
./scripts/start_monitoring.sh
```

### "Containers not responding"

```bash
# Voir logs
docker logs promo-grafana
docker logs promo-influxdb

# Redémarrer
docker compose -f docker-compose.monitoring.yml restart

# Ou reset complet
docker compose -f docker-compose.monitoring.yml down -v
./scripts/start_monitoring.sh
```

### "Dashboard vide (pas de données)"

```bash
# Vérifier que test lancé avec --enable-dashboard
python -m src.cli --url "..." --enable-dashboard

# Vérifier que monitoring tourne AVANT le test
./scripts/status_monitoring.sh

# Vérifier connexion InfluxDB
curl http://localhost:8086/health
```

---

## 🎬 Résumé Ultra-Court

```bash
# Installation (1 fois)
./scripts/start_monitoring.sh

# Usage quotidien
python -m src.cli --url "..." --enable-dashboard

# Voir dashboard
open http://localhost:3000

# Arrêter
./scripts/stop_monitoring.sh
```

**Temps total : 2 minutes**

---

**Besoin d'aide ? Voir `monitoring/README.md` ou `docs/GRAFANA_DASHBOARD_GUIDE.md`**
