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
    receiver: {
      active: false,
      framesReceived: 0,
      frameAgeMs: null,
      obsUrl: "http://127.0.0.1:4767/obs",
      streamUrl: "http://127.0.0.1:4767/stream.mjpg",
      postUrl: "http://127.0.0.1:4767/frame",
    },
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
