window.PhoneCamState = {
  data: {
    devices: [],
    settings: {
      cameraFacing: "back",
      resolution: "1920x1080",
      fps: 30,
      alwaysOnTop: false,
      selectedDeviceId: null,
    },
    cameraRunning: false,
    status: "waiting",
    activePanel: "camera",
    error: null,
    missingAdb: false,
    missingScrcpy: false,
    logs: [],
  },

  merge(payload) {
    this.data = {
      ...this.data,
      ...payload,
      settings: { ...this.data.settings, ...(payload.settings || {}) },
    };
  },
};
