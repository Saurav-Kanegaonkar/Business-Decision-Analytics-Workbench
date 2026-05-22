import csv
import json
import math
import random
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "analysis" / "outputs"
SRC = ROOT / "src"

random.seed(42)


CLIENT_SEGMENTS = [
    "Regional bank",
    "Healthcare network",
    "Industrial manufacturer",
    "Insurance carrier",
    "B2B software firm",
    "Energy utility",
    "Hospitality group",
    "Professional services firm",
]

ROLE_FAMILIES = [
    ("Data Analyst", ["SQL", "Excel", "Power BI", "Python"]),
    ("BI Analyst", ["SQL", "Power BI", "Tableau", "Data modeling"]),
    ("Finance Analyst", ["Excel", "SQL", "Forecasting", "Power BI"]),
    ("ERP Analyst", ["SQL", "Process mapping", "Data validation", "Excel"]),
    ("Cybersecurity Analyst", ["SQL", "Risk reporting", "Python", "Excel"]),
    ("Data Engineer", ["SQL", "Python", "Cloud data", "ETL"]),
]

STAGES = ["applied", "qualified", "screened", "submitted", "interview", "offer", "placed"]
SOURCES = ["Referral", "LinkedIn", "Job board", "Talent pool", "Recruiter outreach", "Community event"]
CHECKS = [
    ("missing_pay_rate", "Missing pay or bill rate"),
    ("stale_status", "Open status not refreshed"),
    ("duplicate_candidate", "Duplicate candidate identifier"),
    ("location_mismatch", "Location or work structure mismatch"),
    ("skill_taxonomy_gap", "Skill taxonomy not standardized"),
    ("stage_backfill", "Late stage history backfill"),
]


def pct(value):
    return round(value * 100, 1)


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def clamp(value, low, high):
    return max(low, min(high, value))


def zscores(items, key):
    values = [row[key] for row in items]
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    std = math.sqrt(variance) or 1
    return {row["role_id"]: (row[key] - mean) / std for row in items}


def generate_job_orders():
    cities = ["Cincinnati", "Columbus", "Dayton", "Cleveland", "Indianapolis", "Louisville"]
    work_structures = ["Onsite", "Hybrid", "Remote"]
    priorities = ["Critical", "High", "Standard"]
    job_orders = []
    for idx in range(1, 43):
        family, skills = ROLE_FAMILIES[(idx + random.randint(0, 4)) % len(ROLE_FAMILIES)]
        priority = random.choices(priorities, weights=[0.28, 0.44, 0.28])[0]
        open_days = random.randint(8, 73) + (12 if priority == "Critical" else 0)
        work_structure = random.choices(work_structures, weights=[0.43, 0.39, 0.18])[0]
        pay_rate = random.randint(34, 82)
        bill_rate = round(pay_rate * random.uniform(1.38, 1.62), 0)
        required_skills = skills[:]
        if random.random() < 0.42:
            required_skills.append(random.choice(["Machine learning", "Cloud basics", "Stakeholder reporting"]))
        job_orders.append(
            {
                "role_id": f"REQ{idx:03d}",
                "client_segment": CLIENT_SEGMENTS[idx % len(CLIENT_SEGMENTS)],
                "role_family": family,
                "city": cities[idx % len(cities)],
                "work_structure": work_structure,
                "priority": priority,
                "open_days": open_days,
                "target_submit_days": random.choice([2, 3, 4, 5]),
                "target_fill_days": random.choice([28, 35, 42, 49]),
                "pay_rate": pay_rate,
                "bill_rate": bill_rate,
                "skills_required": "; ".join(required_skills),
                "hiring_manager_response_rate": round(random.uniform(0.42, 0.91), 2),
                "recruiter_owner": random.choice(["North desk", "Central desk", "Enterprise desk", "Specialty desk"]),
            }
        )
    return job_orders


