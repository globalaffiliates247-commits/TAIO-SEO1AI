/**
 * web/static/ai_panel.js - Giao diện cho 2 tính năng AI (F11 & F12).
 * F11: Gợi ý viết lại Title & Meta Description.
 * F12: Giải thích lỗi theo ngữ cảnh trang web.
 * Đảm bảo: Mọi kết quả hiển thị bằng textContent chống XSS.
 */

const AIPanel = {
  // --- F11: Gợi ý Title & Meta Description ---
  openRewriteModal(aiContext) {
    if (!AIConfig.hasKey()) {
      alert("Chưa có key AI. Vui lòng mở Cài đặt AI để nhập key của bạn.");
      document.getElementById("ai-status-pill")?.click();
      return;
    }

    const modal = document.getElementById("ai-rewrite-modal");
    const closeBtn = document.getElementById("ai-rewrite-close");
    const submitBtn = document.getElementById("ai-rewrite-submit");
    const container = document.getElementById("ai-rewrite-results");
    const loading = document.getElementById("ai-rewrite-loading");

    // Điền thông tin mặc định
    document.getElementById("ai-rewrite-brand").value = aiContext?.site_name || "";
    container.innerHTML = "";
    loading.style.display = "none";
    modal.classList.add("active");

    closeBtn.onclick = () => modal.classList.remove("active");

    submitBtn.onclick = async () => {
      const keyword = document.getElementById("ai-rewrite-keyword").value.trim();
      const style = document.getElementById("ai-rewrite-style").value;
      const brand = document.getElementById("ai-rewrite-brand").value.trim();

      loading.style.display = "block";
      container.innerHTML = "";
      submitBtn.disabled = true;

      try {
        const resp = await fetch("/api/ai/rewrite_meta", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-AI-Key": AIConfig.getKey()
          },
          body: JSON.stringify({
            provider: AIConfig.getProvider(),
            model: AIConfig.getModel(),
            base_url: AIConfig.getEndpoint(),
            page: aiContext,
            keyword: keyword,
            style: style,
            brand: brand
          })
        });

        const data = await resp.json();
        if (!resp.ok) {
          throw new Error(data.error || "Không thể lấy gợi ý từ AI.");
        }

        AIPanel.renderRewriteResults(container, data, aiContext);
      } catch (err) {
        const errDiv = document.createElement("div");
        errDiv.className = "fix-badge badge-fail";
        errDiv.style.padding = "10px";
        errDiv.textContent = err.message;
        container.appendChild(errDiv);
      } finally {
        loading.style.display = "none";
        submitBtn.disabled = false;
      }
    };
  },

  renderRewriteResults(container, data, aiContext) {
    container.innerHTML = "";

    // Lưu kết quả vào biến toàn cục để đưa vào báo cáo tải về nếu có
    window.lastAIRewriteResult = data;

    const notice = document.createElement("div");
    notice.style.fontSize = "12px";
    notice.style.color = "var(--text-muted)";
    notice.style.marginBottom = "16px";
    notice.textContent = "💡 Gợi ý do AI, cần bạn kiểm chứng. Điểm SEO cố định và chỉ thay đổi khi bạn cập nhật website thật.";
    container.appendChild(notice);

    // Bảng so sánh 3 Title
    const titleSection = document.createElement("div");
    titleSection.style.marginBottom = "20px";
    const titleHeader = document.createElement("h4");
    titleHeader.textContent = "3 Gợi ý Tiêu đề (Title) tối ưu:";
    titleHeader.style.marginBottom = "8px";
    titleSection.appendChild(titleHeader);

    data.titles.forEach((t, idx) => {
      const box = document.createElement("div");
      box.className = "fix-item";

      const topRow = document.createElement("div");
      topRow.style.display = "flex";
      topRow.style.justifyContent = "space-between";
      topRow.style.alignItems = "center";
      topRow.style.marginBottom = "4px";

      const angleTag = document.createElement("span");
      angleTag.className = "fix-ai-tag";
      angleTag.textContent = `Góc tiếp cận: ${t.angle}`;

      const charBadge = document.createElement("span");
      charBadge.className = `fix-badge ${t.in_range ? "badge-pass" : "badge-warn"}`;
      charBadge.textContent = `${t.chars} ký tự ${t.in_range ? "(Chuẩn)" : "(Hơi dài/ngắn)"}`;

      topRow.appendChild(angleTag);
      topRow.appendChild(charBadge);

      const content = document.createElement("div");
      content.style.fontWeight = "600";
      content.style.fontSize = "14px";
      content.textContent = t.text;

      const why = document.createElement("div");
      why.style.fontSize = "12.5px";
      why.style.color = "var(--text-muted)";
      why.style.marginTop = "4px";
      why.textContent = `Lý do: ${t.why}`;

      const copyBtn = document.createElement("button");
      copyBtn.className = "btn btn-secondary btn-sm";
      copyBtn.style.marginTop = "8px";
      copyBtn.textContent = "Sao chép tiêu đề";
      copyBtn.onclick = () => {
        navigator.clipboard.writeText(t.text);
        copyBtn.textContent = "Đã chép!";
        setTimeout(() => copyBtn.textContent = "Sao chép tiêu đề", 2000);
      };

      box.appendChild(topRow);
      box.appendChild(content);
      box.appendChild(why);
      box.appendChild(copyBtn);
      titleSection.appendChild(box);
    });
    container.appendChild(titleSection);

    // Bảng so sánh 3 Description
    const descSection = document.createElement("div");
    const descHeader = document.createElement("h4");
    descHeader.textContent = "3 Gợi ý Thẻ mô tả (Meta Description) tối ưu:";
    descHeader.style.marginBottom = "8px";
    descSection.appendChild(descHeader);

    data.descriptions.forEach((d, idx) => {
      const box = document.createElement("div");
      box.className = "fix-item";

      const topRow = document.createElement("div");
      topRow.style.display = "flex";
      topRow.style.justifyContent = "space-between";
      topRow.style.alignItems = "center";
      topRow.style.marginBottom = "4px";

      const angleTag = document.createElement("span");
      angleTag.className = "fix-ai-tag";
      angleTag.textContent = `Góc tiếp cận: ${d.angle}`;

      const charBadge = document.createElement("span");
      charBadge.className = `fix-badge ${d.in_range ? "badge-pass" : "badge-warn"}`;
      charBadge.textContent = `${d.chars} ký tự ${d.in_range ? "(Chuẩn)" : "(Ngoài ngưỡng 70–160)"}`;

      topRow.appendChild(angleTag);
      topRow.appendChild(charBadge);

      const content = document.createElement("div");
      content.style.fontSize = "13.5px";
      content.textContent = d.text;

      const why = document.createElement("div");
      why.style.fontSize = "12.5px";
      why.style.color = "var(--text-muted)";
      why.style.marginTop = "4px";
      why.textContent = `Lý do: ${d.why}`;

      const copyBtn = document.createElement("button");
      copyBtn.className = "btn btn-secondary btn-sm";
      copyBtn.style.marginTop = "8px";
      copyBtn.textContent = "Sao chép mô tả";
      copyBtn.onclick = () => {
        navigator.clipboard.writeText(d.text);
        copyBtn.textContent = "Đã chép!";
        setTimeout(() => copyBtn.textContent = "Sao chép mô tả", 2000);
      };

      box.appendChild(topRow);
      box.appendChild(content);
      box.appendChild(why);
      box.appendChild(copyBtn);
      descSection.appendChild(box);
    });
    container.appendChild(descSection);
  },

  // --- F12: Giải thích 5 việc cần sửa ngay theo ngữ cảnh ---
  async explainTopFixes(checkResult) {
    if (!AIConfig.hasKey()) {
      alert("Chưa có key AI. Vui lòng mở Cài đặt AI để nhập key của bạn.");
      document.getElementById("ai-status-pill")?.click();
      return;
    }

    const btn = document.getElementById("btn-explain-fixes");
    if (btn) {
      btn.disabled = true;
      btn.textContent = "Đang hỏi AI giải thích...";
    }

    const topFixIds = checkResult.top_fixes || [];
    const items = [];

    topFixIds.forEach(fid => {
      const c = checkResult.checks.find(it => it.id === fid);
      if (c) {
        items.push({
          id: c.id,
          status: c.status,
          value: c.value,
          expected: c.fix
        });
      }
    });

    try {
      const resp = await fetch("/api/ai/explain", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-AI-Key": AIConfig.getKey()
        },
        body: JSON.stringify({
          provider: AIConfig.getProvider(),
          model: AIConfig.getModel(),
          base_url: AIConfig.getEndpoint(),
          url: checkResult.final_url || checkResult.url,
          lang: checkResult.details?.overview?.lang || "vi",
          cms: checkResult.details?.overview?.cms || "unknown",
          items: items
        })
      });

      const data = await resp.json();
      if (!resp.ok) {
        throw new Error(data.error || "Không thể nhận phản hồi giải thích từ AI.");
      }

      // Lưu kết quả vào biến toàn cục cho báo cáo
      window.lastAIExplainResult = data;

      // Render từng lời giải thích vào khối tương ứng
      (data.items || []).forEach(aiItem => {
        const slot = document.getElementById(`fix-ai-slot-${aiItem.id}`);
        if (slot) {
          slot.innerHTML = "";
          slot.style.display = "block";

          const tag = document.createElement("div");
          tag.className = "fix-ai-tag";
          tag.textContent = "AI Giải thích cho trang của bạn";

          const fixText = document.createElement("div");
          fixText.style.marginBottom = "6px";
          fixText.textContent = aiItem.fix;

          slot.appendChild(tag);
          slot.appendChild(fixText);

          if (aiItem.example) {
            const exBox = document.createElement("pre");
            exBox.style.background = "#fff";
            exBox.style.padding = "6px 8px";
            exBox.style.borderRadius = "4px";
            exBox.style.fontSize = "12px";
            exBox.style.overflowX = "auto";
            exBox.textContent = aiItem.example;
            slot.appendChild(exBox);
          }
        }
      });

      if (btn) btn.textContent = "Đã có giải thích từ AI";
    } catch (err) {
      alert(`Lỗi AI: ${err.message}`);
      if (btn) {
        btn.disabled = false;
        btn.textContent = "Giải thích cho trang của tôi";
      }
    }
  }
};
