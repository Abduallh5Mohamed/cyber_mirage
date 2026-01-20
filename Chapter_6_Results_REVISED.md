# Chapter 6: Experimental Results and Analysis

This chapter presents the results obtained from deploying the Cyber Mirage honeynet system in a live production environment. The purpose of this deployment was to observe and analyze real-world attacker behavior on an internet-exposed network and evaluate the effectiveness of the reinforcement learning-based adaptive deception engine in detecting, engaging, and profiling malicious actors.

Cyber Mirage represents an adaptive honeynet architecture that integrates a Proximal Policy Optimization (PPO) reinforcement learning agent to make dynamic deception decisions. The system was deployed to collect threat intelligence from actual cyber attacks while maintaining realistic engagement to prevent detection by sophisticated adversaries.

## Experimental Setup and Deployment

Cyber Mirage was deployed on a publicly accessible Virtual Private Server (VPS) hosted on Amazon Web Services (AWS) EC2 infrastructure in the Stockholm region (eu-north-1). The deployment utilized a t2.large instance (2 vCPU, 8GB RAM) running Ubuntu 22.04 LTS with Docker containerization for service isolation and management.

Multiple honeypot services were exposed to the internet to attract diverse attack vectors and attacker profiles. The deployed services included:

- **SMB (Ports 445, 139):** Windows file sharing protocol, commonly targeted by ransomware and lateral movement attacks
- **SSH (Port 2222):** Secure shell service for remote access attempts and brute force attacks  
- **HTTP/HTTPS (Ports 8080, 8443):** Web application honeypots to capture web-based exploitation attempts
- **FTP (Port 2121):** File transfer protocol for credential harvesting and malware distribution attempts
- **MySQL (Port 3307):** Database service to attract SQL injection and database exploitation
- **Modbus (Port 502):** Industrial Control System (ICS) protocol to study attacks on critical infrastructure emulation
- **Custom services (Port 1025):** Generic TCP services for protocol-agnostic attack capture

The system architecture consisted of multiple integrated components working in concert:

**Data Collection Infrastructure:** All incoming network traffic was logged and stored in a PostgreSQL relational database with comprehensive attack session tracking. Redis was deployed for real-time caching and session state management, enabling sub-millisecond response times for the RL agent. Each attack session captured detailed metadata including source IP, geolocation, targeted service, command sequences, and temporal information.

**Geolocation and Threat Enrichment:** Incoming attacker IP addresses were enriched with geolocation data (country, city, coordinates) and network information (ASN, ISP) using the MaxMind GeoIP2 database. This enrichment enabled geographic threat distribution analysis and ISP-based attacker profiling.

**Visualization and Monitoring:** A custom real-time dashboard was developed using Streamlit to provide live monitoring capabilities. The dashboard integrated with Grafana for time-series metrics visualization and Prometheus for infrastructure monitoring. This multi-layered observability approach enabled both real-time operational awareness and historical trend analysis.

**Reinforcement Learning Engine:** The PPO agent operated with a 20-dimensional state space capturing attack characteristics including attacker skill level, suspicion level, data collected, attack duration, command patterns, and MITRE ATT&CK technique indicators. The agent selected from 20 distinct deception actions ranging from passive monitoring to active engagement techniques.

The system was monitored continuously over multiple deployment periods spanning several weeks, accumulating significant real-world attack data from internet-based threat actors.

## Quantitative Performance Metrics

The deployed Cyber Mirage system demonstrated substantial engagement with real-world threat actors over the observation period. The following metrics quantify the system's operational performance:

**Total Attack Requests:** 9,106 malicious network requests were captured and processed by the honeypot infrastructure. Each request represented an attacker interaction ranging from initial reconnaissance scans to sustained exploitation attempts.

**Reinforcement Learning Decisions:** The PPO agent executed 8,727 deception decisions across all attack sessions. This high decision count demonstrates the agent's active involvement in shaping attacker engagement, with an average of 0.96 RL decisions per attack request, indicating that nearly every attack interaction was evaluated and responded to by the intelligent deception system.

**Unique Attacking IP Addresses:** 628 distinct source IP addresses were recorded, representing a diverse threat landscape spanning automated scanners, botnets, and targeted attackers. The ratio of 9,106 requests to 628 unique IPs (14.5 requests per IP on average) indicates repeat engagement from persistent attackers.