def generate_weekly_metrics(job_orders):
    start = date(2026, 3, 23)
    rows = []
    for role in job_orders:
        family_multiplier = {
            "Data Analyst": 1.0,
            "BI Analyst": 0.93,
            "Finance Analyst": 1.08,
            "ERP Analyst": 0.74,
            "Cybersecurity Analyst": 0.68,
            "Data Engineer": 0.62,
        }[role["role_family"]]
        onsite_penalty = 0.78 if role["work_structure"] == "Onsite" else 1.0
        critical_boost = 1.18 if role["priority"] == "Critical" else 1.0
        base_applicants = random.randint(16, 42) * family_multiplier * onsite_penalty * critical_boost
        for week in range(8):
            week_start = start + timedelta(days=7 * week)
            demand_noise = random.uniform(0.82, 1.22)
            applicants = max(5, round(base_applicants * demand_noise))
            qualified_rate = clamp(random.uniform(0.32, 0.61) * family_multiplier, 0.18, 0.72)
            screened_rate = random.uniform(0.55, 0.82)
            submit_rate = random.uniform(0.28, 0.58) * (role["hiring_manager_response_rate"] + 0.35)
            interview_rate = random.uniform(0.18, 0.45) * (role["hiring_manager_response_rate"] + 0.25)
            offer_rate = random.uniform(0.08, 0.28)
            qualified = round(applicants * qualified_rate)
            screened = round(qualified * screened_rate)
            submitted = round(screened * submit_rate)
            interviews = round(submitted * interview_rate)
            offers = round(interviews * offer_rate)
            placements = 1 if random.random() < offers * 0.34 else 0
            dropoffs = max(0, qualified - screened) + random.randint(0, 5)
            rows.append(
                {
                    "week_start": week_start.isoformat(),
                    "role_id": role["role_id"],
                    "applicants": applicants,
                    "qualified": qualified,
                    "screened": screened,
                    "submitted": submitted,
                    "client_interviews": interviews,
                    "offers": offers,
                    "placements": placements,
                    "candidate_dropoffs": dropoffs,
                    "recruiter_touches": random.randint(8, 36),
                }
            )
    return rows


def generate_pipeline_events(job_orders):
    rows = []
    candidate_counter = 1
    for role in job_orders:
        event_count = random.randint(24, 54)
        for _ in range(event_count):
            stage = random.choices(STAGES, weights=[30, 24, 18, 13, 8, 4, 3])[0]
            source = random.choices(SOURCES, weights=[12, 27, 24, 17, 15, 5])[0]
            duplicate_flag = random.random() < 0.055
            missing_rate_flag = random.random() < (0.13 if role["priority"] == "Critical" else 0.07)
            location_flag = random.random() < (0.11 if role["work_structure"] == "Onsite" else 0.04)
            skill_gap_flag = random.random() < 0.10
            age_days = random.randint(0, min(80, int(role["open_days"]) + 12))
            rows.append(
                {
                    "event_id": f"EVT{len(rows) + 1:05d}",
                    "role_id": role["role_id"],
                    "candidate_id": f"CAND{candidate_counter:05d}",
                    "source": source,
                    "stage": stage,
                    "event_age_days": age_days,
                    "profile_complete_pct": round(random.uniform(0.58, 1.0), 2),
                    "duplicate_candidate_flag": int(duplicate_flag),
                    "missing_rate_flag": int(missing_rate_flag),
                    "location_mismatch_flag": int(location_flag),
                    "skill_taxonomy_gap_flag": int(skill_gap_flag),
                    "estimated_margin_value": round(float(role["bill_rate"]) - float(role["pay_rate"])) * random.randint(120, 520),
                }
            )
            candidate_counter += 1
    return rows


def generate_quality_checks(job_orders, events):
    event_index = defaultdict(list)
    for row in events:
        event_index[row["role_id"]].append(row)

    rows = []
    for role in job_orders:
        role_events = event_index[role["role_id"]]
        for check_id, label in CHECKS:
            if check_id == "duplicate_candidate":
                issue_count = sum(int(row["duplicate_candidate_flag"]) for row in role_events)
            elif check_id == "missing_pay_rate":
                issue_count = sum(int(row["missing_rate_flag"]) for row in role_events)
            elif check_id == "location_mismatch":
                issue_count = sum(int(row["location_mismatch_flag"]) for row in role_events)
            elif check_id == "skill_taxonomy_gap":
                issue_count = sum(int(row["skill_taxonomy_gap_flag"]) for row in role_events)
            elif check_id == "stale_status":
                issue_count = 1 if int(role["open_days"]) > int(role["target_fill_days"]) and random.random() < 0.75 else 0
            else:
                issue_count = random.randint(0, 4)

            severity = "Pass"
            if issue_count >= 5:
                severity = "Fail"
            elif issue_count >= 2:
                severity = "Watch"

            rows.append(
                {
                    "check_id": check_id,
                    "role_id": role["role_id"],
                    "check_name": label,
                    "records_tested": len(role_events),
                    "issue_count": issue_count,
                    "severity": severity,
                    "owner": role["recruiter_owner"],
                }
            )
    return rows


