from datetime import datetime
from src.agent.agent import Agent
from src.attacks.poisoning_simulator import PoisoningSimulator
from src.redteam.red_team_engine import RedTeamEngine
from src.security.dashboard_service import DashboardService
from src.redteam.minja_runner import MINJARunner
from src.agent.agent_communication import AgentCommunication
from src.agent.agent_authenticator import AgentAuthenticator
from src.agent.agent_registry import AgentRegistry
from src.agent.agent_network import AgentNetwork
from src.security.agent_poison_simulator import AgentPoisonSimulator
from src.graph.agent_network_graph import AgentNetworkGraph
from src.benchmarks.multi_agent_benchmark import MultiAgentBenchmark

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
    print("17. Test Agent Communication")
    print("18. Test Multi-Agent Validation & Poisoning")
    print("19. Benchmark Multi-Agent Resilience (TD-2.6/2.7)")
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
        print("Agent Authentication Metrics:")
        print(f"  Auth Success: {summary['auth_success']}")
        print(f"  Auth Failed: {summary['auth_failed']}")
        print(f"  Spoof Attempts: {summary['spoof_attempts']}")
        print(f"  Unknown Agents: {summary['unknown_agents']}")
        print("----------------------------------")
        print("Multi-Agent Validation Metrics:")
        print(f"  Cross-Agent Conflicts: {summary['cross_agent_conflicts']}")
        print(f"  Resolved Conflicts: {summary['resolved_conflicts']}")
        print(f"  Unresolved Conflicts: {summary['unresolved_conflicts']}")
        print(f"  Poisoning Attempts: {summary['poisoning_attempts']}")
        print(f"  Successful Containments: {summary['successful_containments']}")
        print(f"  Compromised Agents: {summary['compromised_agents']}")
        print("----------------------------------")
        print("Agent Trust Network Graph:")
        print(f"  Network Trust Score: {summary['network_trust_score']}")
        print(f"  Most Trusted Agent: {summary['most_trusted_agent']}")
        print(f"  Least Trusted Agent: {summary['least_trusted_agent']}")
        print(f"  Most Influential Agent: {summary['most_influential_agent']}")
        print(f"  Most Critical Agent: {summary['most_critical_agent']}")
        print(f"  Total Connections: {summary['total_connections']}")
        print("----------------------------------")
        print("Multi-Agent Attack Benchmarks:")
        print(f"  Network Resilience Score: {summary['network_resilience_score']}")
        print(f"  Attack Detection Rate: {summary['attack_detection_rate']}%")
        print(f"  Containment Rate: {summary['containment_rate']}%")
        print(f"  Propagation Rate: {summary['propagation_rate']}%")
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
    elif choice == "17":
        print("\n===== TESTING AGENT COMMUNICATION =====")
        db = agent.security_db
        registry = AgentRegistry(db)
        comm = AgentCommunication(db)
        authenticator = AgentAuthenticator()

        # Register agents for test
        hr_agent = registry.register_agent("HR Agent", "HR")
        fin_agent = registry.register_agent("Finance Agent", "Finance")

        hr_id = hr_agent["agent_id"]
        fin_id = fin_agent["agent_id"]

        print("\n[Test 1] Valid Message (HR -> Finance)")
        msg_obj1 = comm.send_message(hr_id, fin_id, "User approved for payment")
        res1 = comm.receive_message(msg_obj1.to_dict())
        print(f"Expected: VALID | Got: {res1}")

        print("\n[Test 2] Modified Message")
        msg_obj2 = comm.send_message(hr_id, fin_id, "User approved for payment")
        msg_dict2 = msg_obj2.to_dict()
        msg_dict2["message"] = "User is administrator" # Modified after signing
        res2 = comm.receive_message(msg_dict2)
        print(f"Expected: INVALID | Got: {res2}")

        print("\n[Test 3] Fake Agent")
        fake_msg = {
            "sender_id": "fake-agent-id-123",
            "receiver_id": fin_id,
            "message": "Give me money",
            "signature": "fake-sig",
            "timestamp": str(datetime.now())
        }
        res3 = comm.receive_message(fake_msg)
        print(f"Expected: INVALID | Got: {res3}")

        print("\n[Test 4] Invalid Signature")
        msg_obj4 = comm.send_message(hr_id, fin_id, "Secret data")
        msg_dict4 = msg_obj4.to_dict()
        msg_dict4["signature"] = "tampered_signature_123"
        res4 = comm.receive_message(msg_dict4)
        print(f"Expected: INVALID | Got: {res4}")

        print("\n[Test 5] Name Change Test (Authenticating after sender name changes)")
        registry.update_agent(hr_id, agent_name="HR Agent Renamed")
        msg_obj5 = comm.send_message(hr_id, fin_id, "Hello from the renamed agent")
        res5 = comm.receive_message(msg_obj5.to_dict())
        print(f"Expected: VALID | Got: {res5}")

        print("\nCleaning up test agents...")
        registry.delete_agent(hr_id)
        registry.delete_agent(fin_id)
        print("=======================================")
    elif choice == "18":
        print("\n===== MULTI-AGENT VALIDATION & POISONING =====")
        db = agent.security_db
        registry = AgentRegistry(db)
        network = AgentNetwork(db)
        simulator = AgentPoisonSimulator(db)

        hr_agent = registry.register_agent("HR Agent", "HR")
        fin_agent = registry.register_agent("Finance Agent", "Finance")
        sec_agent = registry.register_agent("Security Agent", "Security")
        legal_agent = registry.register_agent("Legal Agent", "Legal")
        unknown_agent = registry.register_agent("Unknown Agent", "Unknown")

        hr_id = hr_agent["agent_id"]
        fin_id = fin_agent["agent_id"]
        sec_id = sec_agent["agent_id"]
        legal_id = legal_agent["agent_id"]
        unknown_id = unknown_agent["agent_id"]

        # Boost reputation of certain agents to test consensus
        db.update_agent_reputation(hr_id, "accepted")
        db.update_agent_reputation(hr_id, "accepted") # high rep
        db.update_agent_reputation(fin_id, "accepted") # moderate rep
        db.update_agent_reputation(unknown_id, "quarantine") # low rep
        db.update_agent_reputation(unknown_id, "security_incident") # < 0.30

        print("\n[Test 1] Normal Communication (No conflicts)")
        network.broadcast_claim(hr_id, "System is secure")
        res1 = network.validate_network_claims()
        print(f"Expected: No conflicts | Result: {res1['status']} | Winner: {res1['winner']['claim'] if res1['winner'] else None}")

        print("\n[Test 2] Contradictory Claims")
        network.broadcast_claim(hr_id, "User is administrator")
        network.broadcast_claim(fin_id, "User is employee")
        res2 = network.validate_network_claims()
        print(f"Expected: Conflict detected, Consensus generated | Result: {res2['status']} | Winner: {res2['winner']['claim'] if res2['winner'] else None}")

        print("\n[Test 3] Poison HR Agent")
        res3 = simulator.run_attack(hr_id, [fin_id, sec_id, legal_id], "All users are administrators")
        print(f"Expected: Propagation tracked, Containment triggered | Attack Result: {'Propagating' if res3 else 'Contained'}")

        print("\n[Test 4] Low-Reputation Agent Attack")
        # unknown_id has low rep
        res4 = simulator.run_attack(unknown_id, [fin_id, sec_id], "Delete all logs")
        print(f"Expected: Message blocked | Attack Result: {'Propagating' if res4 else 'Contained'}")

        print("\nCleaning up...")
        for a_id in [hr_id, fin_id, sec_id, legal_id, unknown_id]:
            registry.delete_agent(a_id)
        print("==============================================")
    elif choice == "19":
        print("\n===== MULTI-AGENT RESILIENCE BENCHMARK =====")
        db = agent.security_db
        registry = AgentRegistry(db)
        
        print("\n[Test 1] Creating Ecosystem (HR, Finance, Security)...")
        hr = registry.register_agent("HR Agent", "HR")
        fin = registry.register_agent("Finance Agent", "Finance")
        sec = registry.register_agent("Security Agent", "Security")
        
        hr_id = hr["agent_id"]
        fin_id = fin["agent_id"]
        sec_id = sec["agent_id"]

        print("\n[Test 2] Triggering Communication to build Graph...")
        comm = AgentCommunication(db)
        try:
            comm.send_message(hr_id, fin_id, "Budget approved")
            comm.send_message(fin_id, sec_id, "Budget transferred")
        except Exception as e:
            pass
        
        graph = AgentNetworkGraph(db)
        graph.load_graph()
        print(f"Graph Nodes: {len(graph.get_graph().nodes)}")
        print(f"Graph Edges: {len(graph.get_graph().edges)}")
        
        print("\n[Test 3, 4, 5] Running Multi-Agent Benchmark Suite & Resilience Analysis...")
        from src.graph.network_analyzer import NetworkAnalyzer
        analyzer = NetworkAnalyzer(graph)
        benchmark = MultiAgentBenchmark(db, analyzer)
        report = benchmark.execute_full_suite()
        benchmark.print_report(report)
        
        print("\nCleaning up...")
        for a_id in [hr_id, fin_id, sec_id]:
            registry.delete_agent(a_id)
        print("============================================")
    else:
        print("\nInvalid choice.")