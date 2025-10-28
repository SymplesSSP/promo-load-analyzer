# Monitoring en Temps Réel - Grafana

Dashboard temps réel pour visualiser les tests K6 pendant leur exécution.

**100% Local - 100% Gratuit - Aucune connexion externe requise**

---

## 🚀 Installation Rapide (15 min)

### Prérequis

1. **Docker Desktop** (macOS)
   - Télécharger : https://www.docker.com/products/docker-desktop/
   - Installer et démarrer Docker Desktop

2. **Vérifier installation :**
   ```bash
   docker --version
   # Doit afficher : Docker version 24.x.x
   ```

---

## 📊 Utilisation

### 1. Démarrer le Monitoring

```bash
# Démarrer Grafana + InfluxDB
./scripts/start_monitoring.sh
```

**Résultat :**
```
✅ Grafana is running
✅ InfluxDB is running
📊 Grafana Dashboard: http://localhost:3000
```

### 2. Lancer un Test avec Dashboard

```bash
# Test avec dashboard temps réel
python -m src.cli \
  --url "https://preprod.ipln.fr/photo-video/3867-sony-fe-50mm.html" \
  --intensity medium \
  --enable-dashboard
```

**Résultat :**
```
📊 Dashboard: http://localhost:3000/d/k6-load-testing?var-testid=test_20251028_143022_a3f8
```

Le dashboard s'ouvre automatiquement et affiche :
- ⏱️ Temps de réponse (p95) en temps réel
- 👥 Nombre d'utilisateurs actifs
- ❌ Taux d'erreur
- 📈 Graphiques détaillés

### 3. Voir le Dashboard

```bash
# Ouvrir Grafana
open http://localhost:3000

# Login (première fois)
Utilisateur : admin
Mot de passe : admin
```

Le dashboard **K6 Load Testing** se charge automatiquement.

### 4. Arrêter le Monitoring

```bash
# Arrêter Grafana + InfluxDB
./scripts/stop_monitoring.sh
```

Les données restent sauvegardées dans `./monitoring/`.

---

## 🎯 Ce Que Vous Voyez dans le Dashboard

### Panel "Response Time p95" (Jauge)
- **Vert** : < 1000ms (excellent)
- **Jaune** : 1000-2000ms (acceptable)
- **Rouge** : > 2000ms (problème)

### Panel "Virtual Users" (Graphique)
- Montre les utilisateurs simultanés actifs
- Monte progressivement pendant le test

### Panel "Error Rate" (Jauge)
- **Vert** : < 1% erreurs
- **Rouge** : > 1% erreurs

### Panel "Response Time" (Graphique)
- **Moyenne** (ligne bleue)
- **p95** (ligne orange) : 95% des utilisateurs
- **p99** (ligne rouge) : pire cas

---

## 🔧 Structure des Fichiers

```
monitoring/
├── README.md                        # Ce fichier
├── docker-compose.monitoring.yml    # Configuration Docker
├── grafana-provisioning/
│   ├── datasources/influxdb.yml     # Connexion InfluxDB
│   └── dashboards/k6-dashboard.json # Dashboard K6
├── influxdb-data/                   # Données InfluxDB (gitignored)
├── influxdb-config/                 # Config InfluxDB (gitignored)
└── grafana-data/                    # Données Grafana (gitignored)
```

---

## 🛠️ Commandes Utiles

```bash
# Vérifier status
docker compose -f docker-compose.monitoring.yml ps

# Voir logs Grafana
docker logs promo-grafana

# Voir logs InfluxDB
docker logs promo-influxdb

# Redémarrer services
docker compose -f docker-compose.monitoring.yml restart

# Supprimer toutes les données (reset complet)
docker compose -f docker-compose.monitoring.yml down -v
rm -rf monitoring/influxdb-data monitoring/grafana-data
```

---

## 🔍 Filtrer par Test

Dans Grafana, en haut du dashboard :
- **Test ID** : Sélectionner un test spécifique
- Ou choisir **All** pour voir tous les tests

Chaque test a un ID unique : `test_20251028_143022_a3f8`

---

## ❓ Troubleshooting

### Problème : "Cannot connect to Docker"

**Solution :**
```bash
# Démarrer Docker Desktop (icône dans barre menu)
# Attendre 30 secondes
docker ps
```

### Problème : "Port 3000 already in use"

**Solution :**
```bash
# Trouver processus utilisant port 3000
lsof -ti:3000

# Tuer le processus
kill -9 $(lsof -ti:3000)

# Redémarrer
./scripts/start_monitoring.sh
```

### Problème : Dashboard vide (pas de données)

**Causes possibles :**
1. Test K6 lancé **sans** `--enable-dashboard`
2. InfluxDB pas démarré avant le test
3. Mauvais filtre "Test ID" dans Grafana

**Solution :**
```bash
# 1. Vérifier que les services tournent
docker compose -f docker-compose.monitoring.yml ps

# 2. Relancer un test avec --enable-dashboard
python -m src.cli --url "..." --enable-dashboard

# 3. Dans Grafana, sélectionner le bon Test ID
```

---

## 🎓 Fonctionnement Technique

```
Python           K6 Tests         InfluxDB         Grafana          Vous
  |                |                 |                |               |
  |-- Génère -->   |                 |                |               |
  |   script K6    |                 |                |               |
  |                |                 |                |               |
  |-- Lance K6 --> |                 |                |               |
  |   avec tags    |                 |                |               |
  |                |                 |                |               |
  |                |-- Envoie ---->  |                |               |
  |                | métriques (1s)  |                |               |
  |                |                 |                |               |
  |                |                 |<-- Lit -----   |               |
  |                |                 |   données      |               |
  |                |                 |                |               |
  |                |                 |                |-- Affiche --> |
  |                |                 |                |  graphiques   |
```

**Flux :**
1. Python génère script K6 avec tags (testid, environment, etc.)
2. K6 exécute test et envoie métriques à InfluxDB toutes les 1 seconde
3. Grafana interroge InfluxDB toutes les 5 secondes
4. Le dashboard se rafraîchit automatiquement en temps réel

---

## 📚 Pour Aller Plus Loin

- **Guide complet** : `docs/GRAFANA_DASHBOARD_GUIDE.md`
- **Dashboard officiel K6** : https://grafana.com/grafana/dashboards/2587
- **Documentation K6 + InfluxDB** : https://k6.io/docs/results-output/real-time/influxdb/

---

## 🔐 Sécurité

**Credentials par défaut (à changer en production) :**

| Service   | URL                   | User  | Password |
|-----------|-----------------------|-------|----------|
| Grafana   | http://localhost:3000 | admin | admin    |
| InfluxDB  | http://localhost:8086 | admin | admin123 |

**Token InfluxDB :** `my-super-secret-token`

**⚠️ À faire avant Black Friday :**
- Changer tous les mots de passe
- Changer le token InfluxDB
- Activer HTTPS si accessible depuis internet

---

**Questions ? Voir le guide complet dans `docs/GRAFANA_DASHBOARD_GUIDE.md`**
