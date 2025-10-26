# 📝 Format Output

## Exemple rapport

````markdown
# 📊 ANALYSE DE CHARGE
**URL** : https://ipln.fr/promo/bf2025  
**Type** : Page produit  
**Date** : 26/10/2025 14:30

---

# 🎯 RÉSUMÉ

✅ Capacité suffisante pour Black Friday  
⚠️ 2 codes cumulés réduisent performance de 30%  
💡 Recommandation : Fusionner en 1 code unique

---

# 📈 SCORES

| Critère | Valeur | Grade |
|---------|--------|-------|
| Performance globale | 78/100 | B 🟢 |
| Temps réponse (p95) | 1850ms | B 🟢 |
| Taux d'erreur | 0.3% | A 🟢 |
| Impact promo | +30% | 🟡 |

---

# 👥 CAPACITÉ SERVEUR

- **Tient jusqu'à** : 520 users simultanés
- **BF attendu** : ~500 users pic (19h)
- **Marge** : 20 users (4%)

**Verdict** : ✅ Capacité OK avec marge faible

---

# 🏷️ PROMOTIONS DÉTECTÉES

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

# ✅ RECOMMANDATIONS

## 1. FUSIONNER CODES PROMOS
🔴 **Priorité HAUTE**

**Action** : Créer code unique "SONYBF" (-25%)

**Gain** :
- -40% calculs serveur
- p95 : 1850ms → ~1400ms
- +150 users capacité

**Effort** : 30min (modifier règle BO)  
**Deadline** : J-7 (19 nov)

---

## 2. ACTIVER CACHE FULL PAGE
🔴 **Priorité HAUTE**

**Action** : Cache Smarty full page 19h-21h

**Gain** :
- -60% charge (pages en cache)
- p95 : 1850ms → ~800ms (cache hit)
- +300 users capacité

**Effort** : 15min (config Smarty)  
**Deadline** : J-1 (28 nov)

---

## 3. LIMITER CUMUL CODES
🟡 **Priorité MOYENNE**

**Action** : Max 1 code par panier

**Gain** :
- -50% validation codes
- p95 : 1850ms → ~1250ms
- +120 users capacité

**Effort** : 1h (module Promos)  
**Deadline** : J-3 (23 nov) si possible

---

# 📅 PLAN BLACK FRIDAY

## J-7 (19 nov)
- [ ] Fusionner codes → SONYBF
- [ ] Test PREPROD
- [ ] Validation marketing

## J-3 (23 nov)
- [ ] Limite 1 code max
- [ ] Logs monitoring
- [ ] Test final 500 VUs

## J-1 (28 nov)
- [ ] Cache full page ON
- [ ] OVH Scale 5
- [ ] Pré-chargement cache

## J-0 (29 nov)
- [ ] Dashboard surveillance
- [ ] Alerte Slack si p95 > 2s
- [ ] Équipe standby 18h-22h

---

# 🎓 GLOSSAIRE

- **p95** : 95% des visiteurs < ce temps
- **VUs** : Utilisateurs simulés simultanés
- **Taux erreur** : % requêtes échouées (5xx)

---

*Rapport généré par Claude Code - 26/10/2025*
````

---
