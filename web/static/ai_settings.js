/**
 * web/static/ai_settings.js - Quản lý cấu hình & kết nối AI riêng của người dùng (F10).
 * Nguyên tắc bảo mật:
 * - Mặc định lưu sessionStorage (mất khi đóng tab).
 * - Tích chọn "Nhớ key" mới lưu localStorage.
 * - Key không bao giờ lưu trên máy chủ ngoài các lệnh gọi API qua HTTPS header X-AI-Key.
 */

const AIConfig = {
  STORAGE_KEY: "taio_seo_ai_key",
  STORAGE_PROVIDER: "taio_seo_ai_provider",
  STORAGE_MODEL: "taio_seo_ai_model",
  STORAGE_ENDPOINT: "taio_seo_ai_endpoint",
  STORAGE_REMEMBER: "taio_seo_ai_remember",

  getKey() {
    return sessionStorage.getItem(this.STORAGE_KEY) || localStorage.getItem(this.STORAGE_KEY) || "";
  },

  getProvider() {
    return sessionStorage.getItem(this.STORAGE_PROVIDER) || localStorage.getItem(this.STORAGE_PROVIDER) || "openai";
  },

  getModel() {
    return sessionStorage.getItem(this.STORAGE_MODEL) || localStorage.getItem(this.STORAGE_MODEL) || "";
  },

  getEndpoint() {
    return sessionStorage.getItem(this.STORAGE_ENDPOINT) || localStorage.getItem(this.STORAGE_ENDPOINT) || "";
  },

  saveSettings(provider, key, model, endpoint, remember) {
    const storage = remember ? localStorage : sessionStorage;
    const otherStorage = remember ? sessionStorage : localStorage;

    // Xoá từ storage còn lại để tránh xung đột
    otherStorage.removeItem(this.STORAGE_KEY);
    otherStorage.removeItem(this.STORAGE_PROVIDER);
    otherStorage.removeItem(this.STORAGE_MODEL);
    otherStorage.removeItem(this.STORAGE_ENDPOINT);
    localStorage.setItem(this.STORAGE_REMEMBER, remember ? "1" : "0");

    if (key) {
      storage.setItem(this.STORAGE_KEY, key);
    } else {
      storage.removeItem(this.STORAGE_KEY);
    }
    storage.setItem(this.STORAGE_PROVIDER, provider);
    storage.setItem(this.STORAGE_MODEL, model || "");
    storage.setItem(this.STORAGE_ENDPOINT, endpoint || "");

    this.updateStatusPill();
  },

  clearKey() {
    sessionStorage.removeItem(this.STORAGE_KEY);
    localStorage.removeItem(this.STORAGE_KEY);
    this.updateStatusPill();
  },

  hasKey() {
    return Boolean(this.getKey());
  },

  updateStatusPill() {
    const pill = document.getElementById("ai-status-pill");
    const dot = document.getElementById("ai-status-dot");
    const text = document.getElementById("ai-status-text");
    if (!pill || !dot || !text) return;

    if (this.hasKey()) {
      dot.classList.add("active");
      text.textContent = `AI: ${this.getProvider()}`;
    } else {
      dot.classList.remove("active");
      text.textContent = "Kết nối AI (tuỳ chọn)";
    }
  }
};

// Khởi tạo Modal cài đặt AI
function initAISettingsModal(providers, localMode) {
  const modal = document.getElementById("ai-modal");
  const openBtn = document.getElementById("ai-status-pill");
  const closeBtn = document.getElementById("ai-modal-close");
  const cancelBtn = document.getElementById("ai-modal-cancel");
  const saveBtn = document.getElementById("ai-modal-save");
  const testBtn = document.getElementById("ai-modal-test");
  const testResult = document.getElementById("ai-test-result");

  const providerSelect = document.getElementById("ai-provider-select");
  const keyInput = document.getElementById("ai-key-input");
  const modelInput = document.getElementById("ai-model-input");
  const endpointGroup = document.getElementById("ai-endpoint-group");
  const endpointInput = document.getElementById("ai-endpoint-input");
  const rememberCheckbox = document.getElementById("ai-remember-key");

  // Nạp danh sách providers vào select
  providerSelect.innerHTML = "";
  providers.forEach(p => {
    const opt = document.createElement("option");
    opt.value = p.id;
    opt.textContent = p.label;
    providerSelect.appendChild(opt);
  });

  function syncFormWithProvider() {
    const curId = providerSelect.value;
    const p = providers.find(it => it.id === curId);
    if (!p) return;

    if (!modelInput.value || modelInput.getAttribute("data-auto") === "1") {
      modelInput.value = p.default_model;
      modelInput.setAttribute("data-auto", "1");
    }

    if (p.base_url_editable || localMode) {
      endpointGroup.style.display = "block";
      if (!endpointInput.value) {
        endpointInput.value = p.default_endpoint || "";
      }
    } else {
      endpointGroup.style.display = "none";
      endpointInput.value = "";
    }
  }

  providerSelect.addEventListener("change", () => {
    modelInput.removeAttribute("data-auto");
    syncFormWithProvider();
  });

  function openModal() {
    providerSelect.value = AIConfig.getProvider();
    keyInput.value = AIConfig.getKey();
    modelInput.value = AIConfig.getModel();
    endpointInput.value = AIConfig.getEndpoint();
    rememberCheckbox.checked = localStorage.getItem(AIConfig.STORAGE_REMEMBER) === "1";
    testResult.textContent = "";
    syncFormWithProvider();
    modal.classList.add("active");
  }

  function closeModal() {
    modal.classList.remove("active");
  }

  if (openBtn) openBtn.addEventListener("click", openModal);
  if (closeBtn) closeBtn.addEventListener("click", closeModal);
  if (cancelBtn) cancelBtn.addEventListener("click", closeModal);

  if (saveBtn) {
    saveBtn.addEventListener("click", () => {
      AIConfig.saveSettings(
        providerSelect.value,
        keyInput.value.trim(),
        modelInput.value.trim(),
        endpointInput.value.trim(),
        rememberCheckbox.checked
      );
      closeModal();
    });
  }

  if (testBtn) {
    testBtn.addEventListener("click", async () => {
      testResult.textContent = "Đang kiểm tra kết nối...";
      testResult.style.color = "var(--text-muted)";

      const key = keyInput.value.trim();
      const provider = providerSelect.value;
      const model = modelInput.value.trim();
      const endpoint = endpointInput.value.trim();

      if (!key) {
        testResult.textContent = "Vui lòng nhập API Key để thử kết nối.";
        testResult.style.color = "var(--color-red)";
        return;
      }

      try {
        const resp = await fetch("/api/ai/test", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-AI-Key": key
          },
          body: JSON.stringify({
            provider: provider,
            model: model,
            base_url: endpoint
          })
        });

        const data = await resp.json();
        if (resp.ok && data.ok) {
          testResult.textContent = `Kết nối thành công (${data.latency_ms} ms)!`;
          testResult.style.color = "var(--color-green)";
        } else {
          testResult.textContent = data.error || "Kết nối thất bại. Vui lòng kiểm tra lại Key.";
          testResult.style.color = "var(--color-red)";
        }
      } catch (err) {
        testResult.textContent = `Lỗi mạng: ${err.message}`;
        testResult.style.color = "var(--color-red)";
      }
    });
  }
}
