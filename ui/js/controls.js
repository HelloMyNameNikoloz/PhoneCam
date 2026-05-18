window.PhoneCamControls = {
  bind() {
    document.querySelector("#start-camera").addEventListener("click", () => this.startCamera());
    document.querySelector("#stop-camera").addEventListener("click", () => this.stopCamera());
    document.querySelector("#refresh-devices").addEventListener("click", () => this.refreshDevices());
    document.addEventListener("click", (event) => this.handleDynamicClick(event));

    ["device-select", "camera-facing", "resolution", "fps", "auto-start", "always-on-top", "stability-mode"]
      .forEach((id) => document.querySelector(`#${id}`).addEventListener("change", () => this.saveSettings()));
  },

  collectSettings() {
    const stability = document.querySelector("#stability-mode").checked;
    return {
      selectedDeviceId: document.querySelector("#device-select").value || null,
      cameraFacing: stability ? "back" : document.querySelector("#camera-facing").value,
      resolution: stability ? "1920x1080" : document.querySelector("#resolution").value,
      fps: stability ? 30 : Number(document.querySelector("#fps").value),
      autoStart: document.querySelector("#auto-start").checked,
      alwaysOnTop: document.querySelector("#always-on-top").checked,
      stabilityMode: stability,
    };
  },

  async saveSettings() {
    const result = await window.PhoneCamApi.saveSettings(this.collectSettings());
    window.PhoneCamState.merge({ settings: result });
    window.PhoneCamRender.render();
  },

  async startCamera() {
    const status = await window.PhoneCamApi.startCamera(this.collectSettings());
    window.PhoneCamState.merge(status);
    window.PhoneCamRender.render();
  },

  async stopCamera() {
    const status = await window.PhoneCamApi.stopCamera();
    window.PhoneCamState.merge(status);
    window.PhoneCamRender.render();
  },

  async refreshDevices() {
    const status = await window.PhoneCamApi.refreshDevices();
    window.PhoneCamState.merge(status);
    window.PhoneCamRender.render();
  },

  handleDynamicClick(event) {
    if (!event.target.closest("#copy-obs")) return;
    const text = [
      "Open OBS.",
      "Add a Window Capture source, not Video Capture Device.",
      "Select PhoneCam Preview.",
      "Use your external microphone as a separate audio source.",
    ].join("\n");
    navigator.clipboard.writeText(text).catch(() => {});
  },
};