def generate_market_signals(job_orders):
    rows = []
    skill_pool = sorted({skill for _, skills in ROLE_FAMILIES for skill in skills} | {"Machine learning", "Cloud basics", "Stakeholder reporting"})
    for skill in skill_pool:
        related_roles = [role for role in job_orders if skill in role["skills_required"]]
        demand_index = len(related_roles) * random.uniform(7.5, 12.8)
        supply_index = random.uniform(36, 91)
        median_pay = sum(float(role["pay_rate"]) for role in related_roles) / len(related_roles) if related_roles else random.uniform(38, 78)
        rows.append(
            {
                "skill": skill,
                "open_role_count": len(related_roles),
                "demand_index": round(demand_index, 1),
                "available_supply_index": round(supply_index, 1),
                "median_pay_rate": round(median_pay, 0),
                "market_pressure": "High" if demand_index > supply_index else "Moderate",
            }
        )
    return rows


def score_roles(job_orders, weekly, quality_checks):
    weekly_index = defaultdict(list)
    quality_index = defaultdict(list)
    for row in weekly:
        weekly_index[row["role_id"]].append(row)
    for row in quality_checks:
        quality_index[row["role_id"]].append(row)

    scored = []
    for role in job_orders:
        weeks = weekly_index[role["role_id"]]
        totals = {key: sum(int(row[key]) for row in weeks) for key in ["applicants", "qualified", "screened", "submitted", "client_interviews", "offers", "placements", "candidate_dropoffs"]}
        submit_rate = totals["submitted"] / max(totals["screened"], 1)
        interview_rate = totals["client_interviews"] / max(totals["submitted"], 1)
        offer_rate = totals["offers"] / max(totals["client_interviews"], 1)
        quality_rows = quality_index[role["role_id"]]
        issue_count = sum(int(row["issue_count"]) for row in quality_rows)
        fail_count = sum(1 for row in quality_rows if row["severity"] == "Fail")
        quality_score = clamp(100 - issue_count * 2.6 - fail_count * 8, 0, 100)
        aging_ratio = int(role["open_days"]) / int(role["target_fill_days"])
        scarcity = 1.0 if role["work_structure"] == "Onsite" else 0.72
        priority_weight = {"Critical": 1.0, "High": 0.74, "Standard": 0.48}[role["priority"]]
        placement_readiness = clamp(
            100
            * (
                0.26 * submit_rate
                + 0.25 * interview_rate
                + 0.18 * offer_rate
                + 0.18 * (quality_score / 100)
                + 0.13 * float(role["hiring_manager_response_rate"])
            ),
            0,
            100,
        )
        fill_risk_score = clamp(
            100
            * (
                0.30 * clamp(aging_ratio, 0, 1.7) / 1.7
                + 0.22 * (1 - submit_rate)
                + 0.18 * (1 - interview_rate)
                + 0.16 * (1 - quality_score / 100)
                + 0.14 * scarcity
            )
            + 12 * priority_weight,
            0,
            100,
        )
        expected_shortlist_days = clamp(round(9 - submit_rate * 5 + aging_ratio * 4 + (100 - quality_score) / 18, 1), 2.5, 18)
        if quality_score < 76:
            recommendation = "Clean source data before promising a new shortlist"
        elif submit_rate < 0.32:
            recommendation = "Reset sourcing mix and tighten screening criteria"
        elif interview_rate < 0.24:
            recommendation = "Review client feedback and adjust candidate slate"
        elif aging_ratio > 1:
            recommendation = "Escalate aging role in the client review"
        else:
            recommendation = "Keep recruiting motion and prepare weekly readout"
        scored.append(
            {
                "role_id": role["role_id"],
                "client_segment": role["client_segment"],
                "role_family": role["role_family"],
                "city": role["city"],
                "work_structure": role["work_structure"],
                "priority": role["priority"],
                "open_days": int(role["open_days"]),
                "submit_rate": pct(submit_rate),
                "interview_rate": pct(interview_rate),
                "offer_rate": pct(offer_rate),
                "placement_readiness_score": round(placement_readiness, 1),
                "fill_risk_score": round(fill_risk_score, 1),
                "data_quality_score": round(quality_score, 1),
                "expected_shortlist_days": expected_shortlist_days,
                "placements": totals["placements"],
                "estimated_weekly_margin": round((float(role["bill_rate"]) - float(role["pay_rate"])) * max(totals["submitted"], 1), 0),
                "recommendation": recommendation,
                "recruiter_owner": role["recruiter_owner"],
            }
        )

    age_z = zscores(scored, "open_days")
    risk_z = zscores(scored, "fill_risk_score")
    margin_z = zscores(scored, "estimated_weekly_margin")
    for row in scored:
        priority = {"Critical": 14, "High": 8, "Standard": 3}[row["priority"]]
        row["priority_score"] = round(60 + risk_z[row["role_id"]] * 11 + age_z[row["role_id"]] * 7 + margin_z[row["role_id"]] * 6 + priority, 1)

    return sorted(scored, key=lambda row: row["priority_score"], reverse=True)


