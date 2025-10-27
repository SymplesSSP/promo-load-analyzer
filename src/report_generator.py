"""Generate markdown reports from K6 test results."""

from datetime import datetime
from typing import cast

from src.models.k6_results import K6ExecutionResult
from src.models.promotion import AutoCartRule, PromotionData, StrikedPriceData


class ReportGenerator:
    """Generates formatted markdown reports from test results."""

    def generate_report(
        self,
        result: K6ExecutionResult,
        promotions: dict[str, any] | PromotionData | None = None,  # type: ignore[valid-type]
    ) -> str:
        """Generate complete markdown report.

        Args:
            result: K6 execution result with analysis
            promotions: Detected promotions (optional)

        Returns:
            Formatted markdown report
        """
        sections = [
            self._generate_header(result),
            self._generate_summary(result),
            self._generate_scores(result),
            self._generate_capacity(result),
        ]

        if promotions:
            # Handle both dict and PromotionData
            has_promos = False
            if isinstance(promotions, dict):
                has_promos = bool(
                    promotions.get("striked_price")
                    or promotions.get("auto_cart_rules")
                    or promotions.get("has_manual_code_input")
                )
            else:
                has_promos = bool(
                    promotions.striked_price
                    or promotions.auto_cart_rules
                    or promotions.has_manual_code_input
                )

            if has_promos:
                sections.append(self._generate_promotions(promotions))

        sections.append(self._generate_recommendations(result))

        if not result.success:
            sections.append(self._generate_error_section(result))

        sections.append(self._generate_technical_details(result))
        sections.append(self._generate_glossary())

        return "\n\n".join(sections)

    def _generate_header(self, result: K6ExecutionResult) -> str:
        """Generate report header."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return f"""# 📊 ANALYSE DE CHARGE - PROMO LOAD ANALYZER

**URL testée:** {result.url}
**Type de page:** {result.page_type}
**Environnement:** {result.environment.upper()}
**Intensité:** {result.intensity}
**Date:** {timestamp}

---"""

    def _generate_summary(self, result: K6ExecutionResult) -> str:
        """Generate executive summary."""
        if not result.success:
            return """## 🎯 RÉSUMÉ EXÉCUTIF

❌ **Test échoué** - Le test n'a pas pu être complété.

