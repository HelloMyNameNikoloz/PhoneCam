window.PhoneCamState = {
  data: {
    devices: [],
    settings: {
      cameraFacing: "back",
      resolution: "1920x1080",
      fps: 30,
      selectedDeviceId: null,
    },
    cameraRunning: false,
    virtualCameraInstalled: false,
    frameReceiver: {
      listening: false,
      framesReceived: 0,
      lastSize: null,
      postUrl: "http://127.0.0.1:4767/frame",
    },
    status: "waiting",
    activePanel: "camera",
    error: null,
    missingAdb: false,
    missingCompanionApk: false,
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