def build_actions(priority_queue):
    actions = []
    for idx, row in enumerate(priority_queue[:24], 1):
        if row["data_quality_score"] < 76:
            action_type = "Data clean-up"
            owner = "Analytics"
            effort = 4
        elif row["submit_rate"] < 32:
            action_type = "Sourcing reset"
            owner = "Recruiting"
            effort = 6
        elif row["interview_rate"] < 24:
            action_type = "Client calibration"
            owner = "Account lead"
            effort = 3
        else:
            action_type = "Executive review"
            owner = row["recruiter_owner"]
            effort = 2
        actions.append(
            {
                "action_id": f"ACT{idx:03d}",
                "role_id": row["role_id"],
                "action_type": action_type,
                "owner": owner,
                "effort_hours": effort,
                "expected_shortlist_days": row["expected_shortlist_days"],
                "expected_margin_protected": row["estimated_weekly_margin"],
                "status": "Ready for review" if idx <= 8 else "Queued",
            }
        )
    return actions


def write_markdown_files(summary):
    (ROOT / "analysis" / "analysis_plan.md").write_text(
        """# Analysis Plan

## Objective

Rank open analytical and technical staffing roles by fill risk, placement readiness, source-data quality, and near-term margin exposure.

## Method

1. Generate synthetic job orders, candidate pipeline events, weekly funnel metrics, market skill signals, and data quality checks.
2. Normalize funnel conversion, role aging, hiring manager responsiveness, work-structure scarcity, and source-data quality into role-level scores.
3. Build a priority queue that explains which role needs action, why the role is at risk, and who should own the next step.
4. Translate the queue into a recruiter and client-facing brief.

## Validation

The SQL checks in this repo test funnel math, missing fields, duplicate candidates, stale roles, and stage consistency. The front-end workbench displays the same outputs generated by the Python scoring script.
""",
        encoding="utf-8",
    )
    (ROOT / "analysis" / "executive_findings.md").write_text(
        f"""# Executive Findings

## Weekly readout

- {summary["critical_roles"]} critical or high-priority roles are in the current decision queue.
- Average placement readiness is {summary["avg_readiness"]} out of 100.
- Average fill risk is {summary["avg_fill_risk"]} out of 100.
- {summary["quality_failures"]} role-level quality checks failed and need remediation before leadership treats the funnel as clean.

## Interpretation

The largest risks are not only low applicant volume. Aging roles, onsite constraints, inconsistent candidate records, and slow client feedback combine to reduce placement readiness.

## Recommendation

Use the model queue to split this week's operating review into three lanes: clean source data, reset sourcing strategy, and calibrate client feedback. That keeps the discussion focused on decisions instead of dashboard inspection.
""",
        encoding="utf-8",
    )