Consultez la section "Détails Techniques" ci-dessous pour plus d'informations."""

        overall_grade = result.overall_grade
        if not overall_grade:
            return """## 🎯 RÉSUMÉ EXÉCUTIF

⚠️ **Analyse incomplète** - Les résultats n'ont pas pu être analysés."""

        grade_emoji = {
            "A": "🟢",
            "B": "🟢",
            "C": "🟡",
            "D": "🟠",
            "F": "🔴",
        }

        emoji = grade_emoji.get(overall_grade.grade, "⚪")
        status_text = self._get_status_text(overall_grade.grade)

        summary = f"""## 🎯 RÉSUMÉ EXÉCUTIF

{emoji} **{status_text}**"""

        # Add key findings
        if result.threshold_failed:
            summary += "\n⚠️ Les seuils de sécurité K6 ont été dépassés pendant le test"

        if result.max_users_estimate and result.metrics:
            margin = result.max_users_estimate - result.metrics.vus_max
            margin_pct = (margin / result.max_users_estimate) * 100
            if margin_pct < 20:
                summary += f"\n⚠️ Marge de capacité faible: {margin_pct:.0f}% ({margin} utilisateurs)"

        return summary

    def _generate_scores(self, result: K6ExecutionResult) -> str:
        """Generate scores section."""
        if not result.success or not result.overall_grade:
            return ""

        rt_grade = result.response_time_grade
        err_grade = result.error_rate_grade
        overall_grade = result.overall_grade

        grade_emoji = {"A": "🟢", "B": "🟢", "C": "🟡", "D": "🟠", "F": "🔴"}

        metrics = result.metrics
        if not metrics:
            return ""

        if not rt_grade or not err_grade:
            return ""

        return f"""## 📈 SCORES DE PERFORMANCE

| Critère | Valeur | Score | Grade |
|---------|--------|-------|-------|
| **Performance globale** | - | {overall_grade.score:.1f}/100 | **{overall_grade.grade}** {grade_emoji.get(overall_grade.grade, '⚪')} |
| Temps de réponse (p95) | {metrics.http_req_duration_p95:.0f}ms | {rt_grade.score:.1f}/100 | {rt_grade.grade} {grade_emoji.get(rt_grade.grade, '⚪')} |
| Taux d'erreur | {metrics.http_req_failed_rate*100:.2f}% | {err_grade.score:.1f}/100 | {err_grade.grade} {grade_emoji.get(err_grade.grade, '⚪')} |

**Interprétation:**
- {rt_grade.description}
- {err_grade.description}
- {overall_grade.description}"""

    def _generate_capacity(self, result: K6ExecutionResult) -> str:
        """Generate server capacity section."""
        if not result.success or not result.max_users_estimate or not result.metrics:
            return ""

        max_users = result.max_users_estimate
        tested_vus = result.metrics.vus_max
        margin = max_users - tested_vus
        margin_pct = (margin / max_users) * 100 if max_users > 0 else 0

        verdict_emoji = "✅" if margin_pct >= 20 else "⚠️" if margin_pct >= 10 else "🔴"
        verdict_text = (
            "Capacité suffisante avec bonne marge"
            if margin_pct >= 20
            else "Capacité limite, surveillance recommandée"
            if margin_pct >= 10
            else "Capacité insuffisante - CRITIQUE"
        )

        return f"""## 👥 CAPACITÉ SERVEUR

- **Utilisateurs testés:** {tested_vus} VUs simultanés
- **Capacité estimée:** ~{max_users} utilisateurs maximum
- **Marge de sécurité:** {margin} utilisateurs ({margin_pct:.1f}%)

{verdict_emoji} **Verdict:** {verdict_text}

**Note:** L'estimation est basée sur une extrapolation linéaire avec un seuil de p95 < 2000ms et une marge de sécurité de 20%."""

    def _generate_promotions(self, promotions: dict[str, any] | PromotionData) -> str:  # type: ignore[valid-type]
        """Generate promotions section."""
        section = "## 🏷️ PROMOTIONS DÉTECTÉES\n\n"

        promo_count = 0
        details = []

        # Handle both dict and PromotionData
        if isinstance(promotions, dict):
            striked_price_raw = promotions.get("striked_price")
            striked_price = cast(
                StrikedPriceData | None, striked_price_raw
            ) if striked_price_raw else None
            auto_cart_rules_raw = promotions.get("auto_cart_rules", [])
            auto_cart_rules = cast(
                list[AutoCartRule],
                auto_cart_rules_raw if isinstance(auto_cart_rules_raw, list) else []
            )
            has_manual_code_input = bool(promotions.get("has_manual_code_input", False))
        else:
            striked_price = promotions.striked_price
            auto_cart_rules = promotions.auto_cart_rules
            has_manual_code_input = promotions.has_manual_code_input

        if striked_price:
            promo_count += 1
            sp = striked_price
            discount = ((sp.regular_price - sp.current_price) / sp.regular_price) * 100
            details.append(
                f"**Prix barré** - {sp.regular_price:.2f}{sp.currency} → {sp.current_price:.2f}{sp.currency} (-{discount:.0f}%)"
            )

        if auto_cart_rules:
            for rule in auto_cart_rules:
                promo_count += 1
                if rule.discount_type == "percentage":
                    details.append(
                        f"**{rule.rule_name}** - Réduction de {rule.amount:.0f}%"
                    )
                elif rule.discount_type == "amount":
                    details.append(
                        f"**{rule.rule_name}** - Réduction de {rule.amount:.2f}€"
                    )
                else:
                    details.append(f"**{rule.rule_name}** - {rule.discount_type}")

        if has_manual_code_input:
            details.append("**Input manuel** - Champ de saisie de code promo détecté")

        section += f"**Nombre de promotions actives:** {promo_count}\n\n"
        for detail in details:
            section += f"- {detail}\n"

        # Calculate complexity and impact (handle both dict and PromotionData)
        if isinstance(promotions, dict):
            complexity = self._calculate_complexity_from_dict(promotions)
            impact = self._estimate_impact_from_dict(promotions)
        else:
            complexity = promotions.calculate_complexity()
            impact = promotions.estimate_server_impact()

        section += f"\n**Complexité:** {complexity}"
        section += f"\n**Impact serveur estimé:** +{impact*100:.0f}% de charge"

        return section

    def _generate_recommendations(self, result: K6ExecutionResult) -> str:
        """Generate recommendations section."""
        from src.results_analyzer import ResultsAnalyzer

        analyzer = ResultsAnalyzer()
        recommendations = analyzer.get_recommendations(result)

        section = "## 💡 RECOMMANDATIONS\n\n"

        high_priority = [r for r in recommendations if "🔴" in r]
        medium_priority = [r for r in recommendations if "🟡" in r]
        low_priority = [r for r in recommendations if "🟢" in r or "✅" in r]

        if high_priority:
            section += "### 🔴 Priorité HAUTE\n\n"
            for rec in high_priority:
                section += f"- {rec.replace('🔴 HIGH: ', '')}\n"
            section += "\n"

        if medium_priority:
            section += "### 🟡 Priorité MOYENNE\n\n"
            for rec in medium_priority:
                section += f"- {rec.replace('🟡 MEDIUM: ', '')}\n"
            section += "\n"

        if low_priority:
            section += "### ✅ Points positifs\n\n"
            for rec in low_priority:
                section += f"- {rec}\n"
            section += "\n"

        return section.rstrip()

    def _generate_error_section(self, result: K6ExecutionResult) -> str:
        """Generate error details section."""
        if result.success:
            return ""

        return f"""## ❌ DÉTAILS DE L'ERREUR

**Message:** {result.error_message or 'Erreur inconnue'}

**Durée avant échec:** {result.duration_seconds:.1f} secondes

**Actions suggérées:**
- Vérifier que l'URL est accessible
- Vérifier que K6 est installé (`k6 version`)
- Consulter les logs pour plus de détails
- Réessayer avec une intensité plus faible"""

    def _generate_technical_details(self, result: K6ExecutionResult) -> str:
        """Generate technical details section."""
        if not result.success or not result.metrics:
            return f"""## 🔧 DÉTAILS TECHNIQUES

**URL:** {result.url}
**Type de page:** {result.page_type}
**Environnement:** {result.environment}
**Intensité:** {result.intensity}
**Durée:** {result.duration_seconds:.1f}s
**Succès:** {'✅' if result.success else '❌'}
**Seuils dépassés:** {'⚠️ Oui' if result.threshold_failed else '✅ Non'}"""

        m = result.metrics

        return f"""## 🔧 DÉTAILS TECHNIQUES

**Configuration du test:**
- URL: {result.url}
- Type de page: {result.page_type}
- Environnement: {result.environment}
- Intensité: {result.intensity}
- Durée totale: {result.duration_seconds:.1f}s
- Seuils K6 dépassés: {'⚠️ Oui' if result.threshold_failed else '✅ Non'}

**Métriques détaillées:**
- Temps de réponse (min/avg/p95/p99/max): {m.http_req_duration_min:.0f} / {m.http_req_duration_avg:.0f} / {m.http_req_duration_p95:.0f} / {m.http_req_duration_p99:.0f} / {m.http_req_duration_max:.0f} ms
- Requêtes totales: {m.http_req_total_count}
- Requêtes échouées: {m.http_req_failed_count} ({m.http_req_failed_rate*100:.2f}%)
- Taux de réussite des checks: {m.checks_rate*100:.1f}%
- VUs maximum: {m.vus_max}
- Itérations: {m.iterations}
- Données reçues: {m.data_received_bytes / 1024 / 1024:.2f} MB
- Données envoyées: {m.data_sent_bytes / 1024:.2f} KB"""

    def _generate_glossary(self) -> str:
        """Generate glossary for non-technical users."""
        return """## 📚 GLOSSAIRE

**Termes techniques expliqués pour l'équipe marketing:**

- **p95 (percentile 95):** Temps de réponse maximal pour 95% des requêtes. Par exemple, un p95 de 1500ms signifie que 95% des visiteurs ont eu une réponse en moins de 1,5 seconde.

- **Taux d'erreur:** Pourcentage de requêtes qui ont échoué (erreurs serveur, timeouts, etc.). Un taux élevé indique un problème de stabilité.

- **VUs (Virtual Users):** Nombre d'utilisateurs simultanés simulés pendant le test. Plus il y a de VUs, plus la charge sur le serveur est importante.

- **Seuils K6:** Limites de sécurité configurées pour arrêter le test automatiquement si le serveur se dégrade trop (trop d'erreurs ou réponses trop lentes).

- **Capacité estimée:** Nombre maximum d'utilisateurs simultanés que le serveur peut supporter tout en maintenant des performances acceptables (p95 < 2s).

- **Marge de sécurité:** Pourcentage de capacité restante. Une marge de 20% signifie qu'on peut accueillir 20% d'utilisateurs supplémentaires avant d'atteindre la limite.

---

*Rapport généré par Promo Load Analyzer - https://github.com/anthropics/claude-code*"""

    def _get_status_text(self, grade: str) -> str:
        """Get status text from grade."""
        status_map = {
            "A": "Performance excellente - Prêt pour le trafic Black Friday",
            "B": "Bonnes performances - Déploiement recommandé",
            "C": "Performances acceptables - Monitoring recommandé",
            "D": "Performances insuffisantes - Optimisation nécessaire",
            "F": "Performances critiques - Ne pas déployer en production",
        }
        return status_map.get(grade, "Statut inconnu")

    def _calculate_complexity_from_dict(self, promotions: dict[str, any]) -> str:  # type: ignore[valid-type]
        """Calculate promotion complexity from dict data.

        Rules:
            - LOW: Only striked price
            - MEDIUM: 1 auto cart rule OR manual code input
            - HIGH: 2+ auto cart rules OR manual + auto
        """
        has_striked = promotions.get("striked_price") is not None
        auto_cart_rules = promotions.get("auto_cart_rules", [])
        num_auto_rules = len(auto_cart_rules)
        has_manual = promotions.get("has_manual_code_input", False)

        if num_auto_rules >= 2 or (has_manual and num_auto_rules >= 1):
            return "HIGH"
        elif num_auto_rules == 1 or has_manual:
            return "MEDIUM"
        elif has_striked:
            return "LOW"
        else:
            return "LOW"

    def _estimate_impact_from_dict(self, promotions: dict[str, any]) -> float:  # type: ignore[valid-type]
        """Estimate server impact from dict data.

        Impact factors:
            - Striked price: +0.05
            - Each auto cart rule: +0.15
            - Manual code input: +0.25
        """
        impact = 0.0

        if promotions.get("striked_price") is not None:
            impact += 0.05

        auto_cart_rules = promotions.get("auto_cart_rules", [])
        impact += len(auto_cart_rules) * 0.15

        if promotions.get("has_manual_code_input", False):
            impact += 0.25

        return min(impact, 1.0)  # Cap at 1.0
