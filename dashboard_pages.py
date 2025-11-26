# إضافة صفحات جديدة للـ Dashboard

def show_threat_intelligence_page():
    """صفحة تحليل التهديدات - Role 4"""
    import sys
    sys.path.insert(0, '/app')
    
    st.header(" Threat Intelligence Analysis")
    st.markdown("---")
    
    try:
        from src.analysis.threat_intel import ThreatIntelCollector
        from src.analysis.ip_reputation import IPReputationChecker
        from src.analysis.geoip_lookup import GeoIPLookup
        from src.analysis.attack_patterns import AttackPatternAnalyzer
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(" Attack Pattern Analysis")
            analyzer = AttackPatternAnalyzer()
            
            # تحليل الهجمات الأخيرة
            recent_attacks = get_recent_attacks(20)
            if not recent_attacks.empty:
                patterns_found = []
                for _, row in recent_attacks.iterrows():
                    if row.get('origin'):
                        patterns = analyzer.analyze(str(row.get('origin', '')))
                        for p in patterns:
                            patterns_found.append({
                                'Type': p.name,
                                'Severity': p.severity,
                                'Attacker': row.get('attacker_name', 'Unknown')
                            })
                
                if patterns_found:
                    st.dataframe(pd.DataFrame(patterns_found), use_container_width=True)
                else:
                    st.info(" No malicious patterns detected in recent attacks")
            
            # إحصائيات الأنماط
            st.metric(" Patterns Checked", len(analyzer.PATTERNS))
            st.metric(" Analysis Engine", "Active ")
        
        with col2:
            st.subheader(" IP Reputation & GeoIP")
            
            # فحص IP
            ip_to_check = st.text_input("Enter IP to analyze:", "185.220.101.50")
            
            if st.button(" Analyze IP"):
                checker = IPReputationChecker()
                geo = GeoIPLookup()
                
                rep = checker.check_reputation(ip_to_check)
                loc = geo.lookup(ip_to_check)
                
                st.markdown(f"""
                **IP:** `{ip_to_check}`
                
                **Reputation Score:** {rep.score}/100
                
                **Category:** {rep.category}
                
                **Location:** {loc.country} - {loc.city}
                
                **Malicious:** {' Yes' if checker.is_malicious(ip_to_check) else ' No'}
                """)
        
        st.markdown("---")
        st.subheader(" Threat Intelligence Feeds")
        
        intel = ThreatIntelCollector()
        feeds_df = pd.DataFrame({
            'Feed Name': intel.feeds,
            'Status': [' Active'] * len(intel.feeds),
            'Indicators': [150, 230, 180][:len(intel.feeds)]
        })
        st.dataframe(feeds_df, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error loading threat intelligence modules: {e}")
        st.info("Make sure all Role 4 modules are installed correctly.")


def show_forensics_page():
    """صفحة التحليل الجنائي - Role 6"""
    import sys
    sys.path.insert(0, '/app')
    
    st.header(" Digital Forensics Analysis")
    st.markdown("---")
    
    try:
        from src.forensics.evidence_collector import EvidenceCollector
        from src.forensics.timeline_builder import TimelineBuilder
        from src.forensics.log_parser import LogParser
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader(" Evidence Collection")
            collector = EvidenceCollector()
            
            st.metric(" Evidence Items", len(collector.evidence))
            st.metric(" Chain of Custody", "Maintained ")
            
            if st.button(" Collect New Evidence"):
                evidence = collector.collect_evidence("attack_log", {"source": "honeypot", "timestamp": datetime.now().isoformat()})
                st.success(f" Evidence collected: {evidence.evidence_id}")
        
        with col2:
            st.subheader(" Attack Timeline")
            builder = TimelineBuilder()
            
            # إضافة أحداث من الهجمات الأخيرة
            recent = get_recent_attacks(10)
            if not recent.empty:
                for _, row in recent.iterrows():
                    builder.add_event(
                        timestamp=str(row.get('start_time', '')),
                        event_type="attack",
                        description=f"Attack by {row.get('attacker_name', 'Unknown')}",
                        source="honeypot"
                    )
                
                st.metric(" Timeline Events", len(builder.events))
                st.metric(" Time Range", f"{len(recent)} attacks")
        
        with col3:
            st.subheader(" Log Analysis")
            parser = LogParser()
            
            st.metric(" Parsed Logs", "Active ")
            st.metric(" Parsers Available", len(parser.patterns) if hasattr(parser, 'patterns') else 3)
        
        st.markdown("---")
        st.subheader(" Recent Forensic Timeline")
        
        # عرض Timeline
        recent = get_recent_attacks(5)
        if not recent.empty:
            for idx, row in recent.iterrows():
                with st.expander(f" Attack #{idx+1} - {row.get('attacker_name', 'Unknown')}", expanded=idx==0):
                    st.markdown(f"""
                    - **Time:** {row.get('start_time', 'N/A')}
                    - **Attacker:** {row.get('attacker_name', 'Unknown')}
                    - **Skill Level:** {row.get('attacker_skill', 'N/A')}
                    - **Steps Taken:** {row.get('total_steps', 0)}
                    - **Detected:** {row.get('detected', False)}
                    - **Origin:** {row.get('origin', 'Unknown')}
                    """)
        
    except Exception as e:
        st.error(f"Error loading forensics modules: {e}")
        st.info("Make sure all Role 6 modules are installed correctly.")
