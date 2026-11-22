import pytest

from app.core.stats_utils import t_critical, z_critical


def test_z_critical_95() -> None:
    assert z_critical(0.05) == pytest.approx(1.96, abs=0.001)


def test_z_critical_99() -> None:
    assert z_critical(0.01) == pytest.approx(2.576, abs=0.001)


def test_t_critical_df11() -> None:
    assert t_critical(0.05, 11) == pytest.approx(2.201, abs=0.001)


def test_t_critical_approaches_z_for_large_df() -> None:
    assert t_critical(0.05, 10_000) == pytest.approx(z_critical(0.05), abs=0.01)


def test_invalid_alpha() -> None:
    with pytest.raises(ValueError):
        z_critical(1.5)
