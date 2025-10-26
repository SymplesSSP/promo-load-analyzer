# 🔒 Limitations & Risques

## Limitations connues

1. **Détection promos** : Uniquement visibles/applicables immédiatement
2. **Max users** : Estimation conservative (MVP), précision Phase 2
3. **Cloudflare** : Rate limiting 50 VUs sans whitelist
4. **PROD** : Tests limités 3h-6h
5. **API** : Optionnelle, améliore précision mais non requise
6. **Protections K6** : Pas de circuit breaker automatique natif, thresholds configurés manuellement

## Risques

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Rate limiting CF | Haute | Moyen | Whitelist IP ou tests PREPROD |
| Impact PROD clients | Faible | Haut | Horaires 3h-6h + protections K6 + max 50 VUs |
| Tests incomplets < BF | Moyenne | Haut | MVP focus essentiel |
| Faux positifs scoring | Faible | Moyen | Validation manuelle recommandations |
| Arrêt auto intempestif | Faible | Moyen | Thresholds testés en PREPROD d'abord |

---
