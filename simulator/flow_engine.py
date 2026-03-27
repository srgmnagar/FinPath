import random
from datetime import datetime
from event_builder import *

# ── Drop-off probabilities ────────────────────────────────────────────────────
P = {
    "signup_complete":      0.70,
    "email_verify":         0.85,
    "onboarding_complete":  0.90,
    "risk_quiz_complete":   0.60,
    "kyc_attempt":          0.95,
    "kyc_pass":             0.85,
    "kyc_retry_pass":       0.60,
    "bank_link":            0.87,
    "deposit_attempt":      0.85,
    "deposit_success":      0.88,
    "portfolio_create":     0.95,
}

GAPS = {
    "app_to_signup":            (5,      120),
    "signup_steps":             (30,     300),
    "email_verify":             (3600,   86400 * 3),
    "onboarding_steps":         (300,    3600),
    "quiz_per_question":        (10,     60),
    "kyc_steps":                (3600,   86400 * 2),
    "bank_link":                (1800,   86400),
    "deposit_steps":            (3600,   86400 * 3),
    "portfolio_setup":          (60,     600),
    "between_sessions_early":   (86400 * 4,  86400 * 10),  # 4–10 days (was 1–3)
"between_sessions_late":    (86400 * 10, 86400 * 45),   # 10–45 days (was 5–30)
    "engagement_event":         (60,     3600),
    "churn_inactivity":         (86400 * 30, 86400 * 90),
    "churn_to_withdrawal":      (86400,  86400 * 14),
    "withdrawal_to_close":      (86400,  86400 * 7),
}

