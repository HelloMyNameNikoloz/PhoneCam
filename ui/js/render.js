window.PhoneCamRender = {
  render() {
    const state = window.PhoneCamState.data;
    this.statusPill(state);
    this.deviceOptions(state);
    this.formValues(state.settings);
    this.cards(state);
    this.preview(state);
    this.emptyState(state);
    this.logs(state.logs);
  },

  statusPill(state) {
    const pill = document.querySelector("#status-pill");
    const labels = { waiting: "Waiting", connected: "Connected", running: "Running", error: "Error" };
    pill.className = `status-pill ${state.status}`;
    pill.textContent = labels[state.status] || "Waiting";
  },

  deviceOptions(state) {
    const select = document.querySelector("#device-select");
    const selected = state.settings.selectedDeviceId || "";
    select.innerHTML = "";
    const fallback = new Option("Auto select device", "");
    select.appendChild(fallback);
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
    document.querySelector("#auto-start").checked = Boolean(settings.autoStart);
    document.querySelector("#always-on-top").checked = Boolean(settings.alwaysOnTop);
    document.querySelector("#stability-mode").checked = Boolean(settings.stabilityMode);
  },

  cards(state) {
    document.querySelector("#device-card").innerHTML = this.deviceCard(state);
    document.querySelector("#camera-card").innerHTML = this.cameraCard(state);
    document.querySelector("#obs-card").innerHTML = this.obsCard(state);
  },

  deviceCard(state) {
    const device = this.selectedDevice(state);
    const status = device ? device.status : "No device";
    const detail = this.deviceMessage(state, device);
    const badge = device && device.status === "device" ? "success" : device ? "warning" : "error";
    return `<div class="card-body">
      <h3>Device</h3>
      <span class="badge ${badge}">${status}</span>
      <p>${detail}</p>
      <div class="metric"><span>Selected</span><strong>${device ? device.id : "Auto"}</strong></div>
    </div>`;
  },

  cameraCard(state) {
    const running = state.cameraRunning;
    const settings = state.settings;
    return `<div class="card-body">
      <h3>Camera</h3>
      <span class="badge ${running ? "success" : "warning"}">${running ? "Running" : "Stopped"}</span>
      <p>${running ? "PhoneCam Preview is open and ready for capture." : "Start the camera when your phone is connected."}</p>
      <div class="metric"><span>Mode</span><strong>${settings.cameraFacing} / ${settings.resolution} / ${settings.fps} FPS</strong></div>
    </div>`;
  },

  obsCard(state) {
    const ready = state.cameraRunning;
    return `<div class="card-body">
      <h3>${ready ? "OBS Ready" : "OBS"}</h3>
      <span class="badge ${ready ? "success" : ""}">${ready ? "Preview active" : "Window Capture"}</span>
      <p>${ready ? "Preview active - capture 'PhoneCam Preview' in OBS." : "This build appears in OBS Window Capture, not Video Capture Device. Add a Window Capture source and select 'PhoneCam Preview'."}</p>
      <button id="copy-obs" class="button ghost" type="button">Copy OBS setup steps</button>
    </div>`;
  },

  preview(state) {
    const panel = document.querySelector("#preview-card");
    const running = state.cameraRunning;
    panel.className = `preview-card ${running ? "running" : ""}`;
    panel.innerHTML = `<div>
      <h2>Preview</h2>
      <p>${running ? "PhoneCam Preview is running automatically." : "Connect and authorize a phone. Auto Start will open PhoneCam Preview."}</p>
    </div>
    <div class="preview-frame" aria-label="Preview status">
      <span class="preview-dot"></span>
    </div>
    <span class="badge ${running ? "success" : "warning"}">${running ? "Capture PhoneCam Preview" : "Waiting for camera"}</span>`;
  },

  selectedDevice(state) {
    const selected = state.settings.selectedDeviceId;
    return state.devices.find((d) => d.id === selected) || state.devices[0] || null;
  },

  deviceMessage(state, device) {
    if (state.missingAdb) return "Bundled adb.exe was not found in the bin folder.";
    if (state.missingScrcpy) return "Bundled scrcpy.exe was not found in the bin folder.";
    if (state.error) return state.error;
    if (!device) return "Connect your Android phone with USB.";
    if (device.status === "unauthorized") return "Unlock your phone and accept the USB debugging prompt.";
    if (device.status === "offline") return "Reconnect the cable or switch USB mode to Transferring images / PTP or Charging only.";
    return "Authorized Android device connected.";
  },

  emptyState(state) {
    document.querySelector("#empty-state").classList.toggle("hidden", state.devices.length > 0 || state.missingAdb);
  },

  logs(logs) {
    const panel = document.querySelector("#log-panel");
    panel.innerHTML = logs.map((entry) => `<div class="log-line ${entry.level}">
      <span>${entry.time}</span><span>${entry.level}</span><span>${entry.message}</span>
    </div>`).join("");
    panel.scrollTop = panel.scrollHeight;
  },
};
