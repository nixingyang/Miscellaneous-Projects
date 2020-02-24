### Workaround of issues in Visual Studio Code

#### Disable the Preview feature
```plaintext
# https://stackoverflow.com/a/38723094
"workbench.editor.enablePreview": false
"workbench.editor.enablePreviewFromQuickOpen": false
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
