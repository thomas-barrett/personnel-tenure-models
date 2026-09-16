from ptm.parse.rules import classify
from tests import fixtures_rules as F


def _c(fx):
    return classify(fx["rules_primary"], fx["rules_secondary"])


def test_effectiveleave_admin_is_vacate_rule():
    rv = _c(F.EFFECTIVELEAVE_ADMIN)
    assert rv.trigger == "vacate"
    assert not rv.competing and not rv.any_member
    assert rv.death_scalar and not rv.death_not_yes
    assert rv.temp_absence_excluded
    assert rv.term_expiration_counts
    assert rv.reoccupy_settles_initial
    assert rv.window_end == "2027-01-01"   # "before 2027"
    assert rv.window_start is None


def test_hegseth_monthly_window_parses():
    rv = _c(F.HEGSETH)
    assert rv.trigger == "vacate"
    assert rv.window_end == "2026-12-01"


def test_leadersout_is_announce_or_vacate_with_one_year_cap():
    rv = _c(F.LEADERSOUT)
    assert rv.trigger == "announce_or_vacate"
    assert rv.one_year_cap
    assert rv.death_not_yes
    assert rv.forced_departure_counts
    assert rv.term_expiration_counts
    assert rv.window_end == "2027-01-01"


def test_cabout_competing_field_with_tie_break():
    rv = _c(F.CABOUT)
    assert rv.competing
    assert rv.trigger == "announce_or_vacate"
    assert rv.tie_break == "leave_first_then_alpha"
    assert rv.acting_excluded
    assert rv.death_not_yes and not rv.death_scalar
    assert rv.window_start == "2026-05-22"
    assert rv.window_end is None


def test_cableave_any_member_with_carveout_and_president_announcement():
    rv = _c(F.CABLEAVE)
    assert rv.any_member
    assert rv.trigger == "announce_or_vacate"
    assert rv.president_announcement_counts
    assert rv.excluded_persons == ("Tulsi Gabbard",)
    assert rv.acting_excluded
    assert rv.window_end == "2027-01-01"


def test_ukcabout_is_announcement_triggered_and_voids_on_pm_change():
    rv = _c(F.UKCABOUT)
    assert rv.trigger == "announce"
    assert rv.competing
    assert rv.tie_break == "split_settlement"
    assert rv.field_void_on_head_change
    assert rv.window_end == "2028-01-01"


def test_g7_and_africa_are_vacate_competing_with_scalar_death():
    for fx in (F.G7, F.AFRICA):
        rv = _c(fx)
        assert rv.trigger == "vacate", fx
        assert rv.competing
        assert rv.death_scalar
        assert not rv.death_not_yes


def test_alito_effective_date_vs_thomas_announcement():
    a = _c(F.ALITO)
    t = _c(F.THOMAS_ANNOUNCE)
    assert a.trigger == "vacate"
    assert t.trigger == "announce"
    assert a.window_end == "2027-07-01" and t.window_end == "2028-01-01"


def test_scotusresign_announce_or_vacate_death_not_yes():
    rv = _c(F.SCOTUSRESIGN)
    assert rv.trigger == "announce_or_vacate"
    assert rv.death_not_yes and not rv.death_scalar
    assert rv.window_end == "2029-01-20"


def test_powell_term_limit_acknowledgement_excluded():
    rv = _c(F.POWELL)
    assert rv.trigger == "announce_or_vacate"
    assert rv.term_limit_ack_excluded
    assert rv.one_year_cap
    assert rv.death_not_yes


def test_cook_announce_or_vacate():
    rv = _c(F.COOK)
    assert rv.trigger == "announce_or_vacate"
    assert rv.one_year_cap
    assert rv.death_not_yes
    assert rv.forced_departure_counts


def test_warsh_vacate_with_term_expiration():
    rv = _c(F.WARSH)
    assert rv.trigger == "vacate"
    assert rv.term_expiration_counts
    assert rv.window_end == "2031-01-01"


def test_hash_changes_when_wording_changes():
    a = _c(F.HEGSETH)
    b = classify(F.HEGSETH["rules_primary"], F.HEGSETH["rules_secondary"] + " ")
    assert a.rules_sha256 != b.rules_sha256


def test_unknown_text_yields_none_not_guess():
    rv = classify("If X happens, then the market resolves to Yes.", "")
    assert rv.trigger is None
    assert rv.window_end is None
