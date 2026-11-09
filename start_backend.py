import os
import sys
import subprocess

def main():
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
    sys.path.insert(0, backend_dir)
    os.chdir(backend_dir)
    os.environ["PYTHONPATH"] = backend_dir

    print("=" * 60)
    print("Starting ClearBorder AI Backend (FastAPI)...")
    print("API Base URL: http://127.0.0.1:8000")
    print("API Docs:     http://127.0.0.1:8000/docs")
    print("=" * 60)

    import uvicorn
    from app.main import app
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main()
