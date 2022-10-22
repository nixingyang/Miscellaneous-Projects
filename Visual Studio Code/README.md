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
cat ~/.config/Code\ -\ OSS/User/settings.json
{
    "debug.console.fontFamily": "Noto Sans",
    "diffEditor.ignoreTrimWhitespace": false,
    "editor.fontFamily": "Noto Sans",
    "editor.formatOnSave": true,
    "extensions.ignoreRecommendations": true,
    "latex-workshop.docker.enabled": true,
    "latex-workshop.docker.image.latex": "texlive/texlive:latest",
    "latex-workshop.latex.autoClean.run": "onBuilt",
    "security.workspace.trust.enabled": false,
    "telemetry.telemetryLevel": "off",
    "terminal.integrated.fontFamily": "Noto Sans Mono",
    "window.zoomLevel": 2,
    "workbench.colorTheme": "Default Light+",
    "workbench.editor.enablePreview": false,
    "workbench.startupEditor": "none",
}
```
