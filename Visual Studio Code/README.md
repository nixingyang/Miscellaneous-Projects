### Workaround of issues in Visual Studio Code

#### Disable the Preview feature
```plaintext
# https://stackoverflow.com/a/38723094
"workbench.editor.enablePreview": false
"workbench.editor.enablePreviewFromQuickOpen": false
```

#### Import TensorFlow
```plaintext
# https://github.com/microsoft/python-language-server/issues/818
# https://github.com/tensorflow/tensorflow/issues/32982#issuecomment-545414061
mkdir ~/.local/dummy-site-packages
ln -s ~/.miniconda3/envs/TensorFlow/lib/python3.7/site-packages/tensorflow_core ~/.local/dummy-site-packages/tensorflow
"python.autoComplete.extraPaths": ["/home/xingyang/.local/dummy-site-packages"]
```

#### Breakpoint in file excluded by filters
```plaintext
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
```plaintext
cat ~/.config/Code\ -\ OSS/User/settings.json
{
    "telemetry.enableCrashReporter": false,
    "telemetry.enableTelemetry": false,
    "workbench.colorTheme": "Default Light+",
    "workbench.startupEditor": "newUntitledFile",
    "terminal.integrated.inheritEnv": false,
    "editor.fontFamily": "'Noto Sans'",
    "terminal.integrated.fontFamily": "'Noto Sans Mono'",
    "python.formatting.provider": "yapf",
    "python.formatting.yapfArgs": [
        "--style=google"
    ],
    "editor.formatOnSave": true,
    "python.formatting.yapfPath": "/home/xingyang/.miniconda3/envs/TensorFlow/bin/yapf",
    "python.autoComplete.extraPaths": [
        "/home/xingyang/.local/dummy-site-packages"
    ],
    "debug.console.fontFamily": "'Noto Sans'",
    "workbench.editor.enablePreviewFromQuickOpen": false,
    "workbench.editor.enablePreview": false,
    "explorer.confirmDelete": false
}
```
