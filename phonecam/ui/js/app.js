async function bootPhoneCam() {
  window.PhoneCamControls.bind();
  const settings = await window.PhoneCamApi.loadSettings();
  window.PhoneCamState.merge({ settings });
  await refreshStatus();
  setInterval(refreshStatus, 1000);
}

async function refreshStatus() {
  const status = await window.PhoneCamApi.getStatus();
  window.PhoneCamState.merge(status);
  window.PhoneCamRender.render();
}

window.addEventListener("pywebviewready", bootPhoneCam);
window.addEventListener("DOMContentLoaded", () => {
  setTimeout(() => {
    if (!window.pywebview) {
      window.PhoneCamRender.render();
    }
  }, 500);
});
