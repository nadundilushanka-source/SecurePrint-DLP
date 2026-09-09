"""Policy engine decisions per classification (spec section 20)."""


def test_public_policy_allows_print_without_alert(engine):
    decision = engine.policy_engine.evaluate_policy(
        "PUBLIC",
        {"require_alert": False, "require_masking": False, "require_watermark": False, "require_footer": True, "allow_printing": True},
    )
    assert decision.can_auto_release is True
    assert decision.require_masking is False


def test_confidential_requires_alert_and_masking(engine):
    decision = engine.policy_engine.evaluate_policy(
        "CONFIDENTIAL",
        {"require_alert": True, "require_masking": True, "require_watermark": False, "require_footer": True, "allow_printing": True},
    )
    assert decision.can_auto_release is False
    assert decision.require_masking is True
    assert decision.require_watermark is False


def test_restricted_requires_alert_masking_and_watermark(engine):
    decision = engine.policy_engine.evaluate_policy(
        "RESTRICTED",
        {"require_alert": True, "require_masking": True, "require_watermark": True, "require_footer": True, "allow_printing": True},
    )
    assert decision.can_auto_release is False
    assert decision.require_masking is True
    assert decision.require_watermark is True


def test_policy_denying_printing_never_auto_releases(engine):
    decision = engine.policy_engine.evaluate_policy(
        "RESTRICTED",
        {"require_alert": True, "require_masking": True, "require_watermark": True, "require_footer": True, "allow_printing": False},
    )
    assert decision.can_auto_release is False
    assert decision.allow_printing is False
