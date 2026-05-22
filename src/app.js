const data = window.workbenchData;

const formatNumber = new Intl.NumberFormat("en-US");
const formatCurrency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

function text(value) {
  return String(value ?? "");
}

function riskClass(value) {
  if (value >= 78) return "risk-high";
  if (value >= 64) return "risk-watch";
  return "risk-low";
}

function scoreClass(value) {
  if (value >= 70) return "score-good";
  if (value >= 52) return "score-watch";
  return "score-low";
}

function renderKpis() {
  const summary = data.summary;
  const kpis = [
    ["Open roles modeled", summary.roles, "job orders"],
    ["Pipeline events", formatNumber.format(summary.pipeline_events), "candidate-stage records"],
    ["Avg fill risk", summary.avg_fill_risk, "0 to 100"],
    ["Quality failures", summary.quality_failures, "checks needing cleanup"],
  ];
  document.getElementById("kpiGrid").innerHTML = kpis
    .map(([label, value, note]) => `<article class="kpi"><span>${label}</span><strong>${value}</strong><em>${note}</em></article>`)
    .join("");
}

function renderHeader() {
  const top = data.priorityQueue[0];
  document.getElementById("topDecision").textContent = `${top.role_id} | ${top.role_family}`;
  document.getElementById("topRecommendation").textContent = top.recommendation;
}

function renderPriorityRows() {
  document.getElementById("priorityRows").innerHTML = data.priorityQueue
    .map(
      (row) => `
        <tr>
          <td><strong>${row.role_id}</strong><span>${row.role_family} | ${row.city} | ${row.work_structure}</span></td>
          <td>${row.client_segment}</td>
          <td><mark>${row.priority}</mark></td>
          <td><b class="${riskClass(row.fill_risk_score)}">${row.fill_risk_score}</b></td>
          <td><b class="${scoreClass(row.placement_readiness_score)}">${row.placement_readiness_score}</b></td>
          <td>${row.recommendation}</td>
        </tr>
      `
    )
    .join("");
}

function renderSkillBars() {
  const maxDemand = Math.max(...data.marketSignals.map((row) => row.demand_index));
  document.getElementById("skillBars").innerHTML = data.marketSignals
    .map((row) => {
      const width = Math.round((row.demand_index / maxDemand) * 100);
      return `
        <div class="bar-item">
          <div class="bar-label"><strong>${row.skill}</strong><span>${row.open_role_count} roles</span></div>
          <div class="bar-track"><i style="width:${width}%"></i></div>
          <div class="bar-foot"><span>Demand ${row.demand_index}</span><span>${row.market_pressure} pressure</span></div>
        </div>
      `;
    })
    .join("");
}

function renderModelSummary() {
  document.getElementById("modelSummary").innerHTML = data.modelSummary
    .map(
      (row) => `
        <article>
          <span>${row.metric}</span>
          <strong>${row.value}</strong>
          <p>${row.interpretation}</p>
        </article>
      `
    )
    .join("");
}

function renderModelCards() {
  document.getElementById("modelCards").innerHTML = data.priorityQueue
    .slice(0, 6)
    .map(
      (row) => `
        <article>
          <div class="card-top">
            <span>${row.role_id}</span>
            <b>${row.priority_score}</b>
          </div>
          <h3>${row.role_family}</h3>
          <dl>
            <div><dt>Submit rate</dt><dd>${row.submit_rate}%</dd></div>
            <div><dt>Interview rate</dt><dd>${row.interview_rate}%</dd></div>
            <div><dt>Quality</dt><dd>${row.data_quality_score}</dd></div>
            <div><dt>Shortlist</dt><dd>${row.expected_shortlist_days} days</dd></div>
          </dl>
          <p>${row.recommendation}</p>
        </article>
      `
    )
    .join("");
}

function renderQuality() {
  document.getElementById("qualityRows").innerHTML = data.qualityQueue
    .map(
      (row) => `
        <tr>
          <td><strong>${row.role_id}</strong></td>
          <td>${row.check_name}</td>
          <td>${row.issue_count} of ${row.records_tested}</td>
          <td><mark class="${row.severity.toLowerCase()}">${row.severity}</mark></td>
          <td>${row.owner}</td>
        </tr>
      `
    )
    .join("");

  const failCount = data.qualityQueue.filter((row) => row.severity === "Fail").length;
  const watchCount = data.qualityQueue.filter((row) => row.severity === "Watch").length;
  document.getElementById("qualityNarrative").innerHTML = [
    ["Failing checks", `${failCount} controls block clean reporting until records are corrected.`],
    ["Review checks", `${watchCount} lower-severity checks are held behind the failure queue and can be footnoted when surfaced.`],
    ["Preprocessing rule", "Duplicate candidates, stale role status, and missing rate data are penalized before the model ranks fill risk."],
  ]
    .map(([label, body]) => `<article><strong>${label}</strong><p>${body}</p></article>`)
    .join("");
}

function renderBrief() {
  document.getElementById("briefBlocks").innerHTML = data.brief
    .map(
      (row) => `
        <article>
          <span>${row.brief_section}</span>
          <p>${row.message}</p>
        </article>
      `
    )
    .join("");

  document.getElementById("actionRows").innerHTML = data.actions
    .slice(0, 6)
    .map(
      (row) => `
        <article>
          <div>
            <strong>${row.role_id}</strong>
            <span>${row.action_type} | ${row.owner}</span>
          </div>
          <b>${formatCurrency.format(row.expected_margin_protected)}</b>
        </article>
      `
    )
    .join("");
}

function bindTabs() {
  document.querySelectorAll(".tab-button").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".tab-button").forEach((item) => item.classList.remove("active"));
      document.querySelectorAll(".surface").forEach((surface) => surface.classList.remove("active"));
      button.classList.add("active");
      document.getElementById(button.dataset.view).classList.add("active");
    });
  });
}

renderHeader();
renderKpis();
renderPriorityRows();
renderSkillBars();
renderModelSummary();
renderModelCards();
renderQuality();
renderBrief();
bindTabs();
