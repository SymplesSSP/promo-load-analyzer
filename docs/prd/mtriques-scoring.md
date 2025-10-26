# 📊 Métriques & Scoring

## Métriques collectées

| Métrique | Description | Seuil alerte |
|----------|-------------|--------------|
| **p95 Response** | 95% requêtes < X ms | > 2000ms |
| **Error Rate** | % requêtes 5xx/timeout | > 1% |
| **Max Users** | VUs max avant dégradation | Variable |
| **Promo Impact** | Overhead charge | Calculé |

## Seuils standards web

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

## Score global

```python
score = (score_response * 0.6) + (score_error * 0.4)
grade = A/B/C/D/F
```

## Détection Max Users

**Méthode** :
1. Test progressif : 50 → 100 → 200 → 500 VUs
2. Surveillance p95 chaque palier
3. Détection seuil p95 > 2000ms
4. Marge sécurité -20%

**MVP** : Estimation conservative (extrapolation linéaire)  
**Phase 2** : Détection précise via analyse courbe

---
