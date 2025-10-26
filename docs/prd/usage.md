# 📝 Usage

## Via Claude Code (recommandé)

```
User: "Analyse cette promo BF: https://ipln.fr/objectif-hybride/1492-sony-gm"

Claude Code:
[Exécute main.py avec paramètres détectés]
[Lit /tmp/analysis_XXXXX.json]
[Génère rapport markdown complet]
```

## Ligne de commande

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
