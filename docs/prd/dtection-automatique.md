# 🔍 Détection Automatique

## Types de pages

| Type | Pattern URL | Analyse | Durée |
|------|-------------|---------|-------|
| **Produit** | `/\d+-[\w-]+\.html` | Promos + panier | 5min |
| **Homepage** | `^https?://[^/]+/?$` | Charge globale | 3min |
| **Catégorie** | `/[\w-]+/\d+` | Listing | 4min |
| **Landing** | Autre | DOM | 3min |

## Types de promotions

### Prix barré (Striked Price)
**Détection** : CSS `.regular-price`  
**Impact** : ~5% charge serveur (pré-calculé)  
**Complexité** : LOW

```html
<span class="regular-price">2 299,00 €</span>
<span class="current-price">1 899,00 €</span>
```

### Code auto (Auto Cart Rule)
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

### Code manuel (Manual Code)
**Détection** : Input `[name="discount_name"]`  
**Impact** : ~25% charge serveur  
**Complexité** : HIGH

**⚠️ Note** : Impacts = estimations heuristiques, validation Phase 2

---
