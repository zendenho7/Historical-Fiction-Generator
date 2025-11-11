import sys
import os
import webbrowser
import time
from pathlib import Path
import socket
import traceback

def find_free_port(start_port=8501):
    """Find a free port starting from start_port"""
    port = start_port
    while port < start_port + 100:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            port += 1
    return start_port

if getattr(sys, 'frozen', False):
    application_path = Path(sys.executable).parent
else:
    application_path = Path(__file__).parent

sys.path.insert(0, str(application_path))

# Set Streamlit configuration/environment variables
os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'false'
os.environ['STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION'] = 'false'
os.environ['STREAMLIT_GLOBAL_DEVELOPMENT_MODE'] = 'false'
os.environ['STREAMLIT_SERVER_ENABLE_STATIC_SERVING'] = 'true'

print("="*60)
print("📚 Historical Fiction Generator")
print("="*60)
print("\n🚀 Starting Streamlit server...\n")

port = find_free_port(8501)
print(f"📡 Using port: {port}")

url = f"http://localhost:{port}"

def wait_exit():
    print("\nPress Enter to exit...")
    input()
    sys.exit(1)

if __name__ == "__main__":
    try:
        app_path = str(application_path / "_internal" / "app.py")
        # Check that app.py exists
        if not os.path.exists(app_path):
            print(f"❌ Error: app.py not found at {app_path}")
            wait_exit()

        from streamlit.web import cli as stcli

        sys.argv = [
            "streamlit", "run", app_path,
            f"--server.port={port}",
            "--server.headless=true",
            "--browser.gatherUsageStats=false",
            "--server.enableCORS=false",
            "--server.enableXsrfProtection=false",
        ]

        print(f"\n✅ Server starting at: {url}")
        print("\n🌐 Opening browser in 2 seconds...")
        print("\n" + "="*60)
        print("📋 INSTRUCTIONS:")
        print("   - Browser will open automatically")
        print("   - Configure parameters in the sidebar")
        print("   - Click 'Generate Chronology' to create content")
        print("   - Press Ctrl+C in this window to stop the server")
        print("="*60 + "\n")

        def open_browser():
            time.sleep(2)
            try:
                webbrowser.open(url)
            except Exception as e:
                print(f"⚠️ Could not open browser automatically: {e}")
                print(f"Please open manually: {url}")

        import threading
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()

        sys.exit(stcli.main())
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        wait_exit()
    except Exception as e:
        print(f"\n❌ Error starting server: {e}\n")
        traceback.print_exc()
        wait_exit()
