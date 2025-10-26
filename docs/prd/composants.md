# 🔧 Composants

## 1. Page Detector

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

## 2. Promo Scraper

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

## 3. API PrestaShop (optionnel)

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

## 4. K6 Generator

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

## 5. K6 Executor

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

## 6. Results Analyzer

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
