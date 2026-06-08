from datetime import datetime
from src.agent.agent import Agent
from src.attacks.poisoning_simulator import PoisoningSimulator
from src.redteam.red_team_engine import RedTeamEngine
from src.security.dashboard_service import DashboardService
from src.redteam.minja_runner import MINJARunner
agent = Agent()
simulator = PoisoningSimulator(agent)
redteam = RedTeamEngine(agent)
minja = MINJARunner(agent)
print("\n=== DigiFortress ===")
while True:
    print("\n1. Remember")
    print("2. Ask")
    print("3. View Memory")
    print("4. Analytics")
    print("5. Security Dashboard")
    print("6. Run Attack Simulation")
    print("8. Source Reputations")
    print("9. Security Events")
    print("10. Run Red Team Test")
    print("11. View Red Team Results")
    print("12. Knowledge Graph Neighbors")
    print("13. Memory Security Overview (Dashboard)")
    print("14. Session Analytics")
    print("15. Audit Query (Counterfactual)")
    print("16. Run MINJA Benchmark")
    print("7. Exit")
    choice = input("\nChoice: ")
    if choice == "1":
        print("\nEnter memory (press Enter on an empty line to submit):")
        lines = []
        while True:
            try:
                line = input()
                if not line:
                    break
                lines.append(line)
            except EOFError:
                break
        if lines:
            for line in lines:
                if line.strip():
                    print(f"\nProcessing memory: '{line}'")
                    result = agent.remember(line)
                    print(f"Status: {result['status']}")
                    if result.get("memory_id"):
                        print(f"Memory ID: {result['memory_id']}")
        else:
            print("No memory entered.")
    elif choice == "2":
        question = input("\nAsk: ")
        response = agent.ask(question)
        print(f"\nAgent: {response}")
    elif choice == "3":
        memories = (agent.memory.get_all_memories())
        documents = memories["documents"]
        if not documents:
            print("\nNo memories stored.")
        else:
            print("\nStored Memories:\n")
            for memory in documents:
                print(f"- {memory}")
    elif choice == "4":
        analytics = (agent.security_db.get_memory_analytics())
        if not analytics:
            print("\nNo analytics available.")
        else:
            print("\n===== MEMORY ANALYTICS =====")
            for row in analytics:
                print("\n----------------------------")
                print(f"Memory: {row[0]}")
                print(f"Trust Score: {row[1]}")
                print(f"Access Count: {row[2]}")
                print(f"Reputation: {row[3]}")
                print(f"Last Accessed: {row[4]}")
    elif choice == "5":
        metrics = (agent.security_db.get_all_metrics())
        metric_dict = {}
        for metric in metrics:
            metric_dict[metric[0]] = metric[1]
        accepted = metric_dict.get("accepted",0)
        conflict = metric_dict.get("conflict",0)
        quarantined = metric_dict.get("quarantined",0)
        attacks = metric_dict.get("attack_attempts",0)
        if attacks > 0:
            defense_rate = ((conflict+quarantined)/attacks)*100
        else:
            defense_rate = 0
        print("\n===============================")
        print("DIGIFORTRESS SECURITY DASHBOARD")
        print("===============================")
        print(f"\nAccepted Memories: {accepted}")
        print(f"Conflicts Detected: {conflict}")
        print(f"Quarantined Memories: {quarantined}")
        print(f"Attack Attempts: {attacks}")
        print(f"Defense Success Rate: {defense_rate:.2f}%")
    elif choice == "6":
        simulator.run_source_reputation_test()
    elif choice == "7":
        print("\nExiting DigiFortress...")
        agent.security_db.close()
        break
    elif choice == "8":
        sources = (
            agent.security_db.get_all_sources()
        )
        print("\n===== SOURCE REPUTATIONS =====")
        for source in sources:
            print(f"\nSource: {source[0]}")
            print(f"Reputation: {source[1]}")
            print(f"Accepted: {source[2]}")
            print(f"Conflict: {source[3]}")
            print(f"Quarantined: {source[4]}")
    elif choice == "9":
        events = agent.security_db.get_security_events()
        print("\n===== SECURITY EVENTS =====")
        for event in events:
            print("\n-----------------------")
            print(f"Event ID: {event[0]}")
            print(f"Type: {event[1]}")
            print(f"Memory: {event[2]}")
            print(f"Source: {event[3]}")
            print(f"Status: {event[4]}")
            print(f"Risk Score: {event[5]}")
            print(f"Risk Level: {event[6]}")
            print(f"Time: {event[7]}")
    elif choice == "10":
        redteam.run()
    elif choice == "11":
        results = agent.security_db.get_red_team_res()
        print("\n===== RED TEAM RESULTS =====")
        for result in results:
            print("\n--------------------------")
            print(f"Test ID: {result[0]}")
            print(f"Timestamp: {result[1]}")
            print(f"Total Attacks: {result[2]}")
            print(f"Blocked: {result[3]}")
            print(f"Missed: {result[4]}")
            print(f"Detection Rate: {result[5]:.2f}%")
            print(f"Security Score: {result[6]:.2f}%")
    elif choice == "12":
        node = input("\nNode: ")
        neighbors = (agent.graph.get_neighbors(node))
        print("\nConnected Nodes:")
        for n in neighbors:
            print(f"- {n}")
    elif choice == "13":
        dashboard = DashboardService(agent.security_db)
        summary = dashboard.get_summary()
        print("\n==================================")
        print("MEMORY SECURITY OVERVIEW")
        print("==================================")
        print(f"Accepted Memories: {summary['accepted']}")
        print(f"Conflicts: {summary['conflict']}")
        print(f"Quarantined: {summary['quarantined']}")
        print("----------------------------------")
        print(f"Average Trust Score: {summary['avg_trust']:.2f}")
        print(f"Average Risk Score: {summary['avg_risk']:.2f}")
        print("----------------------------------")
        print(f"Security Score: {summary['security_score']:.2f}%")
        print("----------------------------------")
        print("Top Threat Sources:")
        if not summary['top_threat_sources']:
            print("  No sources registered yet.")
        for source_name, rep in summary['top_threat_sources']:
            print(f"  - {source_name}: {rep:.2f}")
        print("----------------------------------")
        print("Recent Security Events:")
        if not summary['recent_events']:
            print("  No events logged yet.")
        for event in summary['recent_events']:
            print(f"  - [{event[7]}] {event[1]} | Status: {event[4]} | Risk: {event[5]:.1f} ({event[6]})")
            content_truncated = event[2][:60] + "..." if len(event[2]) > 60 else event[2]
            print(f"    Memory: \"{content_truncated}\"")
        print("==================================")
    elif choice == "14":
        session_id = agent.session_manager.get_session_id()
        writes = agent.security_db.get_session_write_count(session_id)
        risk_score = agent.session_risk_engine.calculate_risk(writes)
        
        print("\n===== SESSION ANALYTICS =====")
        print(f"Session ID: {session_id}")
        print(f"Writes: {writes}")
        timestamps = agent.security_db.get_session_timestamps(session_id)
        burst_detected = agent.burst_detector.detect_burst(timestamps)
        if burst_detected:
            risk_score = min(risk_score + 0.3, 1.0)
            agent.security_db.log_security_event(
                event_type="MINJA_BURST_DETECTED",
                memory_content="Session Burst Activity",
                source=session_id,
                status="suspicious",
                risk_score=risk_score,
                risk_level="HIGH",
                timestamp=str(datetime.now())
            )
        risk_level = agent.session_risk_engine.get_risk_level(risk_score)
        print(f"Burst Detected: {burst_detected}")
        print(f"Risk Score: {risk_score}")
        print(f"Risk Level: {risk_level}")
        print("\nRecent Timestamps:")
        for ts in timestamps:
            print(f"- {ts}")
        print("\n=============================")
    elif choice == "15":
        query = input("Query: ")
        results = agent.audit_query(query)
        print("\n===== AUDIT RESULTS =====")
        print(f"Normal Response: {results['normal_response']}")
        print(f"Counterfactual Response: {results['counterfactual_response']}")
        print(f"Divergence: {results['divergence']:.2f}")
        print(f"Judgment Divergence: {results['judgment_divergence']}")
        print(f"Normal Judgment: {results['normal_judgment']}")
        print(f"Counterfactual Judgment: {results['counterfactual_judgment']}")
        print(f"Influence Score: {results['influence_score']:.2f}")
        print(f"Influence Level: {results['influence_level']}")
        print("\n=========================")
    elif choice == "16":
        minja.run()
    else:
        print("\nInvalid choice.")