### Workaround of issues in Visual Studio Code

#### Set VS Code as the default text editor
```bash
xdg-mime default visual-studio-code.desktop text/plain
```

#### Breakpoint in file excluded by filters
```bash
cat .vscode/launch.json
{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "justMyCode": false
        }
    ]
}
```

#### User/settings.json
```bash
cat ~/.config/Code/User/settings.json
{
    "python.formatting.provider": "yapf",
    "python.formatting.yapfArgs": [
        "--style=google"
    ],
    "python.formatting.yapfPath": "/home/ni/.miniconda/envs/TensorFlow2.2/bin/yapf",
    "telemetry.enableCrashReporter": false,
    "telemetry.enableTelemetry": false,
    "workbench.colorTheme": "Default Light+",
    "workbench.editor.enablePreview": false,
    "workbench.editor.enablePreviewFromQuickOpen": false,
    "workbench.startupEditor": "none",
    "workbench.editorAssociations": [
        {
            "viewType": "jupyter.notebook.ipynb",
            "filenamePattern": "*.ipynb"
        }
    ],
    "editor.formatOnSave": true,
    "python.linting.pylintArgs": [
        "--generated-members=cv2.*"
    ],
    "python.condaPath": "/home/ni/.miniconda/bin/conda",
    "editor.fontFamily": "'Noto Sans'",
    "debug.console.fontFamily": "'Noto Sans'",
    "terminal.integrated.fontFamily": "'Noto Sans Mono'",
    "explorer.confirmDelete": false,
}
```
