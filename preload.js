const { contextBridge, ipcRenderer } = require("electron");

// exposing some APIs to renderer
contextBridge.exposeInMainWorld("electronAPI", {
  // exposing python script run
  runPythonScript: (jsonFilePath) =>
    ipcRenderer.invoke("run-python-script", jsonFilePath),

  // exposing fs module called from main.js
  writeJsonFile: (filePath, data) =>
    ipcRenderer.invoke("write-json-file", filePath, data),

  // exposing node variable called in main.js
  getDirname: () => ipcRenderer.invoke("get-dirname"),
});
