# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata, collect_data_files, collect_submodules

# ---- Collect critical data and metadata ----
streamlit_metadata = copy_metadata('streamlit')
streamlit_datas = collect_data_files('streamlit')
streamlit_hiddenimports = collect_submodules('streamlit')

# ---- Other hidden imports for dependencies ----
additional_hiddenimports = [
    'google.generativeai',
    'google.ai.generativelanguage',
    'google.api_core',
    'altair',
    'plotly',
    'pydeck',
    'validators',
    'watchdog',
    'tornado',
    'PIL',
    'PIL._imagingtk',
    'pyarrow',  # Include this if you use it
    'streamlit.runtime.scriptrunner.magic_funcs',
    'streamlit.runtime.state',
    'streamlit.components.v1',
    'streamlit.web.cli',
]

# ---- Main Analysis ----
a = Analysis(
    ['run_app.py'],
    pathex=[],
    binaries=[],
    datas=(
        streamlit_metadata + streamlit_datas + [
            ('.streamlit', '.streamlit'),   # Streamlit config folder (must exist in project root)
            ('.env', '.'),                  # Your API key/config file
            ('config.py', '.'),             # Project config
            ('ai_client.py', '.'),          # Gemini/OpenAI client
            ('stateful_generator.py', '.'), # State management logic
            ('prompt_grammar.py', '.'),     # Grammar-driven prompt module
            ('app.py', '.'),                # Main Streamlit application (critical!)
        ]
    ),
    hiddenimports=streamlit_hiddenimports + additional_hiddenimports,
    hookspath=['./hooks'],       # In case you have a hook-streamlit.py, good for metadata!
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

# ---- PyInstaller build steps ----
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='HistoricalFictionGenerator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='HistoricalFictionGenerator',
)
