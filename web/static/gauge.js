/**
 * web/static/gauge.js - Vẽ vòng tròn điểm sức khoẻ SEO 0–100 với SVG động.
 * 3 dải màu chuẩn Lighthouse:
 * - 90–100: Xanh (Tốt)
 * - 50–89: Cam (Cần cải thiện)
 * - 0–49: Đỏ (Yếu)
 */

function renderScoreGauge(containerId, score, bandText) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const validScore = typeof score === "number" ? Math.max(0, Math.min(100, Math.round(score))) : 0;

  // Xác định màu sắc
  let color = "#ef4444"; // Đỏ
  if (score >= 90) {
    color = "#10b981"; // Xanh
  } else if (score >= 50) {
    color = "#f59e0b"; // Cam
  }

  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (validScore / 100) * circumference;

  container.innerHTML = `
    <div class="gauge-wrap">
      <svg class="gauge-svg" width="140" height="140" viewBox="0 0 140 140">
        <circle class="gauge-bg" cx="70" cy="70" r="${radius}" />
        <circle class="gauge-progress" id="gauge-circle-anim"
          cx="70" cy="70" r="${radius}"
          stroke="${color}"
          stroke-dasharray="${circumference}"
          stroke-dashoffset="${circumference}" />
      </svg>
      <div class="gauge-number">
        <div class="gauge-score" style="color: ${color};">${validScore}</div>
        <div class="gauge-band" style="color: ${color};">${escapeHtml(bandText || "")}</div>
      </div>
    </div>
  `;

  // Kích hoạt animation
  setTimeout(() => {
    const circle = document.getElementById("gauge-circle-anim");
    if (circle) {
      circle.style.strokeDashoffset = offset;
    }
  }, 50);
}

function escapeHtml(str) {
  if (!str) return "";
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
