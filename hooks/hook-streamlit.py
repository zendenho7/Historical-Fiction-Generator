from PyInstaller.utils.hooks import copy_metadata, collect_data_files, collect_submodules

datas = copy_metadata('streamlit')
datas += collect_data_files('streamlit')
hiddenimports = collect_submodules('streamlit')
