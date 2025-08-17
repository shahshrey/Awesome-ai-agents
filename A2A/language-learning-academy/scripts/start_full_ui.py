#!/usr/bin/env python3
import asyncio
import subprocess
import sys
import time
import webbrowser

import httpx


async def check_agent_health():
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get('http://localhost:9999/.well-known/agent-card.json')
            return response.status_code == 200
    except:
        return False

def main():
    print("🎓 Language Learning Academy - Full UI Launcher")
    print("=" * 60)

    print("📋 Starting services...")

    print("1️⃣ Starting Language Learning Academy Agent...")
    agent_process = subprocess.Popen(
        ['uv', 'run', 'python', '-m', 'language_learning_academy.server.main'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd='src'
    )

    print("⏳ Waiting for agent to start...")
    for i in range(30):
        time.sleep(1)
        if asyncio.run(check_agent_health()):
            print("✅ Agent is ready!")
            break
        print(f"   Checking... ({i+1}/30)")
    else:
        print("❌ Agent failed to start!")
        agent_process.terminate()
        sys.exit(1)

    print("2️⃣ Starting Streamlit Web UI...")
    streamlit_process = subprocess.Popen([
        'uv', 'run', 'python', '-m', 'streamlit', 'run', 'src/language_learning_academy/ui/streamlit_app.py',
        '--server.port', '8501',
        '--server.headless', 'true'
    ])

    print("⏳ Waiting for UI to start...")
    time.sleep(5)

    print("🌐 Opening web browser...")
    webbrowser.open('http://localhost:8501')

    print("\n" + "=" * 60)
    print("🎉 Language Learning Academy is now running!")
    print("📊 Agent API: http://localhost:9999")
    print("🎨 Web UI: http://localhost:8501")
    print("=" * 60)
    print("Press Ctrl+C to stop all services")

    try:
        agent_process.wait()
        streamlit_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        agent_process.terminate()
        streamlit_process.terminate()
        print("✅ All services stopped!")

if __name__ == "__main__":
    main()
