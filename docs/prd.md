# PRD - Outil d'Analyse de Charge Promotionnelle
## Orchestré par Claude Code

**Version:** 2.0  
**Date:** 26 octobre 2025  
**Auteur:** Direction Technique E-commerce  
**Statut:** Ready for Review

---

## 📌 Executive Summary

### Problème
Le marketing ne comprend pas l'**impact performance des promotions** sur le serveur. Risque de ralentissements ou pannes pendant Black Friday en période critique.

### Solution
Outil d'analyse automatisée piloté par **Claude Code** :
1. User saisit URL en langage naturel
2. Détection automatique type page + promotions
3. Test de charge adapté (K6)
4. Rapport simple : Score A-F + recommandations actionnables

### ROI
- Éviter pannes Black Friday (impact business critique)
- Optimiser promos sans dégrader performance
- Identifier capacité serveur maximale
- Tests réguliers en période promo (pas que BF)

---

## 🎯 Objectifs & Contexte

### Contexte technique
- **Platform:** PrestaShop 1.7.8.5
- **Hosting:** OVH Scale 3 (normal) / Scale 5 (Black Friday)
- **CDN:** Cloudflare actif + WAF
- **Cache:** Smarty
- **Module promos:** "Promotions et Discount"

### Objectifs business
1. **Préventif** : Identifier promos lourdes AVANT mise en ligne
2. **Capacité** : Nombre max users simultanés supportés
3. **Optimisation** : Alternatives légères (prix barré vs code auto)
4. **Monitoring** : Tests réguliers périodes promo

### Contraintes
- **PROD** : Tests avec précautions (horaires 3h-6h, max 50 VUs sans whitelist CF)
- **PREPROD** : Tests sans limitations
- **Cloudflare** : Rate limiting 50-100 VUs/IP
- **Délai MVP** : < 2 semaines avant Black Friday 2025

---

## 👥 Utilisateurs

### Marketing (principal)
- **Besoin** : Comprendre impact sans jargon technique
- **Format** : Texte simple + score A-F + actions concrètes
- **Fréquence** : 5-10 tests/semaine en période promo
- **Niveau technique** : Débutant (vulgarisation nécessaire)

### Direction technique (secondaire)
- **Besoin** : Valider capacité + identifier bottlenecks
- **Format** : Métriques détaillées (p95, error rate, VUs)
- **Fréquence** : Ponctuel sur demande
- **Niveau technique** : Expert

---

## 🎛️ Interface & Paramètres

### Workflow conversationnel

```
Marketing → Claude Code
├─> "Teste cette promo BF: https://ipln.fr/promo/bf2025"
├─> "Mode rapide, charge moyenne"
│
Claude Code interprète
├─> url = "https://ipln.fr/promo/bf2025"
├─> environment = "prod" (auto-détecté)
├─> intensity = "medium" (200 VUs)
├─> mode = "read_only" (prod = safe par défaut)
├─> duration = "quick" (2min)
│
Exécution analyse (5min)
│
Rapport markdown
├─> Score: B (78/100)
├─> Capacité: 520 users max
├─> Recommandations actionnables
```

### Paramètres configurables

#### 1. URL & Environnement
```
url: str
environment: 'prod' | 'preprod'
```

**Auto-détection** :
- `ipln.fr` → PROD
- `preprod.ipln.fr` ou autre → PREPROD

**Règles PROD** :
- Max 50 VUs (sans whitelist Cloudflare)
- Tests uniquement 3h-6h du matin
- Mode `read_only` par défaut

#### 2. Intensité

| Intensité | VUs | Durée | Usage |
|-----------|-----|-------|-------|
| `light` | 50 | 2min | Validation rapide |
| `medium` | 200 | 5min | Test réaliste ✓ défaut |
| `heavy` | 500 | 10min | Stress (preprod uniquement) |

#### 3. Mode de test
- `read_only` : GET uniquement (safe, PROD)
- `full` : POST ajout panier (preprod)

#### 4. Fenêtre horaire (PROD)
- Tests autorisés : 3h-6h du matin uniquement
- Validation automatique :
  ```python
  if env=='prod' and current_hour not in range(3,6):
      raise Error("Tests PROD: 3h-6h uniquement")
  ```

#### 5. Cloudflare whitelist
- `False` : Max 50 VUs (rate limiting)
- `True` : Jusqu'à 500 VUs (config IT requise)

---

## 🔍 Détection Automatique

### Types de pages