RISK_CONFIG = {
    "low": {
        "deposit_amounts":      [500, 1000, 2000, 5000],
        "deposit_weights":      [0.40, 0.35, 0.20, 0.05],
        "invest_frequency":     0.20,
        "sell_frequency":       0.08,
        "auto_invest_prob":     0.25,
        "goal_prob":            0.45,
        "chart_to_sell_prob":   0.20,
        "n_sessions_weights": [20, 15, 12, 10, 8, 6, 4, 3, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    },
    "medium": {
        "deposit_amounts":      [2000, 5000, 10000, 25000],
        "deposit_weights":      [0.30, 0.40, 0.20,  0.10],
        "invest_frequency":     0.35,
        "sell_frequency":       0.05,
        "auto_invest_prob":     0.40,
        "goal_prob":            0.55,
        "chart_to_sell_prob":   0.10,
        "n_sessions_weights": [15, 13, 11, 9, 8, 6, 5, 4, 3, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1],
    },
    "high": {
        "deposit_amounts":      [10000, 25000, 50000, 100000],
        "deposit_weights":      [0.25,  0.35,  0.25,   0.15],
        "invest_frequency":     0.55,
        "sell_frequency":       0.03,
        "auto_invest_prob":     0.60,
        "goal_prob":            0.65,
        "chart_to_sell_prob":   0.04,
        "n_sessions_weights": [12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 3, 2, 2, 2, 1, 1, 1, 1, 1, 1],
    },
}


def simulate_user(user: dict) -> tuple[dict, list[dict]]:
    uid    = user["user_id"]
    risk   = user["risk_profile"]
    device = user["device_type"]
    ts     = user["signup_at"]
    cfg    = RISK_CONFIG[risk]
    events = []
    sid    = new_session()

    # Phase 1: Acquisition
    events.append(evt_app_opened(uid, ts, sid, device))
    ts = jitter(ts, *GAPS["app_to_signup"])
    events.append(evt_landing_page_viewed(uid, ts, sid))
    ts = jitter(ts, 5, 60)
    events.append(evt_signup_started(uid, ts, sid))

    if not _pass(P["signup_complete"]):
        return user, events

    ts = jitter(ts, *GAPS["signup_steps"])
    events.append(evt_signup_completed(uid, ts, sid))

    if not _pass(P["email_verify"]):
        return user, events

    ts = jitter(ts, *GAPS["email_verify"])
    events.append(evt_email_verified(uid, ts, sid))

    # Phase 2: Onboarding
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

    # Phase 3: Risk profiling
    ts = jitter(ts, *GAPS["between_sessions_early"])
    sid = new_session()
    events.append(evt_risk_quiz_started(uid, ts, sid))

    n_questions = len(RISK_QUESTIONS)
    completed_q = 0
    for i in range(n_questions):
        ts = jitter(ts, *GAPS["quiz_per_question"])
        events.append(evt_risk_question_answered(uid, ts, sid, i))
        completed_q += 1
        if i < 3 and not _pass(0.92):
            break
        elif i >= 3 and not _pass(0.97):
            break

    if completed_q < n_questions or not _pass(P["risk_quiz_complete"]):
        return user, events

    ts = jitter(ts, 5, 30)
    events.append(evt_risk_quiz_completed(uid, ts, sid, risk))
    ts = jitter(ts, 1, 5)
    events.append(evt_risk_score_generated(uid, ts, sid, risk))

    if _pass(0.10):
        old  = risk
        new  = random.choice([r for r in ["low", "medium", "high"] if r != old])
        ts   = jitter(ts, 10, 60)
        events.append(evt_risk_profile_updated(uid, ts, sid, old, new))
        risk = new
        user["risk_profile"] = new
        cfg  = RISK_CONFIG[risk]

    # Phase 4: KYC
    ts  = jitter(ts, *GAPS["between_sessions_early"])
    sid = new_session()

    if not _pass(P["kyc_attempt"]):
        return user, events

    events.append(evt_kyc_started(uid, ts, sid))
    ts = jitter(ts, *GAPS["kyc_steps"])
    events.append(evt_kyc_document_uploaded(uid, ts, sid))
    ts = jitter(ts, 10, 60)

    if not _pass(P["kyc_pass"]):
        events.append(evt_kyc_verification_failed(uid, ts, sid))
        if _pass(P["kyc_retry_pass"]):
            ts  = jitter(ts, 3600, 86400)
            sid = new_session()
            events.append(evt_kyc_started(uid, ts, sid))
            ts  = jitter(ts, *GAPS["kyc_steps"])
            events.append(evt_kyc_document_uploaded(uid, ts, sid))
            ts  = jitter(ts, 10, 60)
            events.append(evt_kyc_completed(uid, ts, sid))
            user["activated_at"] = ts
        else:
            return user, events
    else:
        events.append(evt_kyc_completed(uid, ts, sid))
        user["activated_at"] = ts

    # Phase 5: Funding
    ts  = jitter(ts, *GAPS["between_sessions_early"])
    sid = new_session()

    if not _pass(P["bank_link"]):
        return user, events

    events.append(evt_bank_account_linked(uid, ts, sid))
    ts = jitter(ts, *GAPS["deposit_steps"])

    if not _pass(P["deposit_attempt"]):
        return user, events

    deposit_amount      = random.choices(cfg["deposit_amounts"], cfg["deposit_weights"])[0]
    deposit_evt         = evt_deposit_initiated(uid, ts, sid)
    deposit_evt["properties"]["amount"] = deposit_amount
    events.append(deposit_evt)
    ts = jitter(ts, 10, 120)

    if not _pass(P["deposit_success"]):
        events.append(evt_deposit_failed(uid, ts, sid))
        return user, events

    events.append(evt_deposit_completed(uid, ts, sid, deposit_amount))
    user["first_deposit_at"] = ts
    portfolio_value = deposit_amount

    # Phase 6: Portfolio
    ts  = jitter(ts, *GAPS["portfolio_setup"])
    sid = new_session()

    if not _pass(P["portfolio_create"]):
        return user, events

    events.append(evt_portfolio_created(uid, ts, sid, risk))

    # Feature adoption decisions made upfront
    user_creates_goal       = _pass(cfg["goal_prob"])
    user_enables_autoinvest = _pass(cfg["auto_invest_prob"])
    goal_created            = False
    autoinvest_created      = False

    # Phase 7+: Engagement sessions with decay
    n_sessions = random.choices(range(1, 21), weights=cfg["n_sessions_weights"])[0]

    for i in range(n_sessions):
        if i < 3:
            ts = jitter(ts, *GAPS["between_sessions_early"])
        else:
            ts = jitter(ts, *GAPS["between_sessions_late"])

        sid = new_session()
        events.append(evt_login(uid, ts, sid, device))

        if _pass(0.90):
            ts = jitter(ts, *GAPS["engagement_event"])
            events.append(evt_dashboard_viewed(uid, ts, sid))

        if _pass(0.75):
            ts = jitter(ts, *GAPS["engagement_event"])
            events.append(evt_portfolio_viewed(uid, ts, sid))

        if _pass(0.60):
            ts = jitter(ts, *GAPS["engagement_event"])
            events.append(evt_performance_chart_viewed(uid, ts, sid))
            # chart view -> panic sell (risk profile driven)
            if _pass(cfg["chart_to_sell_prob"]):
                ts = jitter(ts, 60, 600)
                events.append(evt_investment_removed(uid, ts, sid, risk))
                portfolio_value = max(0, portfolio_value - random.randint(500, 5000))

        if _pass(cfg["invest_frequency"]):
            ts = jitter(ts, *GAPS["engagement_event"])
            events.append(evt_investment_added(uid, ts, sid, risk))
            portfolio_value += random.randint(500, deposit_amount)

        if _pass(cfg["sell_frequency"]):
            ts = jitter(ts, *GAPS["engagement_event"])
            events.append(evt_investment_removed(uid, ts, sid, risk))

        # goal — early sessions only
        if user_creates_goal and not goal_created and i < 3:
            ts = jitter(ts, *GAPS["engagement_event"])
            events.append(evt_goal_created(uid, ts, sid))
            goal_created = True
            if _pass(0.30):
                ts = jitter(ts, *GAPS["engagement_event"])
                events.append(evt_goal_updated(uid, ts, sid))

        # auto invest — early sessions only
        if user_enables_autoinvest and not autoinvest_created and i < 2:
            ts = jitter(ts, *GAPS["engagement_event"])
            events.append(evt_auto_invest_enabled(uid, ts, sid))
            autoinvest_created = True
            if _pass(0.20):
                ts = jitter(ts, 86400, 86400 * 30)
                events.append(evt_auto_invest_disabled(uid, ts, sid))

        if _pass(0.25):
            ts = jitter(ts, *GAPS["engagement_event"])
            events.append(evt_notification_clicked(uid, ts, sid))

        if _pass(0.20):
            ts = jitter(ts, *GAPS["engagement_event"])
            events.append(evt_feature_viewed(uid, ts, sid))

        if _pass(0.15):
            ts = jitter(ts, *GAPS["engagement_event"])
            events.append(evt_portfolio_report_downloaded(uid, ts, sid))

        if _pass(0.08):
            ts = jitter(ts, *GAPS["engagement_event"])
            events.append(evt_support_chat_opened(uid, ts, sid))

        if _pass(0.10):
            ts = jitter(ts, *GAPS["engagement_event"])
            events.append(evt_portfolio_rebalanced(uid, ts, sid))

        if _pass(0.07):
            ts = jitter(ts, *GAPS["engagement_event"])
            events.append(evt_portfolio_allocation_changed(uid, ts, sid, risk))

        if _pass(0.05):
            ts = jitter(ts, *GAPS["engagement_event"])
            events.append(evt_dividend_received(uid, ts, sid))

        if _pass(0.20):
            ts = jitter(ts, *GAPS["engagement_event"])
            add_amount = random.choices(cfg["deposit_amounts"], cfg["deposit_weights"])[0]
            d_evt      = evt_deposit_initiated(uid, ts, sid)
            d_evt["properties"]["amount"] = add_amount
            events.append(d_evt)
            ts = jitter(ts, 10, 120)
            if _pass(0.88):
                events.append(evt_deposit_completed(uid, ts, sid, add_amount))
                portfolio_value += add_amount

        if _pass(0.70):
            ts = jitter(ts, *GAPS["engagement_event"])
            events.append(evt_logout(uid, ts, sid))

    # Phase 10: Churn — risk profile drives churn probability
    churn_prob = {"low": 0.15, "medium": 0.08, "high": 0.04}[risk]

    if _pass(churn_prob):
        ts  = jitter(ts, *GAPS["churn_inactivity"])
        sid = new_session()
        events.append(evt_account_inactive(uid, ts, sid))

        if _pass(0.65):
            ts = jitter(ts, *GAPS["churn_to_withdrawal"])
            events.append(evt_withdrawal_all_funds(uid, ts, sid, portfolio_value))
            portfolio_value = 0

            if _pass(0.70):
                ts = jitter(ts, *GAPS["withdrawal_to_close"])
                events.append(evt_account_closed(uid, ts, sid))

    elif _pass(0.04):
        ts  = jitter(ts, *GAPS["between_sessions_late"])
        sid = new_session()
        events.append(evt_portfolio_closed(uid, ts, sid))

        if _pass(0.50):
            ts       = jitter(ts, *GAPS["churn_to_withdrawal"])
            w_amount = int(portfolio_value * random.uniform(0.3, 0.8))
            events.append(evt_withdrawal_initiated(uid, ts, sid, portfolio_value))
            ts = jitter(ts, 86400, 86400 * 3)
            events.append(evt_withdrawal_completed(uid, ts, sid, w_amount))

    return user, events


def _pass(probability: float) -> bool:
    return random.random() < probability