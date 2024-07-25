const { app, BrowserWindow, ipcMain } = require("electron");
const { execFile } = require("child_process");
const path = require("path");
const fs = require("fs");

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      enableRemoteModule: false,
    },
  });

  mainWindow.loadFile(path.join(__dirname, "public", "index.html"));
}

app.whenReady().then(createWindow);

// function to run python executable
ipcMain.handle("run-python-script", async (event, jsonFilePath) => {
  // get the python .exe path
  const pythonExecutablePath = path.join(
    __dirname,
    "scripts",
    "dist",
    "generate_excel.exe"
  );

  try {
    // run the .exe
    const { stdout, stderr } = await execFile(pythonExecutablePath, [
      jsonFilePath,
    ]);

    // Use JSON parse/stringify to clone and strip non-cloneable parts
    return JSON.parse(JSON.stringify({ success: true, output: stdout }));
  } catch (error) {
    console.error("Error executing Python script:", error);
    // Send back a simplified error object
    return { success: false, error: error.message };
  }
});

ipcMain.handle("write-json-file", (event, filePath, data) => {
  fs.writeFileSync(filePath, data);
  return { success: true };
});

ipcMain.handle("get-dirname", () => {
  return __dirname;
});
