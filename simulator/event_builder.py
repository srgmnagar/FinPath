import random
import uuid
from datetime import datetime, timedelta
 
SIM_END = datetime(2024, 12, 31, 23, 59, 59)
 
def cap(ts: datetime) -> datetime:
    """Ensure no event goes beyond simulation end date."""
    return min(ts, SIM_END)
 
def new_session() -> str:
    return str(uuid.uuid4())
 
def jitter(base: datetime, min_sec: int, max_sec: int) -> datetime:
    return base + timedelta(seconds=random.randint(min_sec, max_sec))
 
def build_event(user_id, event_type, ts, session_id, props):
    return {
        "user_id":    user_id,
        "event_type": event_type,
        "timestamp":  ts,
        "session_id": session_id,
        "properties": props,
    }
 
# ── Acquisition ───────────────────────────────────────────────────────────────
 
def evt_app_opened(uid, ts, sid, device):
    return build_event(uid, "app_opened", ts, sid,
                       {"device": device, "source": random.choice(
                           ["organic", "google_ad", "referral", "social"])})
 
def evt_landing_page_viewed(uid, ts, sid):
    return build_event(uid, "landing_page_viewed", ts, sid,
                       {"page": "home", "utm_source": random.choice(
                           ["google", "facebook", "direct", "referral"])})
 
def evt_signup_started(uid, ts, sid):
    return build_event(uid, "signup_started", ts, sid, {})
 
def evt_signup_completed(uid, ts, sid):
    return build_event(uid, "signup_completed", ts, sid,
                       {"method": random.choice(["email", "google", "phone"])})
 
def evt_email_verified(uid, ts, sid):
    return build_event(uid, "email_verified", ts, sid,
                       {"time_to_verify_min": random.randint(1, 30)})
 
def evt_login(uid, ts, sid, device):
    return build_event(uid, "login", ts, sid,
                       {"device": device, "method": random.choice(
                           ["email", "google", "biometric"])})
 
def evt_logout(uid, ts, sid):
    return build_event(uid, "logout", ts, sid,
                       {"session_duration_min": random.randint(2, 60)})
 
 
# ── Onboarding ────────────────────────────────────────────────────────────────
 
def evt_onboarding_started(uid, ts, sid):
    return build_event(uid, "onboarding_started", ts, sid, {})
 
def evt_profile_completed(uid, ts, sid):
    return build_event(uid, "profile_completed", ts, sid,
                       {"age_group": random.choice(["18-25", "26-35", "36-45", "46-60"]),
                        "income_bracket": random.choice(["<5L", "5-10L", "10-25L", "25L+"])})
 
def evt_investment_goal_selected(uid, ts, sid):
    return build_event(uid, "investment_goal_selected", ts, sid,
                       {"goal": random.choice(["retirement", "wealth_creation",
                                               "child_education", "home_purchase",
                                               "emergency_fund"]),
                        "horizon_years": random.randint(1, 30)})
 
def evt_onboarding_completed(uid, ts, sid):
    return build_event(uid, "onboarding_completed", ts, sid, {})
 
 
# ── Risk profiling ────────────────────────────────────────────────────────────
 
RISK_QUESTIONS = [
    "investment_experience", "loss_tolerance", "income_stability",
    "investment_horizon", "reaction_to_drop", "existing_investments",
    "monthly_savings_pct", "financial_dependents"
]
 
def evt_risk_quiz_started(uid, ts, sid):
    return build_event(uid, "risk_quiz_started", ts, sid, {})
 
def evt_risk_question_answered(uid, ts, sid, q_index):
    return build_event(uid, "risk_question_answered", ts, sid,
                       {"question_id": RISK_QUESTIONS[q_index],
                        "question_index": q_index + 1,
                        "answer_value": random.randint(1, 5),
                        "time_taken_sec": random.randint(4, 45)})
 
def evt_risk_quiz_completed(uid, ts, sid, risk_profile):
    score = {"low": random.randint(8, 18),
             "medium": random.randint(19, 30),
             "high": random.randint(31, 40)}[risk_profile]
    return build_event(uid, "risk_quiz_completed", ts, sid,
                       {"risk_score": score, "risk_label": risk_profile,
                        "total_time_sec": random.randint(60, 600)})
 
def evt_risk_score_generated(uid, ts, sid, risk_profile):
    return build_event(uid, "risk_score_generated", ts, sid,
                       {"risk_label": risk_profile,
                        "recommended_equity_pct": {
                            "low": 30, "medium": 60, "high": 85}[risk_profile]})
 
def evt_risk_profile_updated(uid, ts, sid, old_profile, new_profile):
    return build_event(uid, "risk_profile_updated", ts, sid,
                       {"old_profile": old_profile, "new_profile": new_profile})
 
 
