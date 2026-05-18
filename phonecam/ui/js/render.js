window.PhoneCamRender = {
  render() {
    const state = window.PhoneCamState.data;
    this.statusPill(state);
    this.panels(state);
    this.deviceOptions(state);
    this.formValues(state.settings);
    this.sourceCard(state);
    this.setupMessage(state);
    this.stage(state);
    this.logs(state.logs);
  },

  statusPill(state) {
    const pill = document.querySelector("#status-pill");
    const labels = { waiting: "Waiting", connected: "Connected", running: "Live", error: "Needs attention" };
    pill.className = `status-pill ${state.status}`;
    pill.textContent = labels[state.status] || "Waiting";
  },

  panels(state) {
    document.querySelectorAll(".mode-tab").forEach((tab) => {
      tab.classList.toggle("active", tab.dataset.panel === state.activePanel);
    });
    document.querySelectorAll(".side-panel").forEach((panel) => {
      panel.classList.toggle("active", panel.dataset.panelView === state.activePanel);
    });
  },

  deviceOptions(state) {
    const select = document.querySelector("#device-select");
    const selected = state.settings.selectedDeviceId || "";
    select.innerHTML = "";
    select.appendChild(new Option("Auto select", ""));
    state.devices.forEach((device) => {
      const label = `${device.label} - ${device.id} (${device.status})`;
      select.appendChild(new Option(label, device.id));
    });
    select.value = selected;
  },

  formValues(settings) {
    document.querySelector("#camera-facing").value = settings.cameraFacing;
    document.querySelector("#resolution").value = settings.resolution;
    document.querySelector("#fps").value = String(settings.fps);
    document.querySelector("#always-on-top").checked = Boolean(settings.alwaysOnTop);
  },

  sourceCard(state) {
    const device = this.selectedDevice(state);
    const status = device ? device.status : "No device";
    const badge = device && device.status === "device" ? "success" : device ? "warning" : "error";
    document.querySelector("#source-card").innerHTML = `<div class="source-summary">
      <div class="source-top">
        <div>
          <h2>${device ? device.label : "No phone connected"}</h2>
          <div class="source-id">${device ? device.id : "Waiting for USB"}</div>
        </div>
        <span class="badge ${badge}">${status}</span>
      </div>
      <p>${this.deviceMessage(state, device)}</p>
    </div>`;
  },

  setupMessage(state) {
    const device = this.selectedDevice(state);
    document.querySelector("#setup-message").textContent = this.deviceMessage(state, device);
  },

  stage(state) {
    const settings = state.settings;
    const running = state.cameraRunning;
    const subtitle = running ? "PhoneCam Preview is running automatically." : this.previewHint(state);
    document.querySelector("#stage-subtitle").textContent = subtitle;
    document.querySelector("#stage-metrics").innerHTML = [
      `<span class="badge accent">${this.resolutionLabel(settings.resolution)}</span>`,
      `<span class="badge accent">${settings.fps} FPS</span>`,
      `<span class="badge accent">${settings.cameraFacing}</span>`,
    ].join("");

    document.querySelector("#preview-card").innerHTML = `<div class="viewer-card ${running ? "running" : ""}">
      <div class="camera-glyph" aria-hidden="true"></div>
      <div class="viewer-text">
        <h2>${running ? "Preview active" : "Ready when your phone is"}</h2>
        <p>${running ? "PhoneCam will keep this stream alive until you quit the app." : "Connect and authorize a phone. PhoneCam starts the camera automatically."}</p>
      </div>
    </div>
    <div class="stage-toast">${this.deviceMessage(state, this.selectedDevice(state))}</div>`;
  },

  resolutionLabel(resolution) {
    const labels = {
      "1280x720": "720p",
      "1920x1080": "1080p",
      "2560x1440": "2K",
      "3840x2160": "4K",
    };
    return labels[resolution] || resolution;
  },

  previewHint(state) {
    if (state.missingAdb) return "adb.exe is missing from the bundled bin folder.";
    if (state.missingScrcpy) return "scrcpy.exe is missing from the bundled bin folder.";
    if (state.devices.some((d) => d.status === "device")) return "Phone connected. Starting camera automatically.";
    return "Waiting for an authorized Android phone.";
  },

  selectedDevice(state) {
    const selected = state.settings.selectedDeviceId;
    return state.devices.find((device) => device.id === selected) || state.devices[0] || null;
  },

  deviceMessage(state, device) {
    if (state.missingAdb) return "Bundled adb.exe was not found in the bin folder.";
    if (state.missingScrcpy) return "Bundled scrcpy.exe was not found in the bin folder.";
    if (state.error) return state.error;
    if (!device) return "Connect your Android phone with USB and accept the debugging prompt.";
    if (device.status === "unauthorized") return "Unlock your phone and accept the USB debugging prompt.";
    if (device.status === "offline") return "Reconnect the cable or switch USB mode to Transferring images / PTP or Charging only.";
    return "Authorized Android device connected.";
  },

  logs(logs) {
    const panel = document.querySelector("#log-panel");
    panel.innerHTML = logs.map((entry) => `<div class="log-line ${entry.level}">
      <span>${entry.time}</span><span>${entry.level}</span><span>${entry.message}</span>
    </div>`).join("");
    panel.scrollTop = panel.scrollHeight;
  },
};
