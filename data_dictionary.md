# Data Dictionary

| File | Grain | Important Fields |
| --- | --- | --- |
| `job_orders.csv` | One row per open role | `role_id`, `client_segment`, `role_family`, `work_structure`, `priority`, `open_days`, `pay_rate`, `bill_rate`, `skills_required`, `hiring_manager_response_rate`, `recruiter_owner` |
| `weekly_funnel_metrics.csv` | One role per week | `applicants`, `qualified`, `screened`, `submitted`, `client_interviews`, `offers`, `placements`, `candidate_dropoffs`, `recruiter_touches` |
| `candidate_pipeline_events.csv` | One synthetic candidate-stage event | `candidate_id`, `source`, `stage`, `profile_complete_pct`, `duplicate_candidate_flag`, `missing_rate_flag`, `location_mismatch_flag`, `skill_taxonomy_gap_flag`, `estimated_margin_value` |
| `data_quality_checks.csv` | One quality check per role | `check_id`, `check_name`, `records_tested`, `issue_count`, `severity`, `owner` |
| `market_skill_signals.csv` | One row per skill | `skill`, `open_role_count`, `demand_index`, `available_supply_index`, `median_pay_rate`, `market_pressure` |
| `recommended_actions.csv` | One generated action | `action_id`, `role_id`, `action_type`, `owner`, `effort_hours`, `expected_shortlist_days`, `expected_margin_protected`, `status` |
| `analysis/outputs/role_priority_queue.csv` | One scored role | `priority_score`, `placement_readiness_score`, `fill_risk_score`, `data_quality_score`, `expected_shortlist_days`, `recommendation` |

## Score Definitions

- `placement_readiness_score`: weighted conversion, source-quality, and hiring-manager response signal. Higher is better.
- `fill_risk_score`: weighted aging, scarcity, weak conversion, and data-quality risk. Higher means the role needs attention.
- `priority_score`: composite operating score used to rank the weekly decision queue.
- `expected_shortlist_days`: estimated time to produce a credible shortlist based on role age, submit rate, and quality score.
