# 🎯 Objectifs & Contexte

## Contexte technique
- **Platform:** PrestaShop 1.7.8.5
- **Hosting:** OVH Scale 3 (normal) / Scale 5 (Black Friday)
- **CDN:** Cloudflare actif + WAF
- **Cache:** Smarty
- **Module promos:** "Promotions et Discount"

## Objectifs business
1. **Préventif** : Identifier promos lourdes AVANT mise en ligne
2. **Capacité** : Nombre max users simultanés supportés
3. **Optimisation** : Alternatives légères (prix barré vs code auto)
4. **Monitoring** : Tests réguliers périodes promo

## Contraintes
- **PROD** : Tests avec précautions (horaires 3h-6h, max 50 VUs sans whitelist CF)
- **PREPROD** : Tests sans limitations
- **Cloudflare** : Rate limiting 50-100 VUs/IP
- **Délai MVP** : < 2 semaines avant Black Friday 2025

---
