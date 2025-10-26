# 🧪 Tests

## Test rapide

```bash
# Test 1 produit, mode light
python main.py \
  --url "https://preprod.ipln.fr/test-product" \
  --env preprod \
  --intensity light

# Durée: ~2min
```

## Test complet

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
