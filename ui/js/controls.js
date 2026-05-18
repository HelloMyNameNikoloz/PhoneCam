window.PhoneCamControls = {
  bind() {
    document.querySelector("#start-camera").addEventListener("click", () => this.startCamera());
    document.querySelector("#stop-camera").addEventListener("click", () => this.stopCamera());
    document.querySelector("#refresh-devices").addEventListener("click", () => this.refreshDevices());
    document.addEventListener("click", (event) => this.handleClick(event));

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

  setPanel(panel) {
    window.PhoneCamState.merge({ activePanel: panel });
    window.PhoneCamRender.render();
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

  handleClick(event) {
    const tab = event.target.closest(".mode-tab");
    if (tab) this.setPanel(tab.dataset.panel);
    if (event.target.closest("#viewer-start")) this.startCamera();
    if (event.target.closest("#viewer-stop")) this.stopCamera();
  },
};
