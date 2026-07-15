"""
Automatización de la Importancia Sugerida (IS) vía evidencia bibliográfica
de Scopus, en reemplazo del cuestionario de onboarding.

IS = floor((IL+IE)/2), la misma fórmula (promedio entero) que ya usa el
resto del sistema para IR (ver evaluations.services.calcular_importancia_relativa):
  - IE = Factor.importancia_base (valor experto del catálogo, sin cambios).
  - IL = puntaje 1-4 derivado del volumen de resultados en Scopus para el
    factor (evidencia bibliográfica).

Si Scopus no está configurado, falla, da timeout, o no hay evidencia
suficiente, no se puede calcular IL: se conserva importancia_base tal cual
(regla de fallback), sin tocar la escala 1-4 ni ningún otro cálculo.
"""
import logging

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

SCOPUS_TIMEOUT_SEGUNDOS = 6
SCOPUS_CACHE_TTL_SEGUNDOS = 60 * 60 * 24  # 24h: evita golpear Scopus de nuevo
                                          # por el mismo factor en evaluaciones
                                          # seguidas, sin dejar de ser "en
                                          # tiempo real" en la primera consulta.

# Umbrales de bucketing de IL (documentados y ajustables aquí; no hay una
# heurística "oficial" definida por la tesis para esto). Calibrados contra
# los resultados REALES de Scopus para los 18 factores de GUIOSAD (medidos
# una sola vez, a mano, con la query de abajo; el rango real fue de 0 a
# ~10 500 resultados, repartido de forma muy despareja):
#   < 5 resultados     -> evidencia insuficiente (None -> fallback a importancia_base)
#   5-199              -> IL = 2 (Opcional)
#   200-1499           -> IL = 3 (Importante)
#   1500+              -> IL = 4 (Fundamental)
UMBRAL_EVIDENCIA_MINIMA = 5
UMBRAL_IMPORTANTE = 200
UMBRAL_FUNDAMENTAL = 1500


def _consultar_scopus(termino: str) -> int | None:
    """
    Devuelve el total de resultados de Scopus para el término dado, o None
    si la API no está configurada, falla, da timeout, o responde algo
    inesperado.
    """
    if not settings.SCOPUS_API_KEY:
        return None
    try:
        resp = requests.get(
            settings.SCOPUS_API_URL,
            headers={
                "X-ELS-APIKey": settings.SCOPUS_API_KEY,
                "Accept": "application/json",
            },
            params={
                "query": (
                    f'TITLE-ABS-KEY("{termino}") AND TITLE-ABS-KEY('
                    '"open source software" OR "free and open source software" '
                    'OR FLOSS OR "OSS adoption")'
                ),
            },
            timeout=SCOPUS_TIMEOUT_SEGUNDOS,
        )
        resp.raise_for_status()
        return int(resp.json()["search-results"]["opensearch:totalResults"])
    except (requests.RequestException, KeyError, ValueError, TypeError) as exc:
        logger.warning("Scopus no disponible para %r: %s", termino, exc)
        return None


def _bucket_a_il(total_resultados: int) -> int | None:
    if total_resultados < UMBRAL_EVIDENCIA_MINIMA:
        return None
    if total_resultados < UMBRAL_IMPORTANTE:
        return 2
    if total_resultados < UMBRAL_FUNDAMENTAL:
        return 3
    return 4


def calcular_importancia_sugerida(factor) -> int:
    """
    Importancia Sugerida (IS) de un factor para una nueva evaluación.

    IS = floor((IL+IE)/2) si hay evidencia suficiente en Scopus;
    si no, IS = IE (factor.importancia_base) sin cambios.
    """
    cache_key = f"scopus_il_factor_{factor.id}"
    il = cache.get(cache_key, "__sin_cache__")
    if il == "__sin_cache__":
        termino = factor.termino_busqueda_en or factor.nombre
        total_resultados = _consultar_scopus(termino)
        il = _bucket_a_il(total_resultados) if total_resultados is not None else None
        cache.set(cache_key, il, SCOPUS_CACHE_TTL_SEGUNDOS)

    if il is None:
        return factor.importancia_base
    return (il + factor.importancia_base) // 2
