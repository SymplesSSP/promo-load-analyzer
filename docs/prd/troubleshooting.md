# 🐛 Troubleshooting

## K6 s'arrête automatiquement

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

## K6 timeout
```bash
# Augmenter dans template
export const options = {
    httpDebug: 'full',
    timeout: '5m'
};
```

## Playwright browser manquant
```bash
playwright install chromium --force
```

## API PrestaShop 401
```bash
# Vérifier clé
curl -X GET "https://ipln.fr/api/cart_rules" \
  -H "Authorization: Basic $(echo -n 'KEY:' | base64)"
```

## Cloudflare rate limiting
```bash
# Réduire VUs
--intensity light  # 50 VUs

# Ou whitelist IP
# CF Dashboard → Firewall → Rate Limiting → Exception
```

---
