document.getElementById("run-script").addEventListener("click", () => {
    // Consulta la pestaña activa
    chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
      if (tabs.length === 0) return;
      const tabId = tabs[0].id;
      
      // Envía un mensaje al content script
      chrome.tabs.sendMessage(tabId, { action: "RUN_MARKER_PROCESS" });
    });
  });
  