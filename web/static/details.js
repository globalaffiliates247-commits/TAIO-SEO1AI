/**
 * web/static/details.js - Giao diện Soi chi tiết 6 Tab (F9).
 * Tab 1: Tổng quan
 * Tab 2: Tiêu đề (Cây H1–H6)
 * Tab 3: Liên kết (Nội bộ & Ngoài)
 * Tab 4: Hình ảnh
 * Tab 5: Schema (JSON-LD)
 * Tab 6: Mạng xã hội (Open Graph, Twitter & Preview)
 *
 * MỌI dữ liệu từ website được render bằng textContent/DOM methods để chống XSS (T18).
 */

const DetailsView = {
  render(details, aiContext, notices) {
    this.renderOverview(details.overview, aiContext, notices);
    this.renderHeadings(details.headings);
    this.renderLinks(details.links);
    this.renderImages(details.images);
    this.renderSchema(details.schema);
    this.renderSocial(details.social);
    this.initTabSwitching();
  },

  initTabSwitching() {
    const tabBtns = document.querySelectorAll(".tab-btn");
    const tabPanes = document.querySelectorAll(".tab-pane");

    tabBtns.forEach(btn => {
      btn.onclick = () => {
        tabBtns.forEach(b => b.classList.remove("active"));
        tabPanes.forEach(p => p.classList.remove("active"));

        btn.classList.add("active");
        const targetId = btn.getAttribute("data-tab");
        const pane = document.getElementById(targetId);
        if (pane) pane.classList.add("active");
      };
    });
  },

  // --- TAB 1: TỔNG QUAN ---
  renderOverview(ov, aiContext, notices) {
    const pane = document.getElementById("tab-overview");
    if (!pane || !ov) return;
    pane.innerHTML = "";

    // 1. Thẻ thông báo (Notices)
    if (notices && notices.length > 0) {
      notices.forEach(n => {
        const nBox = document.createElement("div");
        nBox.className = "card";
        nBox.style.background = "var(--color-orange-bg)";
        nBox.style.borderColor = "var(--color-orange-border)";
        nBox.style.padding = "12px 16px";
        nBox.style.marginBottom = "16px";

        const title = document.createElement("strong");
        title.style.color = "var(--color-orange)";
        title.textContent = "Lưu ý: ";
        const desc = document.createElement("span");
        desc.textContent = n.text;

        nBox.appendChild(title);
        nBox.appendChild(desc);
        pane.appendChild(nBox);
      });
    }

    // 2. Tiêu đề (Title) & Nút Gợi ý AI
    const titleCard = document.createElement("div");
    titleCard.className = "card";
    titleCard.style.padding = "16px";

    const titleHeader = document.createElement("div");
    titleHeader.style.display = "flex";
    titleHeader.style.justifyContent = "space-between";
    titleHeader.style.alignItems = "center";
    titleHeader.style.marginBottom = "8px";

    const titleLabel = document.createElement("span");
    titleLabel.style.fontWeight = "700";
    titleLabel.textContent = "Thẻ Tiêu đề (Title)";

    const titleBadge = document.createElement("span");
    const tLen = ov.title?.length || 0;
    const tStatus = ov.title?.status || "warn";
    titleBadge.className = `fix-badge badge-${tStatus}`;
    titleBadge.textContent = `${tLen} ký tự (${tStatus === "pass" ? "Chuẩn" : "Cần tối ưu"})`;

    titleHeader.appendChild(titleLabel);
    titleHeader.appendChild(titleBadge);

    const titleContent = document.createElement("div");
    titleContent.style.fontSize = "15px";
    titleContent.style.fontWeight = "600";
    titleContent.style.color = "var(--primary)";
    titleContent.textContent = ov.title?.text || "(Không có thẻ title)";

    titleCard.appendChild(titleHeader);
    titleCard.appendChild(titleContent);
    pane.appendChild(titleCard);

    // 3. Thẻ Mô tả (Meta Description)
    const descCard = document.createElement("div");
    descCard.className = "card";
    descCard.style.padding = "16px";

    const descHeader = document.createElement("div");
    descHeader.style.display = "flex";
    descHeader.style.justifyContent = "space-between";
    descHeader.style.alignItems = "center";
    descHeader.style.marginBottom = "8px";

    const descLabel = document.createElement("span");
    descLabel.style.fontWeight = "700";
    descLabel.textContent = "Thẻ Mô tả (Meta Description)";

    const descBadge = document.createElement("span");
    const dLen = ov.description?.length || 0;
    const dStatus = ov.description?.status || "warn";
    descBadge.className = `fix-badge badge-${dStatus}`;
    descBadge.textContent = `${dLen} ký tự (${dStatus === "pass" ? "Chuẩn" : "Cần tối ưu"})`;

    descHeader.appendChild(descLabel);
    descHeader.appendChild(descBadge);

    const descContent = document.createElement("div");
    descContent.style.fontSize = "14px";
    descContent.textContent = ov.description?.text || "(Không có thẻ meta description)";

    descCard.appendChild(descHeader);
    descCard.appendChild(descContent);
    pane.appendChild(descCard);

    // Nút Gợi ý AI viết lại Title & Description
    const aiBtnBox = document.createElement("div");
    aiBtnBox.style.marginBottom = "20px";
    aiBtnBox.style.textAlign = "right";

    const aiBtn = document.createElement("button");
    aiBtn.className = "btn btn-primary btn-sm";
    aiBtn.textContent = "✨ Gợi ý viết lại bằng AI";
    aiBtn.onclick = () => AIPanel.openRewriteModal(aiContext);
    aiBtnBox.appendChild(aiBtn);
    pane.appendChild(aiBtnBox);

    // 4. Bảng thông số kỹ thuật trang
    const infoCard = document.createElement("div");
    infoCard.className = "card";
    infoCard.style.padding = "0";

    const table = document.createElement("table");
    table.className = "data-table";

    const rows = [
      ["URL đã nhập", ov.url?.raw || ""],
      ["URL đích cuối cùng", ov.url?.final || ""],
      ["URL sạch tham số quảng cáo", ov.url?.clean || ""],
      ["Thẻ Canonical", `${ov.canonical?.href || "(Thiếu)"} — [${ov.canonical?.relation_text || ""}]`],
      ["Khả năng Index", ov.indexability?.indexable ? "✅ Index được" : `⚠️ Bị chặn: ${(ov.indexability?.reasons || []).join(", ")}`],
      ["Meta Robots", ov.robots_meta || "(Mặc định index, follow)"],
      ["Ngôn ngữ (lang)", ov.lang || "(Không khai báo)"],
      ["Thẻ Viewport", ov.viewport || "(Không có)"],
      ["Số chữ nội dung", `${ov.word_count || 0} chữ`],
      ["Nền tảng website (CMS)", ov.cms ? ov.cms.toUpperCase() : "Chưa xác định"]
    ];

    const tbody = document.createElement("tbody");
    rows.forEach(([k, v]) => {
      const tr = document.createElement("tr");
      const tdK = document.createElement("td");
      tdK.style.fontWeight = "600";
      tdK.style.width = "220px";
      tdK.textContent = k;
      const tdV = document.createElement("td");
      tdV.textContent = v;
      tr.appendChild(tdK);
      tr.appendChild(tdV);
      tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    infoCard.appendChild(table);
    pane.appendChild(infoCard);
  },

  // --- TAB 2: TIÊU ĐỀ (CÂY H1–H6) ---
  renderHeadings(headings) {
    const pane = document.getElementById("tab-headings");
    if (!pane) return;
    pane.innerHTML = "";

    if (!headings || headings.length === 0) {
      pane.innerHTML = "<p style='color:var(--text-muted);'>Không tìm thấy thẻ tiêu đề nào (H1–H6) trên trang.</p>";
      return;
    }

    const counter = document.createElement("div");
    counter.style.fontSize = "13px";
    counter.style.color = "var(--text-muted)";
    counter.style.marginBottom = "12px";
    counter.textContent = `Tổng cộng: ${headings.length} thẻ tiêu đề`;
    pane.appendChild(counter);

    const list = document.createElement("div");
    headings.forEach(h => {
      const item = document.createElement("div");
      item.className = "heading-tree-item";
      item.style.paddingLeft = `${(h.level - 1) * 20 + 12}px`;

      const tag = document.createElement("span");
      tag.className = "heading-tag";
      tag.textContent = `H${h.level}`;
      item.appendChild(tag);

      const text = document.createElement("span");
      text.style.flex = "1";
      text.textContent = h.text || "(Tiêu đề rỗng)";
      if (!h.text) text.style.color = "var(--text-muted)";
      item.appendChild(text);

      if (h.issues && h.issues.length > 0) {
        h.issues.forEach(iss => {
          const badge = document.createElement("span");
          badge.className = "fix-badge badge-warn";
          badge.textContent = iss;
          item.appendChild(badge);
        });
      }

      list.appendChild(item);
    });

    pane.appendChild(list);
  },

  // --- TAB 3: LIÊN KẾT ---
  renderLinks(links) {
    const pane = document.getElementById("tab-links");
    if (!pane || !links) return;
    pane.innerHTML = "";

    // Header thống kê
    const stats = document.createElement("div");
    stats.style.display = "flex";
    stats.style.gap = "16px";
    stats.style.marginBottom = "16px";
    stats.style.fontSize = "13.5px";
    stats.innerHTML = `
      <span>Nội bộ: <strong>${links.internal?.length || 0}</strong></span>
      <span>Bên ngoài: <strong>${links.external?.length || 0}</strong></span>
      <span>Khác (mailto/tel/hash): <strong>${(links.other_counts?.mailto || 0) + (links.other_counts?.tel || 0) + (links.other_counts?.fragment || 0)}</strong></span>
    `;
    pane.appendChild(stats);

    // Ô tìm kiếm lọc liên kết
    const searchBox = document.createElement("input");
    searchBox.className = "form-control";
    searchBox.placeholder = "🔍 Lọc liên kết theo URL hoặc Anchor text...";
    searchBox.style.marginBottom = "16px";
    pane.appendChild(searchBox);

    const tableCard = document.createElement("div");
    tableCard.className = "card";
    tableCard.style.padding = "0";
    tableCard.style.maxHeight = "500px";
    tableCard.style.overflowY = "auto";

    const table = document.createElement("table");
    table.className = "data-table";
    table.innerHTML = `
      <thead>
        <tr>
          <th>Loại</th>
          <th>Văn bản neo (Anchor)</th>
          <th>Đích đến (URL)</th>
          <th>Thuộc tính (Rel)</th>
        </tr>
      </thead>
    `;

    const tbody = document.createElement("tbody");

    const allLinks = [
      ...(links.internal || []).map(l => ({ ...l, type: "Nội bộ" })),
      ...(links.external || []).map(l => ({ ...l, type: "Ngoài" }))
    ];

    function fillRows(filtered) {
      tbody.innerHTML = "";
      filtered.forEach(l => {
        const tr = document.createElement("tr");

        const tdType = document.createElement("td");
        tdType.textContent = l.type;

        const tdAnchor = document.createElement("td");
        tdAnchor.textContent = l.anchor || "(Neo rỗng)";
        if (!l.anchor) tdAnchor.style.color = "var(--text-muted)";

        const tdUrl = document.createElement("td");
        const a = document.createElement("a");
        a.href = l.url;
        a.target = "_blank";
        a.rel = "noopener noreferrer nofollow";
        a.textContent = l.url;
        a.style.color = "var(--primary)";
        tdUrl.appendChild(a);

        const tdRel = document.createElement("td");
        tdRel.textContent = l.rel || "-";

        tr.appendChild(tdType);
        tr.appendChild(tdAnchor);
        tr.appendChild(tdUrl);
        tr.appendChild(tdRel);
        tbody.appendChild(tr);
      });
    }

    fillRows(allLinks);
    table.appendChild(tbody);
    tableCard.appendChild(table);
    pane.appendChild(tableCard);

    searchBox.oninput = () => {
      const q = searchBox.value.toLowerCase();
      const filtered = allLinks.filter(l =>
        (l.url && l.url.toLowerCase().includes(q)) ||
        (l.anchor && l.anchor.toLowerCase().includes(q))
      );
      fillRows(filtered);
    };
  },

  // --- TAB 4: HÌNH ẢNH ---
  renderImages(images) {
    const pane = document.getElementById("tab-images");
    if (!pane) return;
    pane.innerHTML = "";

    if (!images || images.length === 0) {
      pane.innerHTML = "<p style='color:var(--text-muted);'>Không tìm thấy thẻ ảnh <img> nào trên trang.</p>";
      return;
    }

    const note = document.createElement("div");
    note.style.fontSize = "13px";
    note.style.color = "var(--text-muted)";
    note.style.marginBottom = "14px";
    note.textContent = `Tổng cộng: ${images.length} ảnh (Tải ảnh xem trước trực tiếp từ trình duyệt, referrerpolicy="no-referrer").`;
    pane.appendChild(note);

    const tableCard = document.createElement("div");
    tableCard.className = "card";
    tableCard.style.padding = "0";

    const table = document.createElement("table");
    table.className = "data-table";
    table.innerHTML = `
      <thead>
        <tr>
          <th>Xem trước</th>
          <th>Mô tả (Alt)</th>
          <th>Kích thước</th>
          <th>Đường dẫn (Src)</th>
        </tr>
      </thead>
    `;

    const tbody = document.createElement("tbody");
    images.forEach((img, idx) => {
      const tr = document.createElement("tr");

      // Cột Xem trước (30 ảnh đầu)
      const tdThumb = document.createElement("td");
      if (idx < 30 && img.src && !img.src.startsWith("data:")) {
        const thumb = document.createElement("img");
        thumb.src = img.src;
        thumb.referrerPolicy = "no-referrer";
        thumb.style.width = "40px";
        thumb.style.height = "40px";
        thumb.style.objectFit = "cover";
        thumb.style.borderRadius = "4px";
        thumb.style.background = "#e2e8f0";
        thumb.onerror = () => thumb.style.display = "none";
        tdThumb.appendChild(thumb);
      } else {
        tdThumb.textContent = "-";
      }

      // Cột Alt & Trạng thái
      const tdAlt = document.createElement("td");
      const altBadge = document.createElement("span");
      altBadge.className = `fix-badge badge-${img.alt_status === "ok" ? "pass" : (img.alt_status === "empty" ? "warn" : "fail")}`;
      altBadge.textContent = img.alt_status === "ok" ? "Có Alt" : (img.alt_status === "empty" ? "Alt Rỗng" : "Thiếu Alt");
      altBadge.style.marginRight = "6px";

      const altText = document.createElement("span");
      altText.textContent = img.alt || (img.alt_status === "empty" ? "(Ảnh trang trí)" : "(Không có)");

      tdAlt.appendChild(altBadge);
      tdAlt.appendChild(altText);

      // Cột kích thước & loading
      const tdDim = document.createElement("td");
      tdDim.textContent = `${img.width || "?"} × ${img.height || "?"} (${img.loading || "auto"})`;

      // Cột URL ảnh
      const tdSrc = document.createElement("td");
      const a = document.createElement("a");
      a.href = img.src;
      a.target = "_blank";
      a.rel = "noopener noreferrer nofollow";
      a.textContent = img.src.length > 50 ? img.src.slice(0, 50) + "..." : img.src;
      a.style.color = "var(--primary)";
      tdSrc.appendChild(a);

      tr.appendChild(tdThumb);
      tr.appendChild(tdAlt);
      tr.appendChild(tdDim);
      tr.appendChild(tdSrc);
      tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    tableCard.appendChild(table);
    pane.appendChild(tableCard);
  },

  // --- TAB 5: SCHEMA (JSON-LD) ---
  renderSchema(schemas) {
    const pane = document.getElementById("tab-schema");
    if (!pane) return;
    pane.innerHTML = "";

    if (!schemas || schemas.length === 0) {
      pane.innerHTML = "<p style='color:var(--text-muted);'>Không tìm thấy khối dữ liệu có cấu trúc JSON-LD nào trên trang.</p>";
      return;
    }

    schemas.forEach((s, idx) => {
      const card = document.createElement("div");
      card.className = "card";
      card.style.marginBottom = "14px";

      const header = document.createElement("div");
      header.style.display = "flex";
      header.style.justifyContent = "space-between";
      header.style.alignItems = "center";
      header.style.marginBottom = "8px";

      const typeTitle = document.createElement("strong");
      typeTitle.textContent = `Khối #${idx + 1}: ${(s.types || []).join(", ") || "Không rõ Type"}`;

      const validBadge = document.createElement("span");
      validBadge.className = `fix-badge badge-${s.valid ? "pass" : "fail"}`;
      validBadge.textContent = s.valid ? "JSON Hợp Lệ" : "Lỗi Cú Pháp";

      header.appendChild(typeTitle);
      header.appendChild(validBadge);
      card.appendChild(header);

      if (s.errors && s.errors.length > 0) {
        const errDiv = document.createElement("div");
        errDiv.style.color = "var(--color-red)";
        errDiv.style.fontSize = "13px";
        errDiv.style.marginBottom = "8px";
        errDiv.textContent = `Lỗi phát hiện: ${s.errors.join("; ")}`;
        card.appendChild(errDiv);
      }

      const toggleBtn = document.createElement("button");
      toggleBtn.className = "btn btn-secondary btn-sm";
      toggleBtn.textContent = "Xem mã nguồn JSON";

      const pre = document.createElement("pre");
      pre.style.display = "none";
      pre.style.marginTop = "10px";
      pre.style.padding = "10px";
      pre.style.background = "#f8fafc";
      pre.style.borderRadius = "6px";
      pre.style.fontSize = "12px";
      pre.style.overflowX = "auto";
      pre.textContent = s.raw_excerpt || "";

      toggleBtn.onclick = () => {
        const isHidden = pre.style.display === "none";
        pre.style.display = isHidden ? "block" : "none";
        toggleBtn.textContent = isHidden ? "Thu gọn mã nguồn" : "Xem mã nguồn JSON";
      };

      card.appendChild(toggleBtn);
      card.appendChild(pre);
      pane.appendChild(card);
    });
  },

  // --- TAB 6: MẠNG XÃ HỘI ---
  renderSocial(social) {
    const pane = document.getElementById("tab-social");
    if (!pane || !social) return;
    pane.innerHTML = "";

    const og = social.open_graph || {};
    const tw = social.twitter || {};

    // 1. Khung xem trước bài đăng Facebook / Zalo
    const previewWrapper = document.createElement("div");
    previewWrapper.innerHTML = `<h4 style="text-align:center;margin-bottom:12px;">Mô phỏng hiển thị khi chia sẻ:</h4>`;

    const card = document.createElement("div");
    card.className = "social-preview-card";

    if (og["og:image"]) {
      const img = document.createElement("img");
      img.className = "social-preview-img";
      img.src = og["og:image"];
      img.referrerPolicy = "no-referrer";
      img.onerror = () => img.style.display = "none";
      card.appendChild(img);
    }

    const body = document.createElement("div");
    body.className = "social-preview-body";

    const domain = document.createElement("div");
    domain.className = "social-preview-domain";
    domain.textContent = og["og:site_name"] || window.location.hostname;

    const title = document.createElement("div");
    title.className = "social-preview-title";
    title.textContent = og["og:title"] || "Tiêu đề bài viết";

    const desc = document.createElement("div");
    desc.className = "social-preview-desc";
    desc.textContent = og["og:description"] || "Mô tả ngắn của bài viết sẽ xuất hiện ở đây khi chia sẻ lên mạng xã hội.";

    body.appendChild(domain);
    body.appendChild(title);
    body.appendChild(desc);
    card.appendChild(body);
    previewWrapper.appendChild(card);

    const disclaimer = document.createElement("div");
    disclaimer.style.fontSize = "11.5px";
    disclaimer.style.color = "var(--text-muted)";
    disclaimer.style.textAlign = "center";
    disclaimer.style.marginBottom = "24px";
    disclaimer.textContent = "Chỉ mang tính minh hoạ; cách hiển thị thật do từng mạng xã hội quyết định.";
    previewWrapper.appendChild(disclaimer);

    pane.appendChild(previewWrapper);

    // 2. Bảng chi tiết thẻ Open Graph & Twitter
    const tableCard = document.createElement("div");
    tableCard.className = "card";
    tableCard.style.padding = "0";

    const table = document.createElement("table");
    table.className = "data-table";
    table.innerHTML = `
      <thead>
        <tr>
          <th>Thẻ Meta</th>
          <th>Giá trị</th>
        </tr>
      </thead>
    `;

    const tbody = document.createElement("tbody");
    const allSocial = { ...og, ...tw };

    Object.entries(allSocial).forEach(([k, v]) => {
      const tr = document.createElement("tr");
      const tdK = document.createElement("td");
      tdK.style.fontWeight = "600";
      tdK.style.width = "200px";
      tdK.textContent = k;

      const tdV = document.createElement("td");
      tdV.textContent = v;

      tr.appendChild(tdK);
      tr.appendChild(tdV);
      tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    tableCard.appendChild(table);
    pane.appendChild(tableCard);
  }
};