# ── KYC ──────────────────────────────────────────────────────────────────────
 
def evt_kyc_started(uid, ts, sid):
    return build_event(uid, "kyc_started", ts, sid, {})
 
def evt_kyc_document_uploaded(uid, ts, sid):
    return build_event(uid, "kyc_document_uploaded", ts, sid,
                       {"doc_type": random.choice(
                           ["aadhaar", "pan", "passport", "voter_id"]),
                        "upload_method": random.choice(
                            ["camera", "gallery", "digilocker"])})
 
def evt_kyc_verification_failed(uid, ts, sid):
    return build_event(uid, "kyc_verification_failed", ts, sid,
                       {"reason": random.choice(
                           ["blurry_image", "name_mismatch", "expired_doc",
                            "address_mismatch", "ocr_failure"])})
 
def evt_kyc_completed(uid, ts, sid):
    return build_event(uid, "kyc_completed", ts, sid,
                       {"kyc_provider": random.choice(
                           ["digio", "karza", "hyperverge"]),
                        "verification_time_sec": random.randint(10, 120)})
 
 
# ── Funding ───────────────────────────────────────────────────────────────────
 
def evt_bank_account_linked(uid, ts, sid):
    return build_event(uid, "bank_account_linked", ts, sid,
                       {"bank": random.choice(
                           ["HDFC", "SBI", "ICICI", "Axis", "Kotak", "YES"]),
                        "method": random.choice(
                            ["netbanking", "upi", "penny_drop"])})
 
def evt_deposit_initiated(uid, ts, sid):
    amount = random.choice([500, 1000, 2000, 5000, 10000, 25000, 50000, 100000])
    return build_event(uid, "deposit_initiated", ts, sid,
                       {"amount": amount, "currency": "INR",
                        "method": random.choice(
                            ["upi", "netbanking", "neft", "imps"])})
 
def evt_deposit_completed(uid, ts, sid, amount):
    return build_event(uid, "deposit_completed", ts, sid,
                       {"amount": amount, "currency": "INR",
                        "transaction_id": str(uuid.uuid4())[:12].upper()})
 
def evt_deposit_failed(uid, ts, sid):
    return build_event(uid, "deposit_failed", ts, sid,
                       {"reason": random.choice(
                           ["insufficient_funds", "bank_timeout",
                            "upi_limit_exceeded", "network_error"])})
 
def evt_withdrawal_initiated(uid, ts, sid, portfolio_value):
    amount = round(portfolio_value * random.uniform(0.1, 1.0))
    return build_event(uid, "withdrawal_initiated", ts, sid,
                       {"amount": amount, "currency": "INR"})
 
def evt_withdrawal_completed(uid, ts, sid, amount):
    return build_event(uid, "withdrawal_completed", ts, sid,
                       {"amount": amount, "currency": "INR",
                        "settlement_days": random.choice([1, 2, 3])})
 
 
# ── Portfolio ─────────────────────────────────────────────────────────────────
 
FUND_MAP = {
    "low":    ["liquid_fund", "debt_fund", "short_term_bond"],
    "medium": ["balanced_fund", "index_fund", "large_cap"],
    "high":   ["mid_cap", "small_cap", "sectoral", "international"],
}
 
def evt_portfolio_created(uid, ts, sid, risk_profile):
    funds = random.sample(FUND_MAP[risk_profile], k=random.randint(2, 3))
    return build_event(uid, "portfolio_created", ts, sid,
                       {"risk_profile": risk_profile, "funds": funds,
                        "initial_allocation": {
                            f: round(100/len(funds), 1) for f in funds}})
 
def evt_portfolio_viewed(uid, ts, sid):
    return build_event(uid, "portfolio_viewed", ts, sid,
                       {"time_spent_sec": random.randint(10, 300)})
 
def evt_portfolio_rebalanced(uid, ts, sid):
    return build_event(uid, "portfolio_rebalanced", ts, sid,
                       {"trigger": random.choice(
                           ["scheduled", "drift_threshold", "manual"]),
                        "drift_pct": round(random.uniform(1.0, 15.0), 2)})
 
def evt_portfolio_allocation_changed(uid, ts, sid, risk_profile):
    return build_event(uid, "portfolio_allocation_changed", ts, sid,
                       {"from_profile": risk_profile,
                        "direction": random.choice(
                            ["more_aggressive", "more_conservative"]),
                        "trigger": random.choice(
                            ["market_event", "user_initiated", "goal_change"])})
 
def evt_portfolio_closed(uid, ts, sid):
    return build_event(uid, "portfolio_closed", ts, sid,
                       {"reason": random.choice(
                           ["user_requested", "inactivity",
                            "compliance", "full_withdrawal"])})
 
 
