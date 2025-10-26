# External APIs

## PrestaShop Webservice API (Optional)

- **Purpose:** Enrich promotional rule data with conditions, restrictions, priorities
- **Base URL:** `https://ipln.fr/api` (PROD) | `https://preprod.ipln.fr/api` (PREPROD)
- **Authentication:** HTTP Basic Auth (API Key as username, no password)
- **Key Endpoints:**
  - `GET /api/cart_rules?filter[active]=1` - List active cart rules
  - `GET /api/cart_rules/{id}` - Get cart rule details

**Graceful Degradation:** If API key absent or API fails, continues with scraping data only.

---
