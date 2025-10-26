# 🎛️ Interface & Paramètres

## Workflow conversationnel

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

## Paramètres configurables

### 1. URL & Environnement
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

### 2. Intensité

| Intensité | VUs | Durée | Usage |
|-----------|-----|-------|-------|
| `light` | 50 | 2min | Validation rapide |
| `medium` | 200 | 5min | Test réaliste ✓ défaut |
| `heavy` | 500 | 10min | Stress (preprod uniquement) |

### 3. Mode de test
- `read_only` : GET uniquement (safe, PROD)
- `full` : POST ajout panier (preprod)

### 4. Fenêtre horaire (PROD)
- Tests autorisés : 3h-6h du matin uniquement
- Validation automatique :
  ```python
  if env=='prod' and current_hour not in range(3,6):
      raise Error("Tests PROD: 3h-6h uniquement")
  ```

### 5. Cloudflare whitelist
- `False` : Max 50 VUs (rate limiting)
- `True` : Jusqu'à 500 VUs (config IT requise)

---
