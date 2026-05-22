window.PhoneCamControls = {
  bind() {
    document.addEventListener("click", (event) => this.handleClick(event));
    ["device-select", "camera-facing", "resolution", "fps", "show-preview"]
      .forEach((id) => document.querySelector(`#${id}`).addEventListener("change", () => this.saveSettings()));
  },

  collectSettings() {
    return {
      selectedDeviceId: document.querySelector("#device-select").value || null,
      cameraFacing: document.querySelector("#camera-facing").value,
      resolution: document.querySelector("#resolution").value,
      fps: Number(document.querySelector("#fps").value),
      transportMode: "jpeg",
      showPreview: document.querySelector("#show-preview").checked,
    };
  },

  setPanel(panel) {
    window.PhoneCamState.merge({ activePanel: panel });
    window.PhoneCamRender.render();
    this.refreshIfIdle();
  },

  async saveSettings() {
    const result = await window.PhoneCamApi.saveSettings(this.collectSettings());
    window.PhoneCamState.merge({ settings: result });
    await this.refreshIfIdle();
    window.PhoneCamRender.render();
  },

  async refreshIfIdle() {
    if (window.PhoneCamState.data.cameraRunning) return;
    const status = await window.PhoneCamApi.getStatus();
    window.PhoneCamState.merge(status);
  },

  handleClick(event) {
    const tab = event.target.closest(".mode-tab");
    if (tab) this.setPanel(tab.dataset.panel);
    const start = event.target.closest("#start-camera");
    if (start) this.startCamera();
    const stop = event.target.closest("#stop-camera");
    if (stop) this.stopCamera();
    const repair = event.target.closest("#repair-camera");
    if (repair) this.repairVirtualCamera();
    const register = event.target.closest("#register-camera");
    if (register) this.registerVirtualCamera();
    const unregister = event.target.closest("#unregister-camera");
    if (unregister) this.unregisterVirtualCamera();
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

  async repairVirtualCamera() {
    const status = await window.PhoneCamApi.repairVirtualCamera();
    window.PhoneCamState.merge(status);
    window.PhoneCamRender.render();
  },

  async registerVirtualCamera() {
    const status = await window.PhoneCamApi.registerVirtualCamera();
    window.PhoneCamState.merge(status);
    window.PhoneCamRender.render();
  },

  async unregisterVirtualCamera() {
    const status = await window.PhoneCamApi.unregisterVirtualCamera();
    window.PhoneCamState.merge(status);
    window.PhoneCamRender.render();
  },
};
