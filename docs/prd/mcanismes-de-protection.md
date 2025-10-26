# 🛡️ Mécanismes de Protection

## Vue d'ensemble

K6 ne possède **pas de circuit breaker automatique**. Les protections doivent être **configurées explicitement** via thresholds avec `abortOnFail`.

**Objectif** : Éviter qu'un test de charge fasse planter le site en production.

---

## Thresholds de sécurité obligatoires

Tous les scripts K6 incluent ces protections par défaut :

```javascript
export const options = {
    stages: [...],
    
    thresholds: {
        // 🚨 PROTECTION CRITIQUE 1 : Taux d'erreur
        'http_req_failed': [
            {
                threshold: 'rate<0.10',      // Max 10% erreurs
                abortOnFail: true,           // Arrêt immédiat
                delayAbortEval: '10s'        // Après 10s stabilisation
            }
        ],
        
        // 🚨 PROTECTION CRITIQUE 2 : Dégradation serveur
        'http_req_duration': [
            {
                threshold: 'p(95)<5000',     // p95 < 5s
                abortOnFail: true
            }
        ],
        
        // 🚨 PROTECTION CRITIQUE 3 : Checks systématiques
        'checks': [
            {
                threshold: 'rate>0.80',      // Min 80% checks OK
                abortOnFail: true,
                delayAbortEval: '10s'
            }
        ],
        
        // 📊 ALERTE (sans arrêt) : Performance acceptable
        'http_req_duration': [
            {
                threshold: 'p(95)<2000',     // p95 < 2s
                abortOnFail: false           // Continue mais signale
            }
        ]
    }
};
```

---

## Différences PROD vs PREPROD

### PROD (Protection maximale)

```javascript
// Seuils ultra-conservateurs
thresholds: {
    'http_req_failed': [
        { threshold: 'rate<0.05', abortOnFail: true }  // Max 5%
    ],
    'http_req_duration': [
        { threshold: 'p(95)<3000', abortOnFail: true } // p95 < 3s
    ],
    'http_req_duration': [
        { threshold: 'p(99)<5000', abortOnFail: true } // p99 < 5s
    ]
}

// + Validation horaire
if (current_hour < 3 || current_hour >= 6) {
    throw new Error("Tests PROD: 3h-6h uniquement");
}

// + Max VUs limité
max_vus: 50  // Sans whitelist Cloudflare
```

### PREPROD (Protection standard)

```javascript
// Seuils standards
thresholds: {
    'http_req_failed': [
        { threshold: 'rate<0.10', abortOnFail: true }  // Max 10%
    ],
    'http_req_duration': [
        { threshold: 'p(95)<5000', abortOnFail: true } // p95 < 5s
    ]
}

// Pas de limite horaire
// Max VUs: 500
```

---

## Niveaux de protection par intensité

| Intensité | Max VUs | Erreurs max | p95 max | Arrêt si |
|-----------|---------|-------------|---------|----------|
| **light** (PROD safe) | 50 | 5% | 3000ms | Dépassement seuil |
| **medium** (PREPROD) | 200 | 10% | 5000ms | Dépassement seuil |
| **heavy** (PREPROD stress) | 500 | 15% | 10000ms | Dépassement seuil |

---

## Procédures d'arrêt d'urgence

### 1. Arrêt gracieux (recommandé)

```bash
# Ctrl+C dans le terminal
# → Arrête nouvelles itérations
# → Termine itérations en cours
# → Exécute teardown()
# → Export metrics
```

**Délai** : 5-30s selon test en cours

### 2. Arrêt immédiat (urgence)

```bash
# Double Ctrl+C
# → Tue le processus immédiatement
# → Pas de teardown
# → Metrics partielles perdues
```

**Délai** : Instantané

### 3. Arrêt via API REST (si k6 en mode serveur)

```bash
# Lancer k6 en mode serveur
k6 run --address=:6565 script.js

# Arrêt distant
curl -X PATCH \
  -d '{"data":{"attributes":{"stopped":true}}}' \
  http://localhost:6565/v1/status
```

**Usage** : Monitoring externe, dashboards

### 4. Arrêt automatique (thresholds)

```javascript
// Déjà configuré dans les scripts
// Arrêt auto si seuil dépassé
abortOnFail: true
```

---

## Monitoring temps réel (recommandé)

### Méthode 1 : Terminal (basique)

```bash
k6 run script.js

# Output live :
# ✓ checks.........................: 98.50%
# ✗ http_req_duration..............: p(95)=2450ms
# ⚠️  threshold breach warning
```

### Méthode 2 : Dashboard externe (avancé)

```bash
# Export vers InfluxDB + Grafana
k6 run \
  --out influxdb=http://localhost:8086/k6 \
  script.js

# Dashboard Grafana temps réel :
# - Graphe p95 live
# - Alerte si > seuil
# - Bouton STOP d'urgence
```

