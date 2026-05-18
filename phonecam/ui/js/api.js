window.PhoneCamApi = {
  async call(name, ...args) {
    if (!window.pywebview || !window.pywebview.api) {
      return { status: "error", error: "Python bridge is not ready" };
    }
    return window.pywebview.api[name](...args);
  },

  getStatus() {
    return this.call("get_status");
  },

  refreshDevices() {
    return this.call("refresh_devices");
  },

  startCamera(settings) {
    return this.call("start_camera", settings);
  },

  stopCamera() {
    return this.call("stop_camera");
  },

  saveSettings(settings) {
    return this.call("save_settings", settings);
  },

  loadSettings() {
    return this.call("load_settings");
  },
};
