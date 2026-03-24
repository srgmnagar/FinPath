import random
from datetime import datetime
from event_builder import *

# ── Drop-off probabilities (industry-realistic for Indian robo-advisory) ─────
P = {
    "signup_complete":          0.70,
    "email_verify":             0.85,
    "onboarding_complete":      0.90,
    "risk_quiz_complete":       0.60,
    "kyc_attempt":              0.95,
    "kyc_pass":                 0.85,
    "kyc_retry_pass":           0.60,
    "bank_link":                0.87,
    "deposit_attempt":          0.85,
    "deposit_success":          0.88,
    "portfolio_create":         0.95,
    "auto_invest_enable":       0.40,
    "goal_create":              0.55,
    "becomes_churner":          0.08,
    "portfolio_close":          0.04,
}

# Average seconds between stages (adds realism to timestamps)
GAPS = {
    "app_to_signup":            (5,   120),
    "signup_steps":             (30,  300),
    "email_verify":             (60,  1800),
    "onboarding_steps":         (60,  600),
    "quiz_per_question":        (10,  60),
    "kyc_steps":                (120, 900),
    "bank_link":                (60,  600),
    "deposit_steps":            (30,  300),
    "portfolio_setup":          (30,  180),
    "between_sessions":         (3600, 86400 * 7),
    "engagement_event":         (60,  3600),
}


def gap(key: str) -> int:
    lo, hi = GAPS[key]
    return random.randint(lo, hi)