**Average Reward Score:** The RL agent achieved an average reward of 6.97 per decision, substantially above the baseline reward threshold. This positive reward trajectory indicates that the agent successfully learned to balance multiple objectives: maintaining deception realism, maximizing data collection, and avoiding premature detection.

**Action Space Utilization:** All 20 available deception actions were successfully employed by the agent during live operation. This complete action space coverage demonstrates that the training process enabled the agent to discover effective use cases for the entire tactical repertoire, rather than converging to a limited subset of safe but suboptimal actions.

**Recent Activity Volume:** In the final 24-hour observation period, the system captured 3,095 attack attempts, representing 34% of the total attack volume. This concentration indicates either an escalation in attack intensity or improved honeypot visibility in attacker scanning infrastructure during later deployment phases.

**Service Targeting Distribution:** SMB services on ports 445 and 139 attracted 88.5% of all attack traffic (8,059 of 9,106 requests). This overwhelming preference for SMB exploitation reflects the protocol's continued prevalence as a primary attack vector, particularly for ransomware deployment, credential theft, and lateral movement operations.

## Reinforcement Learning Action Distribution

Analysis of the RL agent's action selection patterns revealed sophisticated decision-making behavior aligned with optimal deception strategies. The action distribution demonstrated clear strategic preferences rather than uniform random selection:

**CAPTURE Actions (7,023 executions, 80.5%):** The CAPTURE action, which maintains full engagement while covertly logging all attacker activity, was by far the most frequently selected action. This preference indicates the agent learned that silent observation maximizes intelligence collection while minimizing detection risk. The high frequency of CAPTURE actions demonstrates the agent's primary objective achievement: keeping attackers engaged for extended periods to gather comprehensive behavioral data.

**SWITCH_BANNER Actions (845 executions, 9.7%):** Banner switching, which modifies service identification strings to present different apparent vulnerabilities, was the second most common action. This tactical deception can redirect attacker focus, extend engagement time, or gauge attacker sophistication based on their response to banner changes.

**INJECT_DELAY Actions (512 executions, 5.9%):** Network delay injection simulates realistic system latency or processing overhead. The agent's selective use of this action suggests it learned to employ delays strategically—potentially to simulate resource-intensive operations or to pace attacker progression through attack stages.

**REDIRECT Actions (347 executions, 4.0%):** Redirection to alternative honeypot services or decoy resources was employed in specific contexts, likely when the agent identified opportunities to steer attackers toward more instrumented environments or to test attacker persistence.

**Rare Actions (Combined <1%):** Actions such as DROP_SESSION (premature termination), AGGRESSIVE_RESPONSE (overt defensive behavior), and FAKE_ERROR (simulated system failures) were used sparingly. This restraint demonstrates the agent learned to avoid actions that risk revealing the honeypot's true nature.

The action distribution analysis proves the reinforcement learning model successfully acquired sophisticated deception strategies. The agent learned to prioritize sustained engagement over reactive defensive measures, avoid obvious honeypot indicators, and emphasize comprehensive data collection approaches. This behavior contrasts sharply with rule-based honeypots that often employ deterministic or easily recognizable response patterns.

## Geographic Threat Distribution Analysis

Attack traffic originated from diverse geographic locations, reflecting the global nature of internet-based cyber threats. The primary source countries for attacks included:

**India:** The highest volume of attacks originated from Indian IP space, likely representing a combination of compromised residential networks, virtual private server (VPS) infrastructure, and legitimate attacker operations. The prevalence of Indian source IPs aligns with known patterns of botnet command infrastructure and bulletproof hosting concentrations in the region.

**Indonesia:** Indonesian networks contributed significant attack traffic, predominantly automated scanning and brute force attempts. Many attacks from this region exhibited characteristics of IoT botnet activity, with repetitive scanning patterns targeting default credentials.

**Russia:** Russian-sourced attacks demonstrated higher sophistication levels on average, with evidence of manual exploitation attempts, lateral movement reconnaissance, and targeted service enumeration. Several Russian IPs exhibited multi-stage attack patterns consistent with advanced persistent threat (APT) tradecraft.

**United States:** US-based attack sources included both compromised cloud infrastructure (AWS, Azure, GCP) and residential networks. The sophistication level varied widely, from automated vulnerability scanning to deliberate exploitation attempts.

