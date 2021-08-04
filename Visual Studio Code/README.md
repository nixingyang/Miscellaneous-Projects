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
    "debug.console.fontFamily": "'Noto Sans'",
    "editor.fontFamily": "'Noto Sans'",
    "editor.formatOnSave": true,
    "explorer.confirmDelete": false,
    "latex-workshop.docker.enabled": true,
    "latex-workshop.docker.image.latex": "texlive/texlive:TL2020-historic",
    "latex-workshop.latex.autoClean.run": "onBuilt",
    "python.condaPath": "/home/ni/.miniconda/bin/conda",
    "python.defaultInterpreterPath": "/home/ni/.miniconda/envs/TensorFlow2.2/bin/python",
    "python.formatting.provider": "yapf",
    "python.formatting.yapfArgs": [
        "--style=google"
    ],
    "python.formatting.yapfPath": "/home/ni/.miniconda/envs/TensorFlow2.2/bin/yapf",
    "python.linting.pylintArgs": [
        "--generated-members=cv2.*"
    ],
    "python.showStartPage": false,
    "security.workspace.trust.enabled": false,
    "telemetry.enableCrashReporter": false,
    "telemetry.enableTelemetry": false,
    "terminal.integrated.fontFamily": "'Noto Sans Mono'",
    "workbench.colorTheme": "Default Light+",
    "workbench.editor.enablePreview": false,
    "workbench.editor.enablePreviewFromQuickOpen": false,
    "workbench.editor.untitled.hint": "hidden",
    "workbench.editorAssociations": {
        "*.ipynb": "jupyter-notebook",
        "*.pdf": "default"
    },
    "workbench.startupEditor": "none",
}
```