| Type | Pattern URL | Analyse | Durée |
|------|-------------|---------|-------|
| **Produit** | `/\d+-[\w-]+\.html` | Promos + panier | 5min |
| **Homepage** | `^https?://[^/]+/?$` | Charge globale | 3min |
| **Catégorie** | `/[\w-]+/\d+` | Listing | 4min |
| **Landing** | Autre | DOM | 3min |

### Types de promotions

#### Prix barré (Striked Price)
**Détection** : CSS `.regular-price`  
**Impact** : ~5% charge serveur (pré-calculé)  
**Complexité** : LOW

```html
<span class="regular-price">2 299,00 €</span>
<span class="current-price">1 899,00 €</span>
```

#### Code auto (Auto Cart Rule)
**Détection** : `window.prestashop.cart.vouchers.added` après ajout panier  
**Impact** : ~15% charge serveur par code  
**Complexité** : MEDIUM

```javascript
window.prestashop.cart.vouchers.added = {
  "1164996": {
    "name": "SONY GM-2",
    "reduction_amount": 399.996
  }
}
```

#### Code manuel (Manual Code)
**Détection** : Input `[name="discount_name"]`  
**Impact** : ~25% charge serveur  
**Complexité** : HIGH

**⚠️ Note** : Impacts = estimations heuristiques, validation Phase 2

---

## 📊 Métriques & Scoring

### Métriques collectées

| Métrique | Description | Seuil alerte |
|----------|-------------|--------------|
| **p95 Response** | 95% requêtes < X ms | > 2000ms |
| **Error Rate** | % requêtes 5xx/timeout | > 1% |
| **Max Users** | VUs max avant dégradation | Variable |
| **Promo Impact** | Overhead charge | Calculé |

### Seuils standards web

```
Response Time (p95):
  A (Excellent) : < 1000ms
  B (Good)      : 1000-2000ms
  C (Acceptable): 2000-3000ms
  D (Slow)      : 3000-5000ms
  F (Critical)  : > 5000ms

Error Rate:
  A : < 0.1%
  B : 0.1-1%
  C : 1-5%
  D : 5-10%
  F : > 10%
```

### Score global

```python
score = (score_response * 0.6) + (score_error * 0.4)
grade = A/B/C/D/F
```

### Détection Max Users

**Méthode** :
1. Test progressif : 50 → 100 → 200 → 500 VUs
2. Surveillance p95 chaque palier
3. Détection seuil p95 > 2000ms
4. Marge sécurité -20%

**MVP** : Estimation conservative (extrapolation linéaire)  
**Phase 2** : Détection précise via analyse courbe

---

## 🏗️ Architecture

### Vue simplifiée

```
USER (Marketing)
  │
  │ "Teste promo: https://ipln.fr/..."
  ▼
┌──────────────────────────────────┐
│      CLAUDE CODE                 │
│  1. Parse demande                │
│  2. Détermine paramètres         │
│  3. Execute main.py              │
│  4. Lit JSON results             │
│  5. Génère rapport markdown      │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│  PYTHON ANALYZER (main.py)       │
│  ┌────────────────────────────┐  │
│  │ Page Detector              │  │
│  │ └─> Type + IDs produit     │  │
│  └────────────────────────────┘  │
│  ┌────────────────────────────┐  │
│  │ Promo Scraper (Playwright) │  │
│  │ └─> Prix barré / Codes auto│  │
│  └────────────────────────────┘  │
│  ┌────────────────────────────┐  │
│  │ API PrestaShop (opt.)      │  │
│  │ └─> Détails cart rules     │  │
│  └────────────────────────────┘  │
│  ┌────────────────────────────┐  │
│  │ K6 Generator               │  │
│  │ └─> Template dynamique     │  │
│  └────────────────────────────┘  │
│  ┌────────────────────────────┐  │
│  │ K6 Executor                │  │
│  │ └─> Test charge            │  │
│  └────────────────────────────┘  │
│  ┌────────────────────────────┐  │
│  │ Results Analyzer           │  │
│  │ └─> Score + Max users      │  │
│  └────────────────────────────┘  │
└──────────────┬───────────────────┘
               │
               ▼
    /tmp/analysis_XXXXX.json
               │
               ▼
┌──────────────────────────────────┐
│  CLAUDE CODE                     │
│  Génération rapport markdown     │
│  + Recommandations               │
└──────────────┬───────────────────┘
               │
               ▼
       Rapport final (markdown)
```

