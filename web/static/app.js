/**
 * web/static/app.js - Bộ điều phối trạng thái giao diện chính của TAIO SEO Check.
 * Quản lý 4 trạng thái:
 * 1. Chờ nhập (state-input)
 * 2. Đang kiểm tra (state-progress)
 * 3. Kết quả tổng quan (state-results)
 * 4. Soi chi tiết 6 tab (state-details)
 */

let appState = {
  currentResult: null,
  config: null
};

document.addEventListener("DOMContentLoaded", async () => {
  await initApp();
});

async function initApp() {
  AIConfig.updateStatusPill();

  // 1. Tải cấu hình từ server
  try {
    const resp = await fetch("/api/config");
    if (resp.ok) {
      const cfg = await resp.json();
      appState.config = cfg;

      // Cập nhật nhãn phiên bản dưới logo
      const verEl = document.getElementById("brand-version-tag");
      if (verEl) {
        verEl.textContent = `v${cfg.version} · ${cfg.stamp}`;
      }

      // Cập nhật số lượt kiểm tra còn lại
      updateRemainingLimitDisplay(cfg.remaining, cfg.daily_limit);

      // Khởi tạo Modal Cài đặt AI
      initAISettingsModal(cfg.ai?.providers || [], cfg.local_mode);
    }
  } catch (err) {
    console.error("Lỗi tải cấu hình:", err);
  }

  // 2. Bắt sự kiện form kiểm tra
  const form = document.getElementById("seo-form");
  const urlInput = document.getElementById("seo-url-input");

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const rawUrl = urlInput.value.trim();
      if (!rawUrl) return;

      await startSeoCheck(rawUrl);
    });
  }

  // 3. Nút tải báo cáo
  const btnDownloadHtml = document.getElementById("btn-download-html");
  if (btnDownloadHtml) {
    btnDownloadHtml.addEventListener("click", () => {
      if (appState.currentResult) {
        ReportGenerator.downloadHtmlReport(
          appState.currentResult,
          window.lastAIRewriteResult,
          window.lastAIExplainResult
        );
      }
    });
  }

  const btnDownloadMd = document.getElementById("btn-download-md");
  if (btnDownloadMd) {
    btnDownloadMd.addEventListener("click", () => {
      if (appState.currentResult) {
        ReportGenerator.downloadMarkdownReport(
          appState.currentResult,
          window.lastAIRewriteResult,
          window.lastAIExplainResult
        );
      }
    });
  }

  // 4. Nút Soi chi tiết
  const btnToggleDetails = document.getElementById("btn-toggle-details");
  if (btnToggleDetails) {
    btnToggleDetails.addEventListener("click", () => {
      const detailsSection = document.getElementById("section-details");
      if (detailsSection) {
        detailsSection.style.display = "block";
        detailsSection.scrollIntoView({ behavior: "smooth" });
      }
    });
  }

  // 5. Nút Giải thích lỗi bằng AI
  const btnExplainFixes = document.getElementById("btn-explain-fixes");
  if (btnExplainFixes) {
    btnExplainFixes.addEventListener("click", () => {
      if (appState.currentResult) {
        AIPanel.explainTopFixes(appState.currentResult);
      }
    });
  }
}

function updateRemainingLimitDisplay(remaining, dailyLimit) {
  const el = document.getElementById("daily-limit-text");
  if (el) {
    if (dailyLimit <= 0) {
      el.textContent = "Chế độ không giới hạn lượt kiểm tra.";
    } else {
      el.textContent = `Lượt kiểm tra miễn phí hôm nay: còn ${remaining}/${dailyLimit}`;
    }
  }
}

async function startSeoCheck(url) {
  switchState("progress");
  showErrorMessage("");

  try {
    const resp = await fetch("/api/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: url })
    });

    const data = await resp.json();
    if (!resp.ok) {
      throw new Error(data.error || "Có lỗi xảy ra khi kiểm tra website.");
    }

    appState.currentResult = data;
    renderSeoResults(data);
    DetailsView.render(data.details, data.ai_context, data.notices);

    // Cập nhật lại số lượt còn lại
    if (appState.config && typeof appState.config.remaining === "number") {
      appState.config.remaining = Math.max(0, appState.config.remaining - 1);
      updateRemainingLimitDisplay(appState.config.remaining, appState.config.daily_limit);
    }

    switchState("results");
  } catch (err) {
    switchState("input");
    showErrorMessage(err.message);
  }
}

