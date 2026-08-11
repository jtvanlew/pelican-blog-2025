Auto-activate Conda environment in this workspace
===============================================

This workspace enables automatic activation of Python virtual environments (including Conda) when you open the integrated terminal.

What was added
- `.vscode/settings.json` — settings that enable environment activation and recommend defaults.
- `.vscode/extensions.json` — recommends the Python and Pylance extensions.

If VS Code doesn't pick the correct Conda interpreter automatically, you can pin it by setting `python.defaultInterpreterPath` in workspace settings. Example (PowerShell/Windows):

```
"python.defaultInterpreterPath": "C:\\Users\\<you>\\anaconda3\\envs\\myenv\\python.exe"
```

Notes:
- Make sure `conda` is on your PATH or set `python.condaPath` to the full conda executable.
- You can also select the interpreter from the Command Palette: `Python: Select Interpreter`.

Pelican quick commands
----------------------

Here are the Pelican commands I use for this project. Put these in a terminal opened from this workspace (the integrated Anaconda Prompt profile will try to activate your conda install):

Build the site locally (development settings):

```powershell
pelican content -s pelicanconf.py -t themes/clean-blog -o output
```

Build and serve with an automatic reload (development):

```powershell
pelican content -s pelicanconf.py -t themes/clean-blog -o output -l -r
```

If you prefer the invoke tasks included in this repo (they wrap pelican + rsync):

```powershell
# Start the livereload development server (requires 'invoke' package)
invoke livereload

# Build and publish using the repo's publish task (uses publishconf.py + rsync)
invoke publish
```

Publish manually (production settings):

```powershell
pelican content -s publishconf.py -t themes/clean-blog -o output
rsync -avz --delete output/ your_ssh_user@your_host:/path/to/site
```

Notes:
- `-l`/`--listen` opens a local web server on port 8000.
- `-r`/`--autoreload` watches for changes and rebuilds automatically.
- Replace `your_ssh_user@your_host:/path/to/site` with your real deploy target if you run rsync.