### Stack

```yaml
Orchestration:
  - Claude Code CLI
  - Python 3.11+

Scraping:
  - Playwright (DOM + interactions)
  - Regex (URL patterns)
  - requests (API PrestaShop)

Load Testing:
  - k6 v0.47+

Infrastructure:
  - PrestaShop 1.7.8.5
  - OVH Scale 3/5
  - Cloudflare CDN
  - Cache Smarty
```

---

## 🛡️ Mécanismes de Protection

### Vue d'ensemble

K6 ne possède **pas de circuit breaker automatique**. Les protections doivent être **configurées explicitement** via thresholds avec `abortOnFail`.

**Objectif** : Éviter qu'un test de charge fasse planter le site en production.

---

### Thresholds de sécurité obligatoires

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

### Différences PROD vs PREPROD

#### PROD (Protection maximale)

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

#### PREPROD (Protection standard)

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

### Niveaux de protection par intensité

| Intensité | Max VUs | Erreurs max | p95 max | Arrêt si |
|-----------|---------|-------------|---------|----------|
| **light** (PROD safe) | 50 | 5% | 3000ms | Dépassement seuil |
| **medium** (PREPROD) | 200 | 10% | 5000ms | Dépassement seuil |
| **heavy** (PREPROD stress) | 500 | 15% | 10000ms | Dépassement seuil |

---

### Procédures d'arrêt d'urgence

#### 1. Arrêt gracieux (recommandé)

```bash
# Ctrl+C dans le terminal
# → Arrête nouvelles itérations
# → Termine itérations en cours
# → Exécute teardown()
# → Export metrics
```

**Délai** : 5-30s selon test en cours

#### 2. Arrêt immédiat (urgence)

```bash
# Double Ctrl+C
# → Tue le processus immédiatement
# → Pas de teardown
# → Metrics partielles perdues
```

**Délai** : Instantané

#### 3. Arrêt via API REST (si k6 en mode serveur)

```bash
# Lancer k6 en mode serveur
k6 run --address=:6565 script.js

# Arrêt distant
curl -X PATCH \
  -d '{"data":{"attributes":{"stopped":true}}}' \
  http://localhost:6565/v1/status
```

**Usage** : Monitoring externe, dashboards

#### 4. Arrêt automatique (thresholds)

```javascript
// Déjà configuré dans les scripts
// Arrêt auto si seuil dépassé
abortOnFail: true
```

---

### Monitoring temps réel (recommandé)

#### Méthode 1 : Terminal (basique)

```bash
k6 run script.js

# Output live :
# ✓ checks.........................: 98.50%
# ✗ http_req_duration..............: p(95)=2450ms
# ⚠️  threshold breach warning
```

#### Méthode 2 : Dashboard externe (avancé)

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

### Exemple complet : Template produit avec protections

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

### Logs & Alertes

#### Détection arrêt automatique

```bash
# Output K6 si threshold abort
✗ http_req_failed............: 12.5%  ✓ 125 ✗ 875
  ↳ threshold [rate<0.10] FAILED
  
⚠️  ABORTING TEST - Threshold exceeded
    Error rate: 12.5% (limit: 10%)
    
Test stopped at 1m32s / 5m00s planned
```

#### Notification Slack (recommandé PROD)

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

### Checklist pré-test PROD

Avant tout test en production :

- [ ] **Horaire** : Entre 3h-6h du matin ✓
- [ ] **VUs** : Max 50 sans whitelist Cloudflare ✓
- [ ] **Thresholds** : Mode PROD activé (seuils stricts) ✓
- [ ] **Mode** : `read_only` (GET uniquement) ✓
- [ ] **Monitoring** : Dashboard ouvert ou logs actifs ✓
- [ ] **Équipe** : 1 personne en standby pour arrêt d'urgence ✓
- [ ] **Backup** : Snapshot serveur récent < 24h ✓

---

### FAQ Sécurité

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

## 🔧 Composants

### 1. Page Detector

**Rôle** : Identifie type page + métadonnées

**Input** : URL  
**Output** : 
```json
{
  "type": "product",
  "url": "https://ipln.fr/...",
  "id_product": "1492",
  "id_product_attribute": "2766",
  "has_add_to_cart": true,
  "has_promo_input": false
}
```

**Durée** : ~5s

---

### 2. Promo Scraper

**Rôle** : Détecte promotions actives