def simulate_user(user: dict) -> tuple[dict, list[dict]]:
    """
    Returns (updated_user, events_list).
    updated_user has activated_at and first_deposit_at set if applicable.
    """
    uid         = user["user_id"]
    risk        = user["risk_profile"]
    device      = user["device_type"]
    ts          = user["signup_at"]
    events      = []
    sid         = new_session()

    # ── Phase 1: Acquisition ─────────────────────────────────────────────────
    events.append(evt_app_opened(uid, ts, sid, device))
    ts = jitter(ts, *GAPS["app_to_signup"])
    events.append(evt_landing_page_viewed(uid, ts, sid))
    ts = jitter(ts, 5, 60)
    events.append(evt_signup_started(uid, ts, sid))

    if not _pass(P["signup_complete"]):
        return user, events                             # drop-off: never signed up

    ts = jitter(ts, *GAPS["signup_steps"])
    events.append(evt_signup_completed(uid, ts, sid))

    if not _pass(P["email_verify"]):
        return user, events                             # drop-off: no email verify

    ts = jitter(ts, *GAPS["email_verify"])
    events.append(evt_email_verified(uid, ts, sid))

    # ── Phase 2: Onboarding ───────────────────────────────────────────────────
    ts = jitter(ts, *GAPS["onboarding_steps"])
    sid = new_session()
    events.append(evt_onboarding_started(uid, ts, sid))
    ts = jitter(ts, *GAPS["onboarding_steps"])
    events.append(evt_profile_completed(uid, ts, sid))
    ts = jitter(ts, 30, 120)
    events.append(evt_investment_goal_selected(uid, ts, sid))

    if not _pass(P["onboarding_complete"]):
        return user, events

    ts = jitter(ts, 30, 120)
    events.append(evt_onboarding_completed(uid, ts, sid))

    # ── Phase 3: Risk profiling ───────────────────────────────────────────────
    ts = jitter(ts, *GAPS["between_sessions"])
    sid = new_session()
    events.append(evt_risk_quiz_started(uid, ts, sid))

    n_questions = len(RISK_QUESTIONS)
    completed_questions = 0
    for i in range(n_questions):
        ts = jitter(ts, *GAPS["quiz_per_question"])
        events.append(evt_risk_question_answered(uid, ts, sid, i))
        completed_questions += 1
        # mid-quiz drop-off more likely in first 3 questions
        if i < 3 and not _pass(0.92):
            break
        elif i >= 3 and not _pass(0.97):
            break

    if completed_questions < n_questions:
        return user, events                             # drop-off: quiz abandoned

    if not _pass(P["risk_quiz_complete"]):
        return user, events

    ts = jitter(ts, 5, 30)
    events.append(evt_risk_quiz_completed(uid, ts, sid, risk))
    ts = jitter(ts, 1, 5)
    events.append(evt_risk_score_generated(uid, ts, sid, risk))

    # occasional risk profile update
    if _pass(0.10):
        old = risk
        new = random.choice([r for r in ["low", "medium", "high"] if r != old])
        ts = jitter(ts, 10, 60)
        events.append(evt_risk_profile_updated(uid, ts, sid, old, new))
        risk = new
        user["risk_profile"] = new

    # ── Phase 4: KYC ─────────────────────────────────────────────────────────
    ts = jitter(ts, *GAPS["between_sessions"])
    sid = new_session()

    if not _pass(P["kyc_attempt"]):
        return user, events

    events.append(evt_kyc_started(uid, ts, sid))
    ts = jitter(ts, *GAPS["kyc_steps"])
    events.append(evt_kyc_document_uploaded(uid, ts, sid))
    ts = jitter(ts, 10, 60)

    if not _pass(P["kyc_pass"]):
        events.append(evt_kyc_verification_failed(uid, ts, sid))
        # retry logic
        if _pass(P["kyc_retry_pass"]):
            ts = jitter(ts, 3600, 86400)
            sid = new_session()
            events.append(evt_kyc_started(uid, ts, sid))
            ts = jitter(ts, *GAPS["kyc_steps"])
            events.append(evt_kyc_document_uploaded(uid, ts, sid))
            ts = jitter(ts, 10, 60)
            events.append(evt_kyc_completed(uid, ts, sid))
            user["activated_at"] = ts
        else:
            return user, events                         # drop-off: KYC failed twice
    else:
        events.append(evt_kyc_completed(uid, ts, sid))
        user["activated_at"] = ts

    # ── Phase 5: Funding ──────────────────────────────────────────────────────
    ts = jitter(ts, *GAPS["between_sessions"])
    sid = new_session()

    if not _pass(P["bank_link"]):
        return user, events

    events.append(evt_bank_account_linked(uid, ts, sid))
    ts = jitter(ts, *GAPS["deposit_steps"])

    if not _pass(P["deposit_attempt"]):
        return user, events

    deposit_event = evt_deposit_initiated(uid, ts, sid)
    events.append(deposit_event)
    deposit_amount = deposit_event["properties"]["amount"]
    ts = jitter(ts, 10, 120)

    if not _pass(P["deposit_success"]):
        events.append(evt_deposit_failed(uid, ts, sid))
        return user, events

    events.append(evt_deposit_completed(uid, ts, sid, deposit_amount))
    user["first_deposit_at"] = ts
    portfolio_value = deposit_amount

    # ── Phase 6: Portfolio lifecycle ─────────────────────────────────────────
    ts = jitter(ts, *GAPS["portfolio_setup"])
    sid = new_session()

    if not _pass(P["portfolio_create"]):
        return user, events

    events.append(evt_portfolio_created(uid, ts, sid, risk))

    # ── Phase 7+: Ongoing engagement (multiple sessions) ─────────────────────
    n_sessions = random.randint(3, 20)
    for _ in range(n_sessions):
        ts = jitter(ts, *GAPS["between_sessions"])
        sid = new_session()

        # login at start of session
        events.append(evt_login(uid, ts, sid, device))

        # dashboard view (almost always)
        if _pass(0.90):
            ts = jitter(ts, *GAPS["engagement_event"])
            events.append(evt_dashboard_viewed(uid, ts, sid))

        # portfolio view
        if _pass(0.75):
            ts = jitter(ts, *GAPS["engagement_event"])
            events.append(evt_portfolio_viewed(uid, ts, sid))

        # performance chart
        if _pass(0.60):
            ts = jitter(ts, *GAPS["engagement_event"])
            events.append(evt_performance_chart_viewed(uid, ts, sid))

        # investment action
        if _pass(0.35):
            ts = jitter(ts, *GAPS["engagement_event"])
            events.append(evt_investment_added(uid, ts, sid, risk))
            portfolio_value += random.randint(500, 10000)

        if _pass(0.12):
            ts = jitter(ts, *GAPS["engagement_event"])
            events.append(evt_investment_removed(uid, ts, sid, risk))

        # goal creation (once-ish)
        if _pass(P["goal_create"] / n_sessions):
            ts = jitter(ts, *GAPS["engagement_event"])
            events.append(evt_goal_created(uid, ts, sid))
            if _pass(0.30):
                ts = jitter(ts, *GAPS["engagement_event"])
                events.append(evt_goal_updated(uid, ts, sid))

        # auto invest
        if _pass(P["auto_invest_enable"] / n_sessions):
            ts = jitter(ts, *GAPS["engagement_event"])
            events.append(evt_auto_invest_enabled(uid, ts, sid))
            if _pass(0.20):
                ts = jitter(ts, 86400, 86400 * 30)
                events.append(evt_auto_invest_disabled(uid, ts, sid))

        # notification click
        if _pass(0.25):
            ts = jitter(ts, *GAPS["engagement_event"])
            events.append(evt_notification_clicked(uid, ts, sid))

        # feature discovery
        if _pass(0.20):
            ts = jitter(ts, *GAPS["engagement_event"])
            events.append(evt_feature_viewed(uid, ts, sid))

        # feature discovery
        if _pass(0.15):
            ts = jitter(ts, *GAPS["engagement_event"])
            events.append(evt_portfolio_report_downloaded(uid, ts, sid))

        # support chat (friction signal)
        if _pass(0.08):
            ts = jitter(ts, *GAPS["engagement_event"])
            events.append(evt_support_chat_opened(uid, ts, sid))

        # rebalance (periodic)
        if _pass(0.10):
            ts = jitter(ts, *GAPS["engagement_event"])
            events.append(evt_portfolio_rebalanced(uid, ts, sid))

        # allocation change (behavior signal)
        if _pass(0.07):
            ts = jitter(ts, *GAPS["engagement_event"])
            events.append(evt_portfolio_allocation_changed(uid, ts, sid, risk))

        # dividend
        if _pass(0.05):
            ts = jitter(ts, *GAPS["engagement_event"])
            events.append(evt_dividend_received(uid, ts, sid))

        # additional deposit
        if _pass(0.20):
            ts = jitter(ts, *GAPS["engagement_event"])
            d_evt = evt_deposit_initiated(uid, ts, sid)
            events.append(d_evt)
            ts = jitter(ts, 10, 120)
            if _pass(0.88):
                events.append(evt_deposit_completed(uid, ts, sid,
                                                     d_evt["properties"]["amount"]))
                portfolio_value += d_evt["properties"]["amount"]

        # logout
        if _pass(0.70):
            ts = jitter(ts, *GAPS["engagement_event"])
            events.append(evt_logout(uid, ts, sid))

    # ── Phase 10: Retention & Exit ────────────────────────────────────────────
    if _pass(P["becomes_churner"]):
        ts = jitter(ts, *GAPS["between_sessions"])
        sid = new_session()
        events.append(evt_account_inactive(uid, ts, sid))

        if _pass(0.60):
            ts = jitter(ts, 86400, 86400 * 30)
            events.append(evt_withdrawal_all_funds(uid, ts, sid, portfolio_value))

            if _pass(0.70):
                ts = jitter(ts, 86400, 86400 * 7)
                events.append(evt_account_closed(uid, ts, sid))

    elif _pass(P["portfolio_close"]):
        ts = jitter(ts, *GAPS["between_sessions"])
        sid = new_session()
        events.append(evt_portfolio_closed(uid, ts, sid))

    return user, events


def _pass(probability: float) -> bool:
    return random.random() < probability