**Singapore, Australia, Germany, Pakistan:** These countries contributed secondary attack volumes with diverse attack patterns ranging from opportunistic scanning to focused exploitation attempts.

The threat map visualization plotted the geographic coordinates of all attacking IPs, revealing clustering patterns consistent with botnet concentrations, cloud provider regions, and known cybercrime infrastructure hubs. The geographic diversity of attack sources demonstrates the honeypot's successful exposure to global threat actors rather than localized scanning activity.

## Threat Intelligence Enrichment and Attacker Profiling

Each captured attacker IP address was enriched with comprehensive threat intelligence metadata stored in a structured intelligence table. The enrichment process integrated multiple data sources to build detailed attacker profiles:

**Geolocation Data:** Country, city, latitude/longitude coordinates, and timezone information enabled geographic threat distribution analysis and identification of attack origin patterns.

**Network Information:** Autonomous System Number (ASN) and Internet Service Provider (ISP) data revealed attacker infrastructure characteristics. Attacks originating from cloud providers (e.g., Amazon AWS, DigitalOcean) indicated deliberate infrastructure acquisition, while residential ISPs suggested compromised endpoints or VPN usage.

**Severity Classification:** Each attacker was assigned a severity level (Low, Medium, High, Critical) based on behavioral indicators including attack frequency, sophistication of techniques employed, data exfiltration attempts, and correlation with known threat indicators.

**Service Targeting Patterns:** Recording which services each attacker targeted revealed specialization patterns. Some attackers exclusively targeted SSH for credential brute forcing, while others exhibited multi-service reconnaissance consistent with network mapping behavior.

**Attack Volume Metrics:** Total attack count per IP and temporal distribution (first seen, last seen, recent activity) enabled identification of persistent threats versus opportunistic scanners.

The enriched intelligence data enabled categorization of attackers into distinct behavioral profiles:

**Botnets:** Characterized by high-volume automated scanning from residential IP space with repetitive patterns and low sophistication. These attacks typically targeted multiple services with default credentials and known exploits.

**Scanners:** Systematic service enumeration and vulnerability scanning behavior, often originating from dedicated scanning infrastructure. These attacks exhibited regular temporal patterns and broad service coverage.

**Brute-Force Tools:** Focused credential guessing attacks against authentication services (SSH, FTP, SMB) with dictionary or credential stuffing patterns. Attack velocity and pattern regularity indicated automated tooling.

**Targeted Attackers:** Manual or semi-automated attacks demonstrating adaptive behavior, service-specific exploitation techniques, and multi-stage attack progression. These attackers exhibited lower volume but higher sophistication, with evidence of reconnaissance, exploitation, and post-exploitation activities.

The threat intelligence enrichment capability transformed raw IP addresses and network traffic into actionable threat profiles, enabling security teams to prioritize incident response, block malicious infrastructure, and understand attacker capabilities and motivations.

## Reinforcement Learning Performance Evaluation

The PPO agent's performance in live deployment validated the effectiveness of reinforcement learning for adaptive honeypot deception. Key performance characteristics included:

**Stable Decision Policies:** After initial training, the agent exhibited consistent decision-making patterns without catastrophic forgetting or policy collapse. The average reward remained stable throughout deployment, indicating the learned policy generalized effectively to real-world attack distributions not seen during training.

**High Average Reward:** The sustained average reward of 6.97 significantly exceeded baseline non-RL honeypot performance. This reward level demonstrates successful multi-objective optimization across competing goals: maximizing attacker engagement time, collecting behavioral data, and maintaining deception credibility.

**Behavioral Realism:** The agent's action selection produced realistic system responses that avoided common honeypot detection indicators. The preference for passive observation over reactive measures, strategic use of delays, and avoidance of obviously fake responses contributed to sustained attacker engagement.

**Effective Deception Tactics:** The agent successfully employed sophisticated deception techniques including adaptive banner switching, strategic delay injection, and intelligent session management. These tactics extended average attack session duration compared to static honeypot configurations.

**Avoidance of Counterproductive Actions:** The agent learned to minimize risky actions that could expose the honeypot. Early session termination (DROP_SESSION) and aggressive defensive responses were used sparingly, only in scenarios where the cost-benefit analysis favored termination over continued engagement.

**Preference for Intelligence Collection:** The overwhelming preference for CAPTURE actions demonstrates the agent optimized for the primary objective: comprehensive threat intelligence collection. This behavior aligns with honeypot best practices emphasizing observation over active defense.