**Méthode** :
1. Scraping DOM (prix barré, input)
2. Simulation ajout panier
3. Extraction `window.prestashop.cart.vouchers.added`

**Output** :
```json
{
  "type": "auto_cart_rule",
  "rules": [
    {"id": "1164996", "name": "SONY GM-2", "amount": 400}
  ],
  "complexity": "MEDIUM",
  "server_impact": 0.15
}
```

**Durée** : ~10-15s

**Limitations** :
- Promos visibles/applicables immédiatement uniquement
- Conditions complexes non testées (ex: panier > 1000€)

---

### 3. API PrestaShop (optionnel)

**Rôle** : Enrichissement cart rules

**Endpoints** :
- `GET /api/cart_rules?filter[active]=1`
- `GET /api/cart_rules/{id}`

**Enrichissement** :
- Conditions application
- Type réduction
- Restrictions
- Calcul complexité

**Setup** : Clé API lecture seule (BO PrestaShop)

---

### 4. K6 Generator

**Rôle** : Génère script K6 adapté

**Templates** :
- `template_product.js` : GET page + POST panier
- `template_homepage.js` : GET + charge éléments
- `template_category.js` : GET listing + pagination
- `template_landing.js` : GET page + CTA

**Variables** :
- `{target_users}` : 50/200/500
- `{duration}` : 2min/5min/10min
- `{url}`, `{id_product}`, `{id_attr}`
- `{mode}` : read_only vs full

**Exemple** :
```javascript
export const options = {
    stages: [
        { duration: '1m', target: 200 },
        { duration: '3m', target: 200 },
        { duration: '30s', target: 0 }
    ],
    
    // 🛡️ Protections obligatoires (voir section Mécanismes de Protection)
    thresholds: {
        'http_req_failed': [
            { threshold: 'rate<0.10', abortOnFail: true, delayAbortEval: '10s' }
        ],
        'http_req_duration': [
            { threshold: 'p(95)<5000', abortOnFail: true },
            { threshold: 'p(95)<2000', abortOnFail: false }  // Alerte
        ],
        'checks': [
            { threshold: 'rate>0.80', abortOnFail: true }
        ]
    }
};
```

---

### 5. K6 Executor

**Rôle** : Exécute test + collecte métriques

**Commande** :
```bash
k6 run --out json=/tmp/results.json script.js
```

**Métriques** :
- `http_req_duration` : min/avg/p95/max
- `http_req_failed` : Taux erreurs
- `vus` : VUs actifs/seconde
- `iterations` : Total requêtes
- `data_received` : Bande passante

**Durée** : 2-10min selon paramètre

---

### 6. Results Analyzer

**Rôle** : Parse K6 + calcule scoring

**Calculs** :
1. Score temps réponse (60% poids)
2. Score taux erreur (40% poids)
3. Score global + grade A-F
4. Max users recommandé (seuil p95 > 2s + marge -20%)

**Output** :
```json
{
  "url": "https://ipln.fr/...",
  "page_type": "product",
  "promotion": {...},
  "performance": {
    "p95_response_time": 1850,
    "error_rate": 0.003,
    "max_users_recommended": 520
  },
  "score": {
    "grade": "B",
    "value": 78
  },
  "promo_impact": {
    "overhead_percent": 30,
    "description": "2 codes auto = +30%"
  }
}
```

---

## 📝 Format Output

### Exemple rapport

````markdown
# 📊 ANALYSE DE CHARGE
**URL** : https://ipln.fr/promo/bf2025  
**Type** : Page produit  
**Date** : 26/10/2025 14:30

---

## 🎯 RÉSUMÉ

✅ Capacité suffisante pour Black Friday  
⚠️ 2 codes cumulés réduisent performance de 30%  
💡 Recommandation : Fusionner en 1 code unique

---

## 📈 SCORES

| Critère | Valeur | Grade |
|---------|--------|-------|
| Performance globale | 78/100 | B 🟢 |
| Temps réponse (p95) | 1850ms | B 🟢 |
| Taux d'erreur | 0.3% | A 🟢 |
| Impact promo | +30% | 🟡 |

---

## 👥 CAPACITÉ SERVEUR

- **Tient jusqu'à** : 520 users simultanés
- **BF attendu** : ~500 users pic (19h)
- **Marge** : 20 users (4%)

**Verdict** : ✅ Capacité OK avec marge faible

---

## 🏷️ PROMOTIONS DÉTECTÉES