def main():
    DATA.mkdir(exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    SRC.mkdir(exist_ok=True)

    job_orders = generate_job_orders()
    weekly = generate_weekly_metrics(job_orders)
    events = generate_pipeline_events(job_orders)
    quality = generate_quality_checks(job_orders, events)
    market = generate_market_signals(job_orders)
    priority_queue = score_roles(job_orders, weekly, quality)
    actions = build_actions(priority_queue)

    write_csv(DATA / "job_orders.csv", job_orders, list(job_orders[0].keys()))
    write_csv(DATA / "weekly_funnel_metrics.csv", weekly, list(weekly[0].keys()))
    write_csv(DATA / "candidate_pipeline_events.csv", events, list(events[0].keys()))
    write_csv(DATA / "data_quality_checks.csv", quality, list(quality[0].keys()))
    write_csv(DATA / "market_skill_signals.csv", market, list(market[0].keys()))
    write_csv(DATA / "recommended_actions.csv", actions, list(actions[0].keys()))
    write_csv(OUT / "role_priority_queue.csv", priority_queue, list(priority_queue[0].keys()))

    quality_queue = sorted(
        [
            row
            for row in quality
            if row["severity"] in {"Fail", "Watch"}
        ],
        key=lambda row: (row["severity"] != "Fail", -int(row["issue_count"])),
    )
    write_csv(OUT / "data_quality_queue.csv", quality_queue, list(quality_queue[0].keys()))

    model_summary_rows = [
        {
            "metric": "Average placement readiness",
            "value": round(sum(row["placement_readiness_score"] for row in priority_queue) / len(priority_queue), 1),
            "interpretation": "Higher means the role has enough clean funnel signal to move toward shortlist or placement.",
        },
        {
            "metric": "Average fill risk",
            "value": round(sum(row["fill_risk_score"] for row in priority_queue) / len(priority_queue), 1),
            "interpretation": "Higher means aging, scarcity, poor conversion, or quality issues are likely to delay fill.",
        },
        {
            "metric": "Quality checks requiring review",
            "value": len(quality_queue),
            "interpretation": "Rows where source issues could distort reporting or recruiter action.",
        },
        {
            "metric": "Top role priority score",
            "value": priority_queue[0]["priority_score"],
            "interpretation": "Composite decision score for this week's first operating review item.",
        },
    ]
    write_csv(OUT / "model_summary.csv", model_summary_rows, list(model_summary_rows[0].keys()))

    stakeholder_rows = [
        {
            "brief_section": "Situation",
            "message": "Open analytical and technical roles have enough funnel activity to rank, but the riskiest roles combine aging, onsite constraints, and source-data issues.",
        },
        {
            "brief_section": "Decision needed",
            "message": "Decide whether to clean records, reset sourcing, or calibrate with the client before increasing recruiter effort.",
        },
        {
            "brief_section": "Recommended first move",
            "message": f"Start with {priority_queue[0]['role_id']} in {priority_queue[0]['client_segment']}: {priority_queue[0]['recommendation'].lower()}.",
        },
        {
            "brief_section": "Risk if ignored",
            "message": "Leadership may overreact to volume gaps while the root issue is conversion quality, stale stage data, or delayed client feedback.",
        },
    ]
    write_csv(OUT / "stakeholder_brief.csv", stakeholder_rows, list(stakeholder_rows[0].keys()))

    summary = {
        "roles": len(job_orders),
        "pipeline_events": len(events),
        "weekly_rows": len(weekly),
        "critical_roles": sum(1 for row in priority_queue if row["priority"] in {"Critical", "High"}),
        "avg_readiness": round(sum(row["placement_readiness_score"] for row in priority_queue) / len(priority_queue), 1),
        "avg_fill_risk": round(sum(row["fill_risk_score"] for row in priority_queue) / len(priority_queue), 1),
        "quality_failures": sum(1 for row in quality if row["severity"] == "Fail"),
        "top_role": priority_queue[0],
    }
    write_markdown_files(summary)

    app_payload = {
        "summary": summary,
        "priorityQueue": priority_queue[:12],
        "qualityQueue": quality_queue[:12],
        "actions": actions[:10],
        "modelSummary": model_summary_rows,
        "marketSignals": sorted(market, key=lambda row: row["demand_index"], reverse=True)[:8],
        "brief": stakeholder_rows,
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (OUT / "app_payload.json").write_text(json.dumps(app_payload, indent=2), encoding="utf-8")
    (SRC / "data.js").write_text("window.workbenchData = " + json.dumps(app_payload, indent=2) + ";\n", encoding="utf-8")

    print(f"Generated {len(job_orders)} job orders, {len(events)} candidate events, and {len(priority_queue)} scored roles.")
    print(f"Top priority: {priority_queue[0]['role_id']} with score {priority_queue[0]['priority_score']}.")


if __name__ == "__main__":
    main()