**Setup** : Optionnel, Phase 2

---

## Exemple complet : Template produit avec protections

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Trend } from 'k6/metrics';

export const options = {
    // 🎯 Scénario charge
    stages: [
        { duration: '1m', target: 200 },
        { duration: '3m', target: 200 },
        { duration: '30s', target: 0 }
    ],
    
    // 🛡️ PROTECTIONS OBLIGATOIRES
    thresholds: {
        // Protection 1 : Erreurs
        'http_req_failed': [
            {
                threshold: 'rate<0.10',
                abortOnFail: true,
                delayAbortEval: '10s'
            }
        ],
        
        // Protection 2 : Dégradation
        'http_req_duration': [
            { threshold: 'p(95)<5000', abortOnFail: true },
            { threshold: 'p(99)<8000', abortOnFail: true }
        ],
        
        // Protection 3 : Checks
        'checks': [
            { threshold: 'rate>0.80', abortOnFail: true }
        ],
        
        // Alerte performance (sans arrêt)
        'http_req_duration': [
            { threshold: 'p(95)<2000', abortOnFail: false }
        ]
    }
};

const cartSuccess = new Counter('add_to_cart_success');

export default function() {
    // Test ajout panier
    let res = http.get('https://ipln.fr/produit');
    
    // ✅ Checks obligatoires
    const pageOk = check(res, {
        'page loads': (r) => r.status === 200,
        'page fast': (r) => r.timings.duration < 3000,
        'no server error': (r) => r.status < 500
    });
    
    // ⚠️ Si checks échouent, metric 'checks' baisse
    // → Peut déclencher abort si < 80%
    
    if (!pageOk) {
        console.warn(`⚠️ Check failed - VU ${__VU} iteration ${__ITER}`);
    }
    
    sleep(1 + Math.random());
    
    // POST ajout panier
    const addRes = http.post(
        'https://ipln.fr/module/ps_shoppingcart/ajax',
        'id_product=1492&action=add-to-cart',
        { headers: { 'X-Requested-With': 'XMLHttpRequest' } }
    );
    
    const cartOk = check(addRes, {
        'cart add 200': (r) => r.status === 200,
        'cart has products': (r) => r.body.includes('cart-products-count')
    });
    
    if (cartOk) {
        cartSuccess.add(1);
    }
    
    sleep(2);
}

// 🏁 Teardown (toujours exécuté sauf arrêt brutal)
export function teardown(data) {
    console.log('Test terminé - Cleanup...');
}
```

---

## Logs & Alertes

### Détection arrêt automatique

```bash
# Output K6 si threshold abort
✗ http_req_failed............: 12.5%  ✓ 125 ✗ 875
  ↳ threshold [rate<0.10] FAILED
  
⚠️  ABORTING TEST - Threshold exceeded
    Error rate: 12.5% (limit: 10%)
    
Test stopped at 1m32s / 5m00s planned
```

### Notification Slack (recommandé PROD)

```python
# Dans orchestrator.py
if test_aborted:
    send_slack_alert({
        'channel': '#tech-alerts',
        'message': f'🚨 Test K6 arrêté automatiquement\n'
                   f'URL: {url}\n'
                   f'Raison: Taux erreur > 10%\n'
                   f'Action: Vérifier logs serveur'
    })
```

---

## Checklist pré-test PROD

Avant tout test en production :

- [ ] **Horaire** : Entre 3h-6h du matin ✓
- [ ] **VUs** : Max 50 sans whitelist Cloudflare ✓
- [ ] **Thresholds** : Mode PROD activé (seuils stricts) ✓
- [ ] **Mode** : `read_only` (GET uniquement) ✓
- [ ] **Monitoring** : Dashboard ouvert ou logs actifs ✓
- [ ] **Équipe** : 1 personne en standby pour arrêt d'urgence ✓
- [ ] **Backup** : Snapshot serveur récent < 24h ✓

---

## FAQ Sécurité

**Q : Le test peut-il faire crasher le site ?**  
R : Théoriquement oui, mais protections multiples :
- Thresholds arrêt auto si dégradation
- Horaires 3h-6h (trafic minimal)
- Max 50 VUs (charge modérée)
- Mode read_only (pas d'écriture BDD)

**Q : Que se passe-t-il si Cloudflare bloque ?**  
R : K6 reçoit des 429/503 → Taux erreur monte → Threshold abort automatique

**Q : Peut-on tester en PROD sans risque ?**  
R : Oui avec précautions :
- Intensity = `light` (50 VUs)
- Horaire 3h-6h
- Durée courte (2min)
- Surveillance active

**Q : Différence entre abort et fail ?**  
R : 
- `abortOnFail: true` → Arrêt immédiat du test
- `abortOnFail: false` → Test continue, exit code ≠ 0

---