function renderSeoResults(result) {
  // 1. Điểm tổng thể & Vòng tròn Gauge
  renderScoreGauge("main-score-gauge", result.score, result.band_label);

  const urlDisplay = document.getElementById("result-url-display");
  if (urlDisplay) {
    urlDisplay.textContent = result.final_url || result.url;
  }

  // 2. Điểm 4 nhóm
  const groupGrid = document.getElementById("group-scores-grid");
  if (groupGrid) {
    groupGrid.innerHTML = "";
    (result.groups || []).forEach(g => {
      const card = document.createElement("div");
      card.className = "group-card";

      const name = document.createElement("div");
      name.className = "group-name";
      name.textContent = `${g.name} (${g.weight}đ)`;

      const val = document.createElement("div");
      val.className = "group-score-val";

      if (g.score !== null) {
        val.textContent = `${g.score}%`;
        val.style.color = g.score >= 90 ? "var(--color-green)" : (g.score >= 50 ? "var(--color-orange)" : "var(--color-red)");
      } else {
        val.textContent = "N/A";
        val.style.color = "var(--color-gray)";
        val.title = "Không đo được";
      }

      card.appendChild(name);
      card.appendChild(val);
      groupGrid.appendChild(card);
    });
  }

  // 3. Danh sách 5 việc cần sửa ngay
  const fixesContainer = document.getElementById("top-fixes-container");
  if (fixesContainer) {
    fixesContainer.innerHTML = "";
    const topIds = result.top_fixes || [];

    if (topIds.length === 0) {
      fixesContainer.innerHTML = `
        <div class="card" style="text-align:center; padding:20px; background:var(--color-green-bg); border-color:var(--color-green-border);">
          <strong style="color:var(--color-green);">🎉 Tuyệt vời! Không phát hiện lỗi nghiêm trọng nào cần khắc phục ngay.</strong>
        </div>
      `;
    } else {
      topIds.forEach((fid, idx) => {
        const c = (result.checks || []).find(it => it.id === fid);
        if (!c) return;

        const item = document.createElement("div");
        item.className = "fix-item";

        // Tiêu đề lỗi
        const header = document.createElement("div");
        header.className = "fix-header";

        const title = document.createElement("div");
        title.className = "fix-title";
        title.textContent = `#${idx + 1}. ${c.name}`;

        const badge = document.createElement("span");
        badge.className = `fix-badge badge-${c.status}`;
        badge.textContent = c.status === "fail" ? "Không đạt" : "Cảnh báo";

        header.appendChild(title);
        header.appendChild(badge);

        // Nội dung 4 phần
        const details = document.createElement("div");
        details.className = "fix-details";

        const pVal = document.createElement("div");
        pVal.innerHTML = `<strong>Hiện tại:</strong> `;
        pVal.appendChild(document.createTextNode(c.value || "Không đạt yêu cầu"));

        const pWhy = document.createElement("div");
        pWhy.innerHTML = `<strong>Vì sao quan trọng:</strong> `;
        pWhy.appendChild(document.createTextNode(c.why || ""));

        const pFix = document.createElement("div");
        pFix.innerHTML = `<strong>Cách sửa:</strong> `;
        pFix.appendChild(document.createTextNode(c.fix || ""));

        const pVerify = document.createElement("div");
        pVerify.style.fontSize = "12px";
        pVerify.style.color = "var(--text-muted)";
        pVerify.innerHTML = `<strong>Cách kiểm tra lại:</strong> `;
        pVerify.appendChild(document.createTextNode(c.verify || ""));

        details.appendChild(pVal);
        details.appendChild(pWhy);
        details.appendChild(pFix);
        details.appendChild(pVerify);

        // Khe chờ AI giải thích
        const aiSlot = document.createElement("div");
        aiSlot.id = `fix-ai-slot-${c.id}`;
        aiSlot.className = "fix-ai-box";
        aiSlot.style.display = "none";

        item.appendChild(header);
        item.appendChild(details);
        item.appendChild(aiSlot);
        fixesContainer.appendChild(item);
      });
    }
  }

  // 4. Accordion xem toàn bộ 24 hạng mục
  renderAllChecksAccordion(result.checks || []);
}

function renderAllChecksAccordion(checks) {
  const container = document.getElementById("all-checks-accordion");
  if (!container) return;
  container.innerHTML = "";

  const table = document.createElement("table");
  table.className = "data-table";
  table.innerHTML = `
    <thead>
      <tr>
        <th>Hạng mục kiểm tra</th>
        <th>Nhóm</th>
        <th>Trạng thái</th>
        <th>Kết quả ghi nhận</th>
      </tr>
    </thead>
  `;

  const tbody = document.createElement("tbody");
  checks.forEach(c => {
    const tr = document.createElement("tr");

    const tdName = document.createElement("td");
    tdName.style.fontWeight = "600";
    tdName.textContent = c.name;

    const tdGroup = document.createElement("td");
    tdGroup.textContent = c.group;

    const tdStatus = document.createElement("td");
    const badge = document.createElement("span");
    badge.className = `fix-badge badge-${c.status}`;
    badge.textContent = c.status;
    tdStatus.appendChild(badge);

    const tdVal = document.createElement("td");
    tdVal.textContent = c.value || "-";

    tr.appendChild(tdName);
    tr.appendChild(tdGroup);
    tr.appendChild(tdStatus);
    tr.appendChild(tdVal);
    tbody.appendChild(tr);
  });

  table.appendChild(tbody);
  container.appendChild(table);
}

function switchState(state) {
  const sInput = document.getElementById("state-input");
  const sProgress = document.getElementById("state-progress");
  const sResults = document.getElementById("state-results");
  const sDetails = document.getElementById("section-details");

  if (sInput) sInput.style.display = (state === "input" || state === "results") ? "block" : "none";
  if (sProgress) sProgress.style.display = state === "progress" ? "block" : "none";
  if (sResults) sResults.style.display = state === "results" ? "block" : "none";
  if (sDetails) sDetails.style.display = "none"; // Mặc định ẩn, người dùng bấm "Soi chi tiết" mới mở
}

function showErrorMessage(msg) {
  const errBox = document.getElementById("error-box");
  if (errBox) {
    if (msg) {
      errBox.textContent = msg;
      errBox.style.display = "block";
    } else {
      errBox.textContent = "";
      errBox.style.display = "none";
    }
  }
}
