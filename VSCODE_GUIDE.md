# 🎥 VS Code: Watch & Run Everything Guide

## Option 1: VS Code Tasks (Recommended)

### Step 1: Create Tasks Configuration

VS Code → Terminal → Configure Tasks → Create tasks.json

Create `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Run Analysis Pipeline",
      "type": "shell",
      "command": "python",
      "args": ["run_analysis.py"],
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": true,
        "panel": "shared"
      },
      "group": {
        "kind": "build",
        "isDefault": true
      }
    },
    {
      "label": "Start Backend API",
      "type": "shell",
      "command": "python",
      "args": ["-m", "uvicorn", "backend.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"],
      "cwd": "${workspaceFolder}",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
      },
      "isBackground": true,
      "problemMatcher": {
        "pattern": {
          "regexp": "^.*$",
          "file": 1,
          "location": 2,
          "message": 3
        },
        "background": {
          "activeOnStart": true,
          "beginsPattern": "^.*Uvicorn running.*",
          "endsPattern": "^.*Application startup complete.*"
        }
      }
    },
    {
      "label": "Start Frontend UI",
      "type": "shell",
      "command": "streamlit",
      "args": ["run", "frontend/app.py"],
      "cwd": "${workspaceFolder}",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "new"
      },
      "isBackground": true
    },
    {
      "label": "Run Tests",
      "type": "shell",
      "command": "python",
      "args": ["test_api.py"],
      "cwd": "${workspaceFolder}",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": true,
        "panel": "shared"
      }
    },
    {
      "label": "Start All Services (Docker)",
      "type": "shell",
      "command": "docker-compose",
      "args": ["up", "-d"],
      "cwd": "${workspaceFolder}",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": true,
        "panel": "shared"
      }
    },
    {
      "label": "Stop All Services (Docker)",
      "type": "shell",
      "command": "docker-compose",
      "args": ["down"],
      "cwd": "${workspaceFolder}",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": true,
        "panel": "shared"
      }
    }
  ]
}
```

### Step 2: Run Tasks from VS Code

**Method 1: Command Palette**
```
Ctrl+Shift+P → Tasks: Run Task → Select task name
```

**Method 2: Terminal Menu**
```
Terminal → Run Task → Select task name
```

**Quick Shortcuts:**
```
Ctrl+Shift+B → Run default task (Analysis Pipeline)
```

---

## Option 2: VS Code Launch Configurations (Debugging)

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Analysis",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/run_analysis.py",
      "console": "integratedTerminal",
      "justMyCode": true,
      "cwd": "${workspaceFolder}"
    },
    {
      "name": "Debug Backend API",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["backend.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"],
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}"
    },
    {
      "name": "Debug Frontend",
      "type": "python",
      "request": "launch",
      "module": "streamlit",
      "args": ["run", "frontend/app.py"],
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}"
    }
  ]
}
```

**How to use:**
1. Click on Run & Debug (Ctrl+Shift+D)
2. Select configuration from dropdown
3. Click green play button or press F5

---

## Option 3: Run Everything at Once (My Recommended Workflow)

Create compound task in `.vscode/tasks.json`:

```json
{
  "label": "Run Everything",
  "dependsOn": [
    "Start Backend API",
    "Start Frontend UI"
  ],
  "group": {
    "kind": "test",
    "isDefault": true
  }
}
```

Then:
```
Ctrl+Shift+P → Tasks: Run Task → Run Everything
```

This runs both backend and frontend simultaneously!

---

## Option 4: Watch Files & Auto-Reload

Create a file watcher extension integration. Add to `.vscode/settings.json`:

```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.python"
  },
  "files.autoSave": "afterDelay",
  "files.autoSaveDelay": 1000
}
```

**Install Extensions:**
1. Python (Microsoft) - for debugging
2. Pylance - for code analysis
3. Thunder Client - for API testing

---

## 🎯 Complete Workflow in VS Code

### Step 1: Open Project
```
File → Open Folder → Select Survival-Analysis-plus-COX-model
```

### Step 2: Open Terminal
```
Ctrl+` (backtick) or Terminal → New Terminal
```

### Step 3: Run Analysis (One-time setup)
```
Ctrl+Shift+P → Tasks: Run Task → Run Analysis Pipeline
```

Wait for completion (~3-5 minutes)

### Step 4: Start Services
```
Ctrl+Shift+P → Tasks: Run Task → Run Everything
```

This opens 2 terminal panels:
- **Panel 1**: Backend API (port 8000)
- **Panel 2**: Frontend UI (port 8501)

### Step 5: Test While Coding

Open Thunder Client (VS Code extension):
```
View → Thunder Client → Create Request
```

```
POST http://localhost:8000/predict
Content-Type: application/json

{
  "time": 55,
  "sex": 1,
  "chest_pain_type": 0,
  "resting_bp": 130,
  "cholesterol": 230,
  "fasting_bs": 0,
  "resting_ecg": 1,
  "max_hr": 140,
  "exercise_angina": 0,
  "oldpeak": 0.5,
  "st_slope": 2
}
```

