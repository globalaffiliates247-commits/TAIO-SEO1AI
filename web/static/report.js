/**
 * web/static/report.js - Tạo và tải báo cáo SEO (HTML tự chứa & Markdown).
 * Chạy hoàn toàn trên trình duyệt người dùng, máy chủ không lưu báo cáo.
 */

const ReportGenerator = {
  downloadHtmlReport(result, aiRewrite, aiExplain) {
    const title = `Báo cáo SEO - ${result.final_url || result.url}`;
    const dateStr = new Date(result.checked_at).toLocaleString("vi-VN");

    let aiSectionHtml = "";
    if (aiRewrite || aiExplain) {
      aiSectionHtml += `
        <div class="report-section" style="border-top:2px dashed #cbd5e1; padding-top:20px; margin-top:30px;">
          <h2 style="color:#2563eb;">Phần Gợi Ý Của AI (Chưa kiểm chứng)</h2>
          <p style="font-size:12px; color:#64748b;">Dưới đây là các gợi ý được hỗ trợ bởi Trí tuệ Nhân tạo bằng API Key riêng của người dùng.</p>
      `;

      if (aiRewrite) {
        aiSectionHtml += `
          <h3 style="margin-top:16px;">Gợi ý Tiêu đề & Mô tả từ AI:</h3>
          <ul>
            ${(aiRewrite.titles || []).map(t => `<li><strong>${this.escape(t.text)}</strong> (${t.chars} ký tự) — <em>${this.escape(t.why)}</em></li>`).join("")}
          </ul>
          <ul>
            ${(aiRewrite.descriptions || []).map(d => `<li><strong>${this.escape(d.text)}</strong> (${d.chars} ký tự) — <em>${this.escape(d.why)}</em></li>`).join("")}
          </ul>
        `;
      }

      if (aiExplain && aiExplain.items) {
        aiSectionHtml += `
          <h3 style="margin-top:16px;">AI Giải thích các lỗi SEO theo ngữ cảnh:</h3>
          ${aiExplain.items.map(it => `
            <div style="margin-bottom:12px; background:#f8fafc; padding:10px; border-left:3px solid #2563eb;">
              <strong>${this.escape(it.id)}:</strong> ${this.escape(it.fix)}
              ${it.example ? `<pre style="font-size:11px; margin-top:4px;">${this.escape(it.example)}</pre>` : ""}
            </div>
          `).join("")}
        `;
      }

      aiSectionHtml += `</div>`;
    }

    const htmlContent = `<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <title>${this.escape(title)}</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.5; color: #1e293b; padding: 30px; max-width: 900px; margin: 0 auto; background: #fff; }
    h1 { font-size: 24px; color: #0f172a; margin-bottom: 4px; }
    .meta { font-size: 13px; color: #64748b; margin-bottom: 24px; }
    .score-banner { display: flex; align-items: center; gap: 20px; background: #f8fafc; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 24px; }
    .score-val { font-size: 48px; font-weight: 800; color: ${result.score >= 90 ? "#10b981" : (result.score >= 50 ? "#f59e0b" : "#ef4444")}; }
    .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 24px; }
    .grid-item { background: #f8fafc; border: 1px solid #e2e8f0; padding: 12px; border-radius: 8px; text-align: center; }
    .fix-item { border: 1px solid #e2e8f0; padding: 14px; border-radius: 8px; margin-bottom: 12px; }
    .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
    .badge-fail { background: #fef2f2; color: #ef4444; border: 1px solid #fecaca; }
    .badge-warn { background: #fffbeb; color: #f59e0b; border: 1px solid #fde68a; }
    .badge-pass { background: #ecfdf5; color: #10b981; border: 1px solid #a7f3d0; }
    .footer { text-align: center; font-size: 12px; color: #94a3b8; margin-top: 40px; border-top: 1px solid #e2e8f0; padding-top: 20px; }
    @media print {
      body { padding: 0; }
      .no-print { display: none; }
    }
  </style>
</head>
<body>
  <div class="no-print" style="margin-bottom:16px; text-align:right;">
    <button onclick="window.print()" style="padding:8px 16px; cursor:pointer;">🖨️ In ra PDF</button>
  </div>
  <h1>Báo Cáo Sức Khoẻ SEO Website</h1>
  <div class="meta">URL: ${this.escape(result.final_url || result.url)} · Kiểm tra lúc: ${dateStr}</div>

  <div class="score-banner">
    <div class="score-val">${result.score}</div>
    <div>
      <div style="font-size:18px; font-weight:700;">Điểm SEO Tổng Thể: ${this.escape(result.band_label || "")}</div>
      <div style="font-size:13px; color:#64748b;">Đánh giá dựa trên 24 quy chuẩn SEO kỹ thuật, nội dung, schema và Core Web Vitals.</div>
    </div>
  </div>

  <h2>Điểm Theo 4 Nhóm Trọng Điểm:</h2>
  <div class="grid">
    ${(result.groups || []).map(g => `
      <div class="grid-item">
        <div style="font-size:12px; color:#64748b;">${this.escape(g.name)} (${g.weight}đ)</div>
        <div style="font-size:20px; font-weight:700; margin-top:4px;">${g.score !== null ? g.score + "%" : "Không đo được"}</div>
      </div>
    `).join("")}
  </div>

  <h2>5 Việc Cần Sửa Ngay (Ưu tiên theo tác động):</h2>
  ${(result.top_fixes || []).map((fid, idx) => {
    const c = (result.checks || []).find(it => it.id === fid);
    if (!c) return "";
    return `
      <div class="fix-item">
        <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
          <strong>#${idx + 1}. ${this.escape(c.name)}</strong>
          <span class="badge badge-${c.status}">${c.status}</span>
        </div>
        <p style="font-size:13px; margin-bottom:4px;"><strong>Hiện tại:</strong> ${this.escape(c.value || "Không đạt")}</p>
        <p style="font-size:13px; margin-bottom:4px;"><strong>Cách sửa:</strong> ${this.escape(c.fix)}</p>
        <p style="font-size:12px; color:#64748b;"><strong>Cách kiểm tra lại:</strong> ${this.escape(c.verify)}</p>
      </div>
    `;
  }).join("")}

  ${aiSectionHtml}

  <div class="footer">
    Báo cáo được tạo bởi <strong>TAIO SEO Check</strong> (TAIO.CLUB)<br>
    Dựa trên mã nguồn mở Claude-seo (MIT) của Agrici Daniel · <a href="https://digitalbusiness.taio.club" target="_blank">digitalbusiness.taio.club</a>
  </div>
</body>
</html>`;

    this._downloadFile(htmlContent, `TAIO_SEO_Report_${Date.now()}.html`, "text/html;charset=utf-8");
  },

  downloadMarkdownReport(result, aiRewrite, aiExplain) {
    const dateStr = new Date(result.checked_at).toLocaleString("vi-VN");
    let md = `# Báo Cáo Sức Khoẻ SEO Website - TAIO.CLUB\n\n`;
    md += `- **URL kiểm tra:** ${result.final_url || result.url}\n`;
    md += `- **Thời gian:** ${dateStr}\n`;
    md += `- **Điểm tổng:** ${result.score}/100 (${result.band_label})\n\n`;

    md += `## 1. Điểm Theo 4 Nhóm Trọng Điểm\n\n`;
    (result.groups || []).forEach(g => {
      md += `- **${g.name}:** ${g.score !== null ? g.score + "%" : "Không đo được"} (Trọng số ${g.weight})\n`;
    });

    md += `\n## 2. 5 Việc Cần Sửa Ngay\n\n`;
    (result.top_fixes || []).forEach((fid, idx) => {
      const c = (result.checks || []).find(it => it.id === fid);
      if (c) {
        md += `### ${idx + 1}. ${c.name} [${c.status.toUpperCase()}]\n`;
        md += `- **Hiện trạng:** ${c.value || "Không đạt"}\n`;
        md += `- **Vì sao quan trọng:** ${c.why}\n`;
        md += `- **Cách sửa:** ${c.fix}\n`;
        md += `- **Cách kiểm tra:** ${c.verify}\n\n`;
      }
    });

    if (aiRewrite || aiExplain) {
      md += `## 3. Gợi Ý Của AI (Chưa kiểm chứng)\n\n`;
      if (aiRewrite) {
        md += `### Gợi ý Tiêu đề:\n`;
        (aiRewrite.titles || []).forEach(t => {
          md += `- ${t.text} (${t.chars} ký tự) - *${t.why}*\n`;
        });
        md += `\n### Gợi ý Thẻ mô tả:\n`;
        (aiRewrite.descriptions || []).forEach(d => {
          md += `- ${d.text} (${d.chars} ký tự) - *${d.why}*\n`;
        });
        md += `\n`;
      }
      if (aiExplain && aiExplain.items) {
        md += `### AI Giải thích ngữ cảnh:\n`;
        aiExplain.items.forEach(it => {
          md += `- **${it.id}:** ${it.fix}\n`;
          if (it.example) md += `  \`\`\`html\n  ${it.example}\n  \`\`\`\n`;
        });
        md += `\n`;
      }
    }

    md += `---\n*Báo cáo tạo bởi TAIO SEO Check (TAIO.CLUB) - Dựa trên mã nguồn mở Claude-seo (MIT) của Agrici Daniel*\n`;

    this._downloadFile(md, `TAIO_SEO_Report_${Date.now()}.md`, "text/markdown;charset=utf-8");
  },

  escape(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  },

  _downloadFile(content, fileName, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 100);
  }
};
