-- SQL-style checks for the synthetic staffing analytics workbench.
-- Table names mirror the CSV files in /data and /analysis/outputs.

-- 1. Funnel counts should never increase as candidates move deeper into the weekly funnel.
select
  role_id,
  week_start,
  applicants,
  qualified,
  screened,
  submitted,
  client_interviews,
  offers,
  placements
from weekly_funnel_metrics
where qualified > applicants
   or screened > qualified
   or submitted > screened
   or client_interviews > submitted
   or offers > client_interviews
   or placements > offers;

-- 2. Critical roles should have rate and owner fields populated before they enter the client review.
select
  role_id,
  priority,
  pay_rate,
  bill_rate,
  recruiter_owner
from job_orders
where priority = 'Critical'
  and (pay_rate is null or bill_rate is null or recruiter_owner is null);

-- 3. Candidate events with duplicate flags should be reviewed before model scoring.
select
  role_id,
  count(*) as duplicate_candidate_events
from candidate_pipeline_events
where duplicate_candidate_flag = 1
group by role_id
having count(*) >= 3
order by duplicate_candidate_events desc;

-- 4. Failed quality checks should map to an owner and a role in the job order table.
select
  q.role_id,
  q.check_name,
  q.issue_count,
  q.owner
from data_quality_checks q
left join job_orders j
  on q.role_id = j.role_id
where q.severity = 'Fail'
  and (j.role_id is null or q.owner is null);

-- 5. Ranked roles should expose the fields needed for a stakeholder-ready decision.
select
  role_id,
  priority_score,
  placement_readiness_score,
  fill_risk_score,
  data_quality_score,
  expected_shortlist_days,
  recommendation
from role_priority_queue
where recommendation is null
   or expected_shortlist_days is null
   or priority_score is null;

-- 6. Skill signals should identify pressure when demand exceeds supply.
select
  skill,
  open_role_count,
  demand_index,
  available_supply_index,
  market_pressure
from market_skill_signals
where demand_index > available_supply_index
  and market_pressure <> 'High';
