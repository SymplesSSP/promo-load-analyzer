# Dashboard Temps Réel - Quick Start

**Visualisez vos tests K6 en temps réel avec Grafana**

---

## Installation (1 fois)

```bash
# 1. Installer Docker Desktop
# https://www.docker.com/products/docker-desktop/

# 2. Démarrer le monitoring
./scripts/start_monitoring.sh

# ✅ Grafana accessible à http://localhost:3000
```

---

## Utilisation

```bash
# Lancer test avec dashboard
python -m src.cli \
  --url "https://preprod.ipln.fr/votre-url" \
  --enable-dashboard

# 📊 Le dashboard s'affiche automatiquement
```

---

## Ce Que Vous Voyez

- ⏱️ **Temps de réponse** en temps réel (vert/jaune/rouge)
- 👥 **Utilisateurs actifs** (graphique)
- ❌ **Taux d'erreur** (%)
- 📈 **Historique complet** du test

---

## Accès Grafana

```
URL : http://localhost:3000
Login : admin / admin
```

Le dashboard **K6 Load Testing** se charge automatiquement.

---

## Arrêter

```bash
./scripts/stop_monitoring.sh
```

Les données restent sauvegardées.

---

## Documentation Complète

- **README monitoring** : `monitoring/README.md`
- **Guide détaillé** : `docs/GRAFANA_DASHBOARD_GUIDE.md`

---

## Avantages

✅ **100% Local** - Aucune connexion externe
✅ **100% Gratuit** - Pas d'abonnement
✅ **Temps réel** - Rafraîchissement automatique toutes les 5s
✅ **Historique** - Comparer plusieurs tests
✅ **Simple** - 2 commandes pour démarrer