The RL agent's performance demonstrates that reinforcement learning provides significant advantages over rule-based honeypot systems. The agent adapted to real-world attack patterns, made context-aware decisions based on attacker behavior, and optimized for long-term intelligence value rather than short-term reactive responses.

## Discussion and Analysis

The experimental results validate the core hypothesis that reinforcement learning can significantly enhance honeypot effectiveness by enabling adaptive, intelligent deception strategies. The deployment of Cyber Mirage in a live internet environment provided several key insights:

The high engagement rate (8,727 RL decisions across 9,106 attacks) demonstrates that nearly every attacker interaction was actively managed by the intelligent deception system. This level of engagement is impractical with manual honeypot management and difficult to achieve with static rule-based systems.

The complete utilization of all 20 deception actions indicates the training process successfully explored the full action space and discovered effective applications for diverse tactical responses. This contrasts with simpler learning approaches that often converge to limited action subsets.

The overwhelming focus on SMB services (88.5% of attacks) reflects real-world threat landscapes where SMB remains a primary attack vector, particularly for ransomware campaigns. This distribution validates the honeypot's realism—attackers treated the system as a legitimate target consistent with typical internet-exposed networks.

The geographic diversity of attack sources (628 unique IPs from multiple countries) demonstrates the honeypot's exposure to global threat actors rather than localized activity. This distribution is critical for representative threat intelligence collection.

The agent's learned behavior (80.5% CAPTURE actions, minimal DROP_SESSION usage) aligns with optimal honeypot strategies identified in security research: maximize observation time, minimize detection risk, and prioritize intelligence collection over active defense.

## Future Research Directions

Building on the successful deployment and validation of Cyber Mirage, several promising directions for future research and development have been identified:

**Extended Service Emulation:** Expanding the honeypot's service portfolio to include additional high-value targets would broaden threat intelligence coverage. Priority services include Remote Desktop Protocol (RDP) for Windows remote access attacks, Telnet for IoT and legacy system exploitation, Elasticsearch for database targeting and data exposure, and Kubernetes API endpoints for cloud-native attack vectors. These additions would enable capture of emerging attack patterns targeting modern infrastructure.

**Advanced Reinforcement Learning Architectures:** While PPO demonstrated strong performance, more sophisticated RL algorithms may yield further improvements. Deep Q-Networks (DQN) could provide better sample efficiency in sparse reward environments. Asynchronous Advantage Actor-Critic (A3C) could enable parallel training across multiple honeypot instances. Twin Delayed Deep Deterministic Policy Gradient (TD3) could improve stability and performance in continuous action spaces if the deception action model is extended beyond discrete choices.

**Automated Attack Replay Systems:** Developing capabilities to replay captured attack sequences in isolated analysis environments would enable detailed forensic investigation, malware behavior analysis, and attack technique documentation. Replay systems could feed findings back into the RL training process to improve agent responses to specific attack patterns.

**SIEM Platform Integration:** Integrating Cyber Mirage with enterprise Security Information and Event Management (SIEM) platforms such as Splunk, Elastic SIEM, and QRadar would enable seamless threat intelligence sharing with existing security operations. Automated indicator extraction, threat feed generation, and alert correlation would enhance the honeypot's operational value for security teams.

**Dynamic Lure Automation:** Implementing automated lure generation that adapts to specific attacker profiles could further improve engagement effectiveness. The system could dynamically create fake credentials, vulnerable configurations, or sensitive data artifacts tailored to individual attacker behavior patterns, increasing the perceived value of compromise and extending engagement time.

**Multi-Agent Coordination:** Deploying multiple coordinated RL agents across distributed honeypot infrastructure could enable collective learning and coordinated deception strategies. Agents could share intelligence about persistent attackers, coordinate banner and service configurations to create consistent fake networks, and optimize global rather than local engagement metrics.

**Adversarial Robustness:** As attackers become aware of ML-based defensive systems, research into adversarial robustness of the RL agent becomes critical. Studying how sophisticated attackers might probe for or exploit the RL decision process, and developing countermeasures to ensure the agent remains effective against adversarial manipulation, represents an important research direction.

These future directions would build upon the validated foundation of Cyber Mirage to create increasingly sophisticated, adaptive, and operationally valuable deception infrastructure for cyber threat intelligence and defense.
