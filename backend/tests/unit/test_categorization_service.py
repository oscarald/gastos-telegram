"""Pruebas del motor de categorizacion (sin base de datos)."""

from __future__ import annotations

import pytest

from app.models.categoria import Categoria
from app.models.regla import Regla
from app.services.categorization_service import (
    matches_keyword,
    normalize_text,
    select_best_rule,
)


def _regla(
    palabra: str,
    categoria: str = "Alimentación",
    prioridad: int = 0,
    activa: bool = True,
    categoria_activa: bool = True,
    regla_id: int = 1,
) -> Regla:
    return Regla(
        id=regla_id,
        palabra_clave=palabra,
        categoria_id=1,
        prioridad=prioridad,
        activa=activa,
        categoria=Categoria(
            id=1,
            nombre=categoria,
            color_hex="#F59E0B",
            activa=categoria_activa,
        ),
    )


class TestNormalizeText:
    def test_quita_acentos_y_mayusculas(self) -> None:
        assert normalize_text("Almuerzo con Ñoño") == "almuerzo con nono"

    def test_colapsa_espacios(self) -> None:
        assert normalize_text("  paseo   al   parque ") == "paseo al parque"

    def test_texto_vacio(self) -> None:
        assert normalize_text("") == ""


class TestMatchesKeyword:
    @pytest.mark.parametrize(
        ("texto", "clave"),
        [
            ("almuerzo en restaurante", "almuerzo"),
            ("ALMUERZO", "almuerzo"),
            ("panadería", "panaderia"),
            ("compra de electronicos", "electronicos"),
        ],
    )
    def test_coincide(self, texto: str, clave: str) -> None:
        assert matches_keyword(normalize_text(texto), normalize_text(clave)) is True

    @pytest.mark.parametrize(
        ("texto", "clave"),
        [
            ("almuerzos con amigos", "almuerzo"),
            ("xalmuerzo", "almuerzo"),
            ("pasaje", "pase"),
            ("prepasaje", "pase"),
        ],
    )
    def test_no_coincide_por_fragmentos(self, texto: str, clave: str) -> None:
        assert matches_keyword(normalize_text(texto), normalize_text(clave)) is False


class TestSelectBestRule:
    def test_sin_coincidencias_devuelve_none(self) -> None:
        reglas = [_regla("almuerzo", regla_id=1)]
        assert select_best_rule("paseo al parque", reglas) is None

    def test_elige_la_de_mayor_prioridad(self) -> None:
        reglas = [
            _regla("comida", prioridad=1, regla_id=1),
            _regla("almuerzo", prioridad=10, regla_id=2),
        ]
        elegido = select_best_rule("almuerzo de hoy", reglas)
        assert elegido is not None
        assert elegido.palabra_clave == "almuerzo"

    def test_desempata_con_la_palabra_mas_larga(self) -> None:
        reglas = [
            _regla("pase", prioridad=5, regla_id=1),
            _regla("paseaje", prioridad=5, regla_id=2),
        ]
        elegido = select_best_rule("paseaje a la oficina", reglas)
        assert elegido is not None
        assert elegido.palabra_clave == "paseaje"

    def test_ignora_reglas_inactivas(self) -> None:
        reglas = [_regla("almuerzo", activa=False, regla_id=1)]
        assert select_best_rule("almuerzo", reglas) is None

    def test_ignora_reglas_de_categorias_inactivas(self) -> None:
        reglas = [_regla("almuerzo", categoria_activa=False, regla_id=1)]
        assert select_best_rule("almuerzo", reglas) is None

    def test_ignora_acentos_en_la_descripcion(self) -> None:
        reglas = [_regla("electricidad", regla_id=1)]
        elegido = select_best_rule("pago de ELECTRICIDAD", reglas)
        assert elegido is not None
        assert elegido.palabra_clave == "electricidad"
