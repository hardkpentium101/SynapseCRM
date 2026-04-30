#!/usr/bin/env python3
"""
Standalone Orchestrator Demo - Run this to test the agent
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.main import HCPAgent
from src.agent.llm_manager import get_llm_manager


def run_demo():
    """Run orchestrator demo with sample queries"""

    print("=" * 60)
    print("HCP Agent - Orchestrator Demo")
    print("=" * 60)

    # Initialize agent
    print("\n1. Initializing agent...")
    llm = get_llm_manager()
    agent = HCPAgent(llm)
    print("   ✓ Agent initialized")

    # Sample queries to test
    queries = [
        "Find Dr. Sharma",
        "Add Dr. Test Doctor from Stanford, cardiologist",
        "I met with Dr. Priya Sharma today",
        "Set follow-up to call Dr. Priya Sharma next week",
    ]

    session_id = "demo-session"

    print(f"\n2. Running {len(queries)} test queries...\n")

    for i, query in enumerate(queries, 1):
        print(f"--- Query {i}: {query}")
        print("-" * 40)

        try:
            response = agent.process(
                user_input=query, session_id=session_id, user_id="demo_user"
            )

            print(f"Intent: {response.intent}")
            print(f"Entities: {response.entities}")
            print(f"Message: {response.message}")
            print(f"Success: {response.success}")
            if response.error:
                print(f"Error: {response.error}")

        except Exception as e:
            print(f"❌ Error: {e}")

        print()

    print("=" * 60)
    print("Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    run_demo()

    from src.agent.langsmith.tracing import wait_for_all_tracers
    wait_for_all_tracers()