# ── Investment actions ────────────────────────────────────────────────────────
 
def evt_investment_added(uid, ts, sid, risk_profile):
    fund   = random.choice(FUND_MAP[risk_profile])
    amount = random.choice([500, 1000, 2500, 5000, 10000])
    return build_event(uid, "investment_added", ts, sid,
                       {"fund": fund, "amount": amount,
                        "type": random.choice(["lump_sum", "sip"])})
 
def evt_investment_removed(uid, ts, sid, risk_profile):
    fund = random.choice(FUND_MAP[risk_profile])
    return build_event(uid, "investment_removed", ts, sid,
                       {"fund": fund, "reason": random.choice(
                           ["rebalance", "profit_booking",
                            "panic_sell", "goal_achieved"])})
 
def evt_auto_invest_enabled(uid, ts, sid):
    return build_event(uid, "auto_invest_enabled", ts, sid,
                       {"frequency": random.choice(["monthly", "weekly"]),
                        "amount": random.choice([1000, 2000, 5000, 10000])})
 
def evt_auto_invest_disabled(uid, ts, sid):
    return build_event(uid, "auto_invest_disabled", ts, sid,
                       {"reason": random.choice(
                           ["cash_flow", "market_uncertainty",
                            "goal_change", "not_specified"])})
 
def evt_dividend_received(uid, ts, sid):
    return build_event(uid, "dividend_received", ts, sid,
                       {"amount": round(random.uniform(50, 5000), 2),
                        "fund": "index_fund",
                        "reinvested": random.choice([True, False])})
 
 
# ── Feature usage ─────────────────────────────────────────────────────────────
 
def evt_goal_created(uid, ts, sid):
    return build_event(uid, "goal_created", ts, sid,
                       {"goal_type": random.choice(
                           ["sip", "target_amount", "retirement"]),
                        "target_amount": random.choice(
                            [100000, 500000, 1000000, 5000000]),
                        "target_years": random.randint(1, 20)})
 
def evt_goal_updated(uid, ts, sid):
    return build_event(uid, "goal_updated", ts, sid,
                       {"field_changed": random.choice(
                           ["target_amount", "horizon", "sip_amount"])})
 
def evt_notification_clicked(uid, ts, sid):
    return build_event(uid, "notification_clicked", ts, sid,
                       {"type": random.choice(
                           ["market_alert", "sip_reminder",
                            "portfolio_update", "kyc_reminder"])})
 
def evt_feature_viewed(uid, ts, sid):
    return build_event(uid, "feature_viewed", ts, sid,
                       {"feature": random.choice(
                           ["tax_harvesting", "sip_calculator",
                            "compare_funds", "returns_estimator"])})
 
 
# ── Engagement ────────────────────────────────────────────────────────────────
 
def evt_dashboard_viewed(uid, ts, sid):
    return build_event(uid, "dashboard_viewed", ts, sid,
                       {"sections_viewed": random.randint(1, 6),
                        "time_spent_sec": random.randint(15, 240)})
 
def evt_performance_chart_viewed(uid, ts, sid):
    return build_event(uid, "performance_chart_viewed", ts, sid,
                       {"period": random.choice(
                           ["1W", "1M", "3M", "6M", "1Y", "ALL"]),
                        "market_sentiment": random.choice(
                            ["bull", "bear", "neutral"])})
 
def evt_portfolio_report_downloaded(uid, ts, sid):
    return build_event(uid, "portfolio_report_downloaded", ts, sid,
                       {"report_type": random.choice(
                           ["monthly", "quarterly", "annual", "tax"])})
 
def evt_support_chat_opened(uid, ts, sid):
    return build_event(uid, "support_chat_opened", ts, sid,
                       {"trigger": random.choice(
                           ["kyc_issue", "deposit_failed", "returns_query",
                            "withdrawal_help", "general"])})
 
 
# ── Retention & Exit ──────────────────────────────────────────────────────────
 
def evt_account_inactive(uid, ts, sid):
    return build_event(uid, "account_inactive", ts, sid,
                       {"days_inactive": random.randint(30, 180)})
 
def evt_withdrawal_all_funds(uid, ts, sid, portfolio_value):
    return build_event(uid, "withdrawal_all_funds", ts, sid,
                       {"total_amount": portfolio_value,
                        "reason": random.choice(
                            ["emergency", "dissatisfied",
                             "switching_platform", "not_specified"])})
 
def evt_account_closed(uid, ts, sid):
    return build_event(uid, "account_closed", ts, sid,
                       {"reason": random.choice(
                           ["user_requested", "compliance",
                            "inactivity_30d", "fraud_suspected"])})