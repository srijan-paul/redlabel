# Building Windows Executable from macOS

Since you're on macOS but need a Windows executable, here are your options:

## Option 1: GitHub Actions (Recommended ⭐)

**Steps:**
1. Push your code to GitHub
2. Go to the "Actions" tab in your GitHub repo  
3. Click "Build Windows Executable" workflow
4. Click "Run workflow" button
5. Wait ~5 minutes for build to complete
6. Download the zip file from "Artifacts" section
7. Send the zip to your friend

**Advantages:**
- Free (GitHub Actions)
- No local setup needed
- Always builds on clean Windows environment
- Automatic - just click and wait

## Option 2: Wine + Windows Python (Advanced)

**Setup (one-time):**
```bash
# Install Wine via Homebrew
brew install --cask xquartz
brew install wine-stable

# Download and install Windows Python in Wine
wget https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe
wine python-3.11.0-amd64.exe

# Install dependencies in Wine Python
wine python -m pip install PyQt5 lxml pyinstaller
```

**Build:**
```bash
wine python -m PyInstaller redlabel.spec
```

## Option 3: Docker with Wine

**Setup:**
```bash
# Create Dockerfile
cat > Dockerfile.windows << 'EOF'
FROM scottyhardy/docker-wine:latest
RUN wine pip install PyQt5 lxml pyinstaller
COPY . /app
WORKDIR /app
RUN wine python -m PyInstaller redlabel.spec
EOF

# Build
docker build -f Dockerfile.windows -t redlabel-windows .
docker run --rm -v $(pwd)/dist:/app/dist redlabel-windows
```

## Option 4: Windows VM/Remote

- Use Parallels/VMware with Windows
- Use a cloud Windows instance (AWS/Azure)
- Ask a friend with Windows to run the build

## Recommended Workflow

**Use GitHub Actions:**

1. **First time setup:**
   ```bash
   git add .
   git commit -m "Add Windows build workflow"
   git push
   ```

2. **Every time you want to build:**
   - Go to GitHub → Actions tab
   - Click "Run workflow"
   - Download artifact when done

3. **Give to friend:**
   - Download the zip from GitHub Actions
   - Send zip to friend
   - Friend extracts and double-clicks RedLabel.exe

This is the easiest and most reliable method!