**2 codes auto-appliqués :**
1. SONY GM-2 : -400€ fixe
2. SONY10 : -10% sur total

**Coût performance** : +30% charge serveur
- Calculs multiples par ajout panier
- 2 vérifications conditions

**Alternative légère** :
- Prix barré -400€ direct
- Réduction charge : -90%
- Gain capacité : +180 users

---

## ✅ RECOMMANDATIONS

### 1. FUSIONNER CODES PROMOS
🔴 **Priorité HAUTE**

**Action** : Créer code unique "SONYBF" (-25%)

**Gain** :
- -40% calculs serveur
- p95 : 1850ms → ~1400ms
- +150 users capacité

**Effort** : 30min (modifier règle BO)  
**Deadline** : J-7 (19 nov)

---

### 2. ACTIVER CACHE FULL PAGE
🔴 **Priorité HAUTE**

**Action** : Cache Smarty full page 19h-21h

**Gain** :
- -60% charge (pages en cache)
- p95 : 1850ms → ~800ms (cache hit)
- +300 users capacité

**Effort** : 15min (config Smarty)  
**Deadline** : J-1 (28 nov)

---

### 3. LIMITER CUMUL CODES
🟡 **Priorité MOYENNE**

**Action** : Max 1 code par panier

**Gain** :
- -50% validation codes
- p95 : 1850ms → ~1250ms
- +120 users capacité

**Effort** : 1h (module Promos)  
**Deadline** : J-3 (23 nov) si possible

---

## 📅 PLAN BLACK FRIDAY

### J-7 (19 nov)
- [ ] Fusionner codes → SONYBF
- [ ] Test PREPROD
- [ ] Validation marketing

### J-3 (23 nov)
- [ ] Limite 1 code max
- [ ] Logs monitoring
- [ ] Test final 500 VUs

### J-1 (28 nov)
- [ ] Cache full page ON
- [ ] OVH Scale 5
- [ ] Pré-chargement cache

### J-0 (29 nov)
- [ ] Dashboard surveillance
- [ ] Alerte Slack si p95 > 2s
- [ ] Équipe standby 18h-22h

---

## 🎓 GLOSSAIRE

- **p95** : 95% des visiteurs < ce temps
- **VUs** : Utilisateurs simulés simultanés
- **Taux erreur** : % requêtes échouées (5xx)

---

*Rapport généré par Claude Code - 26/10/2025*
````

---

## 🚀 Déploiement

### Prérequis

```bash
# Python 3.11+
pip install playwright requests

# K6
brew install k6  # macOS
# ou apt install k6

# Playwright browsers
playwright install chromium
```

### Structure

```
promo-load-analyzer/
├── main.py                 # Entry point Claude Code
├── page_detector.py        # Détection type page
├── promo_scraper.py        # Scraping promotions
├── prestashop_api.py       # API PrestaShop (opt.)
├── k6_generator.py         # Générateur scripts
├── requirements.txt        # Dépendances
├── templates/
│   ├── template_product.js
│   ├── template_homepage.js
│   ├── template_category.js
│   └── template_landing.js
└── .env
    └── PRESTASHOP_API_KEY  # Optionnel
```

### Configuration

```bash
# .env
PRESTASHOP_API_KEY=xxx              # Optionnel
PRESTASHOP_BASE_URL=https://ipln.fr
MAX_USERS_DEFAULT=200
K6_OUTPUT_DIR=/tmp/k6_results
```

### Activation API PrestaShop (optionnel)

```
BO → Paramètres avancés → Webservice
├─> Activer webservice
├─> Créer clé API
│   ├─> Nom: "Load Testing"
│   ├─> Permissions: cart_rules (GET)
│   └─> Générer
└─> Copier clé dans .env
```

---

## 📝 Usage

### Via Claude Code (recommandé)

```
User: "Analyse cette promo BF: https://ipln.fr/objectif-hybride/1492-sony-gm"

Claude Code:
[Exécute main.py avec paramètres détectés]
[Lit /tmp/analysis_XXXXX.json]
[Génère rapport markdown complet]
```

### Ligne de commande

```bash
python main.py \
  --url "https://ipln.fr/promo/bf2025" \
  --env prod \
  --intensity medium \
  --mode read_only

# Output
[1/6] Détection page... → product
[2/6] Analyse promos... → 2 codes auto
[3/6] Génération K6... → template_product.js
[4/6] Test charge... → 200 VUs (5min)
[5/6] Analyse résultats... → Score B (78/100)
[6/6] Export JSON... → /tmp/analysis_XXXXX.json

✅ Analyse terminée
```

