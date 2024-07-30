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
    "cf_proj.exe"
  );

  try {
    // run the .exe
    process = execFile(pythonExecutablePath, [jsonFilePath]);

    // Send stdout data to the renderer process (standard output)
    process.stdout.on("data", (data) => {
      event.sender.send("python-log", data.toString());
    });

    // Send stderr data to the renderer process (standard error)
    process.stderr.on("data", (data) => {
      event.sender.send("python-log", data.toString());
    });

    // Return a promise that resolves/rejects based on the process exit code
    return new Promise((resolve, reject) => {
      process.on("close", (code) => {
        if (code === 0) {
          resolve({ success: true });
        } else {
          reject(new Error(`Python script exited with code ${code}`));
        }
      });
    });
  } catch (error) {
    console.error("Error executing Python script:", error);
    // Send back a simplified error object
    return { success: false, error: error.message };
  }
});

// Function to write JSON file (using fs module)
ipcMain.handle("write-json-file", (event, filePath, data) => {
  fs.writeFileSync(filePath, data);
  return { success: true };
});

// Function to get directory name
ipcMain.handle("get-dirname", () => {
  return __dirname;
});
