from src.core.orchestrator.agent_loader import load_agents
def launch():
    print("[BOOT] Launching kOS orchestrator...")
    load_agents()
    return 0