---

## 🧪 Tests

### Test rapide

```bash
# Test 1 produit, mode light
python main.py \
  --url "https://preprod.ipln.fr/test-product" \
  --env preprod \
  --intensity light

# Durée: ~2min
```

### Test complet

```bash
# Test stress preprod
python main.py \
  --url "https://preprod.ipln.fr/promo/bf2025" \
  --env preprod \
  --intensity heavy \
  --mode full

# Durée: ~10min
```

---

## 🐛 Troubleshooting

### K6 s'arrête automatiquement

**Symptôme :**
```bash
✗ http_req_failed............: 12.5%
  ↳ threshold [rate<0.10] FAILED
⚠️  ABORTING TEST - Threshold exceeded
```

**Cause :** Threshold de protection déclenché

**Solutions :**
1. **Si PROD** : Site potentiellement surchargé
   - Vérifier logs serveur
   - Réduire VUs (ex: 50 → 25)
   - Attendre période + creuse

2. **Si PREPROD** : Problème application
   - Identifier source erreurs (logs)
   - Corriger bugs
   - Relancer test

3. **Ajuster seuils** (attention !) :
   ```javascript
   // Assouplir temporairement
   'http_req_failed': [
       { threshold: 'rate<0.15', abortOnFail: true }  // 15% au lieu de 10%
   ]
   ```

---

### K6 timeout
```bash
# Augmenter dans template
export const options = {
    httpDebug: 'full',
    timeout: '5m'
};
```

### Playwright browser manquant
```bash
playwright install chromium --force
```

### API PrestaShop 401
```bash
# Vérifier clé
curl -X GET "https://ipln.fr/api/cart_rules" \
  -H "Authorization: Basic $(echo -n 'KEY:' | base64)"
```

### Cloudflare rate limiting
```bash
# Réduire VUs
--intensity light  # 50 VUs

# Ou whitelist IP
# CF Dashboard → Firewall → Rate Limiting → Exception
```

---

## 🔄 Roadmap

### Phase 1 - MVP (< 2 semaines)
- [x] Détection page (produit/homepage/landing)
- [x] Scraping promos (3 types)
- [x] Génération K6 dynamique
- [x] Protections K6 (thresholds abortOnFail)
- [x] Scoring automatique
- [ ] Intégration Claude Code complète
- [ ] Tests validation

### Phase 2 - Post Black Friday
- [ ] Dashboard temps réel (InfluxDB + Grafana)
- [ ] Arrêt d'urgence via dashboard
- [ ] Support catégories + filtres
- [ ] Détection pics automatique
- [ ] Alertes Slack auto
- [ ] Historique comparatif

### Phase 3 - 2026
- [ ] ML prédiction capacité
- [ ] Optimisations auto
- [ ] Tests multi-régions
- [ ] CI/CD integration

---

## 📚 Références

- [K6 Documentation](https://k6.io/docs/)
- [PrestaShop API](https://devdocs.prestashop-project.org/8/webservice/)
- [Playwright Python](https://playwright.dev/python/)
- [Web Performance Standards](https://web.dev/performance/)

---

## 🔒 Limitations & Risques

### Limitations connues

1. **Détection promos** : Uniquement visibles/applicables immédiatement
2. **Max users** : Estimation conservative (MVP), précision Phase 2
3. **Cloudflare** : Rate limiting 50 VUs sans whitelist
4. **PROD** : Tests limités 3h-6h
5. **API** : Optionnelle, améliore précision mais non requise
6. **Protections K6** : Pas de circuit breaker automatique natif, thresholds configurés manuellement

### Risques

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Rate limiting CF | Haute | Moyen | Whitelist IP ou tests PREPROD |
| Impact PROD clients | Faible | Haut | Horaires 3h-6h + protections K6 + max 50 VUs |
| Tests incomplets < BF | Moyenne | Haut | MVP focus essentiel |
| Faux positifs scoring | Faible | Moyen | Validation manuelle recommandations |
| Arrêt auto intempestif | Faible | Moyen | Thresholds testés en PREPROD d'abord |

---

## 👥 Support

**Questions** : Slack #tech-performance  
**Bugs** : Issues repo GitHub  
**Contact** : Direction Technique E-commerce

---

**Version** : 2.0  
**Dernière MAJ** : 26 octobre 2025  
**Prochain test** : Black Friday 2025