---

## 🔄 Live Reload While Editing

### Backend (FastAPI)
- Uses `--reload` flag automatically
- Watches `backend/main.py` for changes
- Auto-restarts server

### Frontend (Streamlit)
- Auto-reloads on file changes
- Just save file, UI updates instantly

### Your Code Changes
1. Edit `backend/main.py` → API restarts automatically
2. Edit `frontend/app.py` → UI refreshes automatically
3. Switch to browser/UI to see changes

---

## 📊 View Everything in Split Panel

### Layout 1: Code + 2 Terminals
```
Ctrl+B (toggle sidebar)
Ctrl+J (maximize terminal)
```

Then split terminals:
```
Click "+" in terminal tab → New Terminal
```

### Layout 2: Code + Browser
```
View → Command Palette → "Simple Browser"
Simple Browser: Open URL → http://localhost:8501
```

Shows browser inside VS Code!

---

## 🧪 Testing While Running

### Option A: Thunder Client (In VS Code)
See above - test API directly

### Option B: Run Tests
```
Ctrl+Shift+P → Tasks: Run Task → Run Tests
```

### Option C: Python Debugger
Set breakpoint in code:
```python
# Click left of line number to set breakpoint
cox_model = joblib.load(MODEL_PATH)  # ← Click here
```

Then:
```
F5 to start debugging → Step through code
```

---

## 📁 Recommended VS Code Layout

### Split View Setup:
```
┌─────────────────────────────────────┐
│  Code Editor (backend/main.py)      │
├──────────────┬──────────────────────┤
│ File Tree    │  Terminal 1 (API)    │
│ Outline      │  Terminal 2 (UI)     │
└──────────────┴──────────────────────┘
```

**How to achieve:**
1. Open file: `backend/main.py`
2. Split editor right: `Ctrl+\`
3. Open terminal: `Ctrl+J`
4. Split terminal: Click "+" button

---

## 🚀 Quick Commands Cheatsheet

```
Ctrl+`          → Toggle Terminal
Ctrl+Shift+D    → Open Debug View
Ctrl+Shift+P    → Command Palette
Ctrl+K Ctrl+W   → Close editor
Ctrl+\          → Split Editor
F5              → Start Debugging
F10             → Step Over
F11             → Step Into
Shift+F5        → Stop Debugging
Ctrl+Shift+B    → Run Build Task
Ctrl+Shift+T    → Reopen Closed Tab
```

---

## ⚙️ Advanced: Run Everything in One Command

Create PowerShell script `.vscode/run-all.ps1`:

```powershell
# Start all services in separate terminals

# Terminal 1: Run analysis (one-time)
Write-Host "Starting analysis pipeline..."
python run_analysis.py

# Wait for completion
Write-Host "Waiting for analysis to complete..."
Start-Sleep -Seconds 5

# Terminal 2: Start backend
Write-Host "Starting backend API..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000"

# Terminal 3: Start frontend
Write-Host "Starting frontend UI..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "streamlit run frontend/app.py"

Write-Host "All services started!"
Write-Host "Backend: http://localhost:8000"
Write-Host "Frontend: http://localhost:8501"
```

Then from VS Code terminal:
```
& .\.vscode\run-all.ps1
```

---

## 📝 VS Code Extensions Recommended

Install these for better experience:

1. **Python** (Microsoft) - Debugging, linting
2. **Pylance** - Smart code analysis
3. **Thunder Client** - API testing
4. **REST Client** - Another API testing option
5. **Docker** (Microsoft) - Docker management
6. **GitLens** - Git integration
7. **Code Runner** - Run code snippets

Install from:
```
Extensions (Ctrl+Shift+X) → Search → Install
```

---

## 🎯 Complete Setup (Copy-Paste Ready)

### Create all config files at once:

1. Create folder: `.vscode`
2. Add `tasks.json` (from above)
3. Add `launch.json` (from above)
4. Add `settings.json` (from above)

```bash
mkdir .vscode
# Copy JSON files from above into .vscode/
```

Then you're ready:
```
Ctrl+Shift+P → Tasks: Run Task → Run Everything
```

---

## ✅ Final Verification

After setup, you should see:

```
✅ Analysis runs (python run_analysis.py)
✅ Backend starts (http://localhost:8000)
✅ Frontend loads (http://localhost:8501)
✅ Can edit code and see changes live
✅ Can debug with breakpoints
✅ Can test API from Thunder Client
```

All visible in VS Code! 🎉

---

## 💡 Pro Tips

1. **Use Integrated Terminal** - Don't use external terminal
2. **Set Breakpoints** - Click left of line number
3. **Watch Variables** - Debug panel shows values
4. **Use Tasks** - Don't remember commands
5. **Split View** - See code + output simultaneously
6. **Auto-save** - Enable in settings

---

**Everything is now in VS Code. No need to switch windows!** 🚀
