"""
🌍 COMPREHENSIVE Cyber Mirage Environment 🌍
بيئة شاملة لكل أنواع الهجمات السيبرانية الموجودة في العالم

Features:
- 50+ نوع مهاجم (كل شيء!)
- من المبتدئين للخبراء (0% → 100%)
- بدون تقسيمات مصطنعة
- كل attacker له مهارته الخاصة
- توزيع طبيعي واقعي
"""

import gymnasium as gym
import numpy as np
from gymnasium import spaces


class ComprehensiveHoneynetEnv(gym.Env):
    """بيئة شاملة لكل أنواع المهاجمين في العالم"""

    # MITRE ATT&CK Tactics (11 tactics)
    MITRE_TACTICS = {
        'reconnaissance': ['T1595', 'T1590', 'T1589'],
        'initial_access': ['T1190', 'T1133', 'T1078'],
        'execution': ['T1059', 'T1203', 'T1204'],
        'persistence': ['T1053', 'T1547', 'T1136'],
        'privilege_escalation': ['T1068', 'T1055', 'T1134'],
        'defense_evasion': ['T1027', 'T1070', 'T1562'],
        'credential_access': ['T1110', 'T1003', 'T1056'],
        'discovery': ['T1082', 'T1083', 'T1018'],
        'lateral_movement': ['T1021', 'T1210', 'T1570'],
        'collection': ['T1005', 'T1039', 'T1119'],
        'exfiltration': ['T1041', 'T1048', 'T1567'],
    }
    
    # 🌍 كل أنواع المهاجمين في العالم (50+ نوع)
    ATTACKER_PROFILES = {
        # ========== 1-10: المبتدئين الكاملين (0-30%) ==========
        "CURIOUS_USER": {
            "skill": 0.05, "stealth": 0.05, "persistence": 0.05,
            "origin": "Curious Individual",
            "desc": "مستخدم فضولي بس، مافيه نية سيئة"
        },
        "AUTOMATED_BOT": {
            "skill": 0.08, "stealth": 0.10, "persistence": 0.80,
            "origin": "Automated Scanner",
            "desc": "بوت تلقائي يسكن الإنترنت"
        },
        "SCRIPT_KIDDIE_BASIC": {
            "skill": 0.12, "stealth": 0.10, "persistence": 0.08,
            "origin": "Basic Script Kiddie",
            "desc": "يستخدم Metasploit بدون فهم"
        },
        "YOUTUBE_HACKER": {
            "skill": 0.15, "stealth": 0.12, "persistence": 0.10,
            "origin": "Tutorial Follower",
            "desc": "يتابع فيديوهات YouTube ويطبق"
        },
        "SCRIPT_KIDDIE": {
            "skill": 0.20, "stealth": 0.15, "persistence": 0.15,
            "origin": "Script Kiddie",
            "desc": "Tools جاهزة: Metasploit, SQLmap, Nmap"
        },
        "WEB_DEFACER": {
            "skill": 0.25, "stealth": 0.20, "persistence": 0.18,
            "origin": "Website Defacer",
            "desc": "يخرب المواقع ويحط اسمه"
        },
        "FORUM_SCRIPTER": {
            "skill": 0.28, "stealth": 0.25, "persistence": 0.22,
            "origin": "Forum Script User",
            "desc": "ينسخ scripts من المنتديات"
        },
        
        # ========== 11-20: المبتدئين المتقدمين (30-45%) ==========
        "PHISHING_BEGINNER": {
            "skill": 0.32, "stealth": 0.28, "persistence": 0.25,
            "origin": "Basic Phishing",
            "desc": "فيشينق بسيط بدون تخصيص"
        },
        "MALWARE_SPREADER": {
            "skill": 0.35, "stealth": 0.30, "persistence": 0.40,
            "origin": "Malware Distribution",
            "desc": "ينشر malware جاهز"
        },
        "CREDENTIAL_STEALER": {
            "skill": 0.38, "stealth": 0.35, "persistence": 0.30,
            "origin": "Credential Harvester",
            "desc": "يسرق usernames وpasswords"
        },
        "SQL_INJECTOR": {
            "skill": 0.40, "stealth": 0.32, "persistence": 0.28,
            "origin": "SQL Injection Specialist",
            "desc": "متخصص في SQL injection"
        },
        "XSS_ATTACKER": {
            "skill": 0.42, "stealth": 0.38, "persistence": 0.32,
            "origin": "XSS Specialist",
            "desc": "Cross-Site Scripting attacks"
        },
        "DDOS_OPERATOR": {
            "skill": 0.45, "stealth": 0.25, "persistence": 0.50,
            "origin": "DDoS Operator",
            "desc": "هجمات DDoS بسيطة"
        },
        
        # ========== 21-35: المتوسطين (45-65%) ==========
        "BOTNET_BASIC": {
            "skill": 0.48, "stealth": 0.40, "persistence": 0.55,
            "origin": "Basic Botnet",
            "desc": "Botnet صغير"
        },
        "PHISHING_ADVANCED": {
            "skill": 0.50, "stealth": 0.45, "persistence": 0.40,
            "origin": "Spear Phishing",
            "desc": "فيشينق مستهدف"
        },
        "RAT_OPERATOR": {
            "skill": 0.52, "stealth": 0.48, "persistence": 0.60,
            "origin": "RAT User",
            "desc": "Remote Access Trojan"
        },
        "CRYPTOJACKER": {
            "skill": 0.55, "stealth": 0.65, "persistence": 0.75,
            "origin": "Cryptocurrency Miner",
            "desc": "تعدين خفي للعملات"
        },
        "WEB_SHELL_ATTACKER": {
            "skill": 0.57, "stealth": 0.50, "persistence": 0.68,
            "origin": "Web Shell Deployer",
            "desc": "يزرع web shells"
        },
        "EXPLOIT_KIT_USER": {
            "skill": 0.60, "stealth": 0.55, "persistence": 0.50,
            "origin": "Exploit Kit",
            "desc": "يستخدم exploit kits جاهزة"
        },
        "INSIDER_THREAT": {
            "skill": 0.62, "stealth": 0.80, "persistence": 0.70,
            "origin": "Malicious Insider",
            "desc": "موظف خائن"
        },
        "BUSINESS_EMAIL_COMPROMISE": {
            "skill": 0.65, "stealth": 0.70, "persistence": 0.60,
            "origin": "BEC Scammer",
            "desc": "احتيال email تجاري"
        },
        
        # ========== 36-45: المتقدمين (65-80%) ==========
        "ADVANCED_BOTNET": {
            "skill": 0.68, "stealth": 0.60, "persistence": 0.78,
            "origin": "Advanced Botnet (Mirai, Emotet)",
            "desc": "Botnet متقدم"
        },
        "RANSOMWARE_BASIC": {
            "skill": 0.70, "stealth": 0.55, "persistence": 0.65,
            "origin": "Basic Ransomware",
            "desc": "Ransomware بسيط"
        },
        "BANKING_TROJAN": {
            "skill": 0.72, "stealth": 0.68, "persistence": 0.70,
            "origin": "Banking Malware",
            "desc": "يستهدف البنوك"
        },
        "RANSOMWARE_GANG": {
            "skill": 0.75, "stealth": 0.60, "persistence": 0.72,
            "origin": "Ransomware Gang (REvil, LockBit)",
            "desc": "عصابة ransomware منظمة"
        },
        "FINANCIALLY_MOTIVATED_FIN7": {
            "skill": 0.78, "stealth": 0.75, "persistence": 0.78,
            "origin": "FIN7 (Carbanak)",
            "desc": "مجموعة مالية منظمة"
        },
        "FINANCIALLY_MOTIVATED_FIN8": {
            "skill": 0.79, "stealth": 0.72, "persistence": 0.76,
            "origin": "FIN8",
            "desc": "تستهدف POS systems"
        },
        
        # ========== 46-60: APT Groups - المحترفين (80-90%) ==========
        "APT1_COMMENT_CREW": {
            "skill": 0.82, "stealth": 0.78, "persistence": 0.88,
            "origin": "China (PLA Unit 61398)",
            "desc": "سرقة IP ضخمة"
        },
        "APT3_GOTHIC_PANDA": {
            "skill": 0.83, "stealth": 0.80, "persistence": 0.85,
            "origin": "China",
            "desc": "استهداف دول آسيوية"
        },
        "APT10_STONE_PANDA": {
            "skill": 0.84, "stealth": 0.82, "persistence": 0.87,
            "origin": "China (MSS)",
            "desc": "Cloud Hopper campaign"
        },
        "APT12_CALC_TEAM": {
            "skill": 0.83, "stealth": 0.79, "persistence": 0.84,
            "origin": "China",
            "desc": "صحافة وحقوق إنسان"
        },
        "APT15_VIXEN_PANDA": {
            "skill": 0.82, "stealth": 0.77, "persistence": 0.83,
            "origin": "China",
            "desc": "استهداف شركات نفط"
        },
        "APT16": {
            "skill": 0.83, "stealth": 0.78, "persistence": 0.85,
            "origin": "China",
            "desc": "تايوان واليابان"
        },
        "APT17_DEPUTY_DOG": {
            "skill": 0.84, "stealth": 0.81, "persistence": 0.86,
            "origin": "China",
            "desc": "قانون ودفاع"
        },
        "APT19_CODOSO": {
            "skill": 0.85, "stealth": 0.83, "persistence": 0.87,
            "origin": "China",
            "desc": "استهداف إعلام"
        },
        "APT27_EMISSARY_PANDA": {
            "skill": 0.84, "stealth": 0.80, "persistence": 0.86,
            "origin": "China",
            "desc": "جنوب شرق آسيا"
        },
        "APT30": {
            "skill": 0.86, "stealth": 0.84, "persistence": 0.89,
            "origin": "China",
            "desc": "منطقة آسيا والمحيط الهادئ"
        },
        "APT32_OCEAN_LOTUS": {
            "skill": 0.88, "stealth": 0.82, "persistence": 0.85,
            "origin": "Vietnam",
            "desc": "فيتنام وجنوب شرق آسيا"
        },
        "APT33_ELFIN": {
            "skill": 0.83, "stealth": 0.79, "persistence": 0.82,
            "origin": "Iran",
            "desc": "قطاع الطيران والطاقة"
        },
        "APT34_OILRIG": {
            "skill": 0.84, "stealth": 0.80, "persistence": 0.83,
            "origin": "Iran (MOIS)",
            "desc": "الشرق الأوسط والطاقة"
        },
        "APT35_CHARMING_KITTEN": {
            "skill": 0.82, "stealth": 0.78, "persistence": 0.81,
            "origin": "Iran",
            "desc": "فيشينق متقدم جداً"
        },
        "APT37_REAPER": {
            "skill": 0.84, "stealth": 0.81, "persistence": 0.84,
            "origin": "North Korea",
            "desc": "استهداف كوريا الجنوبية"
        },
        "APT38": {
            "skill": 0.87, "stealth": 0.83, "persistence": 0.86,
            "origin": "North Korea",
            "desc": "SWIFT heists, البنوك"
        },
        "APT39": {
            "skill": 0.83, "stealth": 0.79, "persistence": 0.82,
            "origin": "Iran",
            "desc": "اتصالات وسفر"
        },
        "APT40_LEVIATHAN": {
            "skill": 0.85, "stealth": 0.81, "persistence": 0.85,
            "origin": "China",
            "desc": "بحري وهندسة"
        },
        "APT41_DOUBLE_DRAGON": {
            "skill": 0.96, "stealth": 0.90, "persistence": 0.88,
            "origin": "China (MSS)",
            "desc": "تجسس + مالي"
        },
        
        # ========== 61-70: Elite APT Groups (90-95%) ==========
        "TURLA_SNAKE": {
            "skill": 0.90, "stealth": 0.88, "persistence": 0.92,
            "origin": "Russia (FSB)",
            "desc": "Snake malware، تجسس طويل"
        },
        "SANDWORM_VOODOO_BEAR": {
            "skill": 0.91, "stealth": 0.85, "persistence": 0.89,
            "origin": "Russia (GRU Unit 74455)",
            "desc": "NotPetya, Industroyer, BlackEnergy"
        },
        "DRAGONFLY_ENERGETIC_BEAR": {
            "skill": 0.89, "stealth": 0.86, "persistence": 0.90,
            "origin": "Russia",
            "desc": "استهداف البنية التحتية"
        },
        "LAZARUS_GROUP_HIDDEN_COBRA": {
            "skill": 0.93, "stealth": 0.88, "persistence": 0.91,
            "origin": "North Korea (RGB Bureau 121)",
            "desc": "WannaCry, Sony hack, SWIFT"
        },
        "KIMSUKY_THALLIUM": {
            "skill": 0.85, "stealth": 0.82, "persistence": 0.84,
            "origin": "North Korea",
            "desc": "فيشينق وجمع معلومات"
        },
        "APT28_FANCY_BEAR": {
            "skill": 0.95, "stealth": 0.85, "persistence": 0.90,
            "origin": "Russia (GRU Unit 26165)",
            "desc": "DNC hack, انتخابات، عسكري"
        },
        "APT29_COZY_BEAR": {
            "skill": 0.98, "stealth": 0.95, "persistence": 0.93,
            "origin": "Russia (SVR)",
            "desc": "SolarWinds supply chain"
        },
        "NOBELIUM": {
            "skill": 0.97, "stealth": 0.94, "persistence": 0.92,
            "origin": "Russia (SVR) - APT29 subgroup",
            "desc": "SolarWinds operation الفعلي"
        },
        
        # ========== 71-85: Elite APT Continued ==========
        "HAFNIUM": {
            "skill": 0.92, "stealth": 0.89, "persistence": 0.90,
            "origin": "China",
            "desc": "Exchange Server exploits 2021"
        },
        "GALLIUM": {
            "skill": 0.86, "stealth": 0.83, "persistence": 0.85,
            "origin": "China",
            "desc": "Telecom operators targeted"
        },
        "CHAMELGANG": {
            "skill": 0.84, "stealth": 0.81, "persistence": 0.83,
            "origin": "China",
            "desc": "Aviation and energy sectors"
        },
        "TWISTED_PANDA": {
            "skill": 0.85, "stealth": 0.82, "persistence": 0.84,
            "origin": "China",
            "desc": "Southeast Asian governments"
        },
        "MUSTANG_PANDA": {
            "skill": 0.83, "stealth": 0.80, "persistence": 0.82,
            "origin": "China",
            "desc": "PlugX malware specialist"
        },
        "BRONZE_UNION": {
            "skill": 0.85, "stealth": 0.82, "persistence": 0.84,
            "origin": "China",
            "desc": "Gambling and gaming industry"
        },
        "TEMP_HERETIC": {
            "skill": 0.84, "stealth": 0.80, "persistence": 0.83,
            "origin": "China",
            "desc": "Maritime and defense"
        },
        "MENUPASS_APT10": {
            "skill": 0.87, "stealth": 0.84, "persistence": 0.86,
            "origin": "China (Stone Panda)",
            "desc": "Managed service providers"
        },
        "BRONZE_RIVERSIDE": {
            "skill": 0.82, "stealth": 0.79, "persistence": 0.81,
            "origin": "China",
            "desc": "Military and government"
        },
        "TONTO_TEAM": {
            "skill": 0.83, "stealth": 0.80, "persistence": 0.82,
            "origin": "China",
            "desc": "Government and military"
        },
        "NAIKON": {
            "skill": 0.84, "stealth": 0.81, "persistence": 0.83,
            "origin": "China (PLA)",
            "desc": "Asian governments targeted"
        },
        "WINNTI_GROUP": {
            "skill": 0.88, "stealth": 0.85, "persistence": 0.87,
            "origin": "China",
            "desc": "Gaming companies, supply chain"
        },
        "AXIOM_APT17": {
            "skill": 0.85, "stealth": 0.82, "persistence": 0.84,
            "origin": "China",
            "desc": "Deputy Dog campaigns"
        },
        "GOBLIN_PANDA": {
            "skill": 0.83, "stealth": 0.79, "persistence": 0.81,
            "origin": "China",
            "desc": "Vietnam government targeted"
        },
        "PUTTER_PANDA": {
            "skill": 0.82, "stealth": 0.78, "persistence": 0.80,
            "origin": "China (PLA)",
            "desc": "Aerospace and satellite"
        },
        
        # ========== 86-100: Iranian Groups ==========
        "APT33_REFINED_KITTEN": {
            "skill": 0.83, "stealth": 0.79, "persistence": 0.82,
            "origin": "Iran (IRGC)",
            "desc": "Shamoon wiper attacks"
        },
        "MAGIC_HOUND_APT35": {
            "skill": 0.82, "stealth": 0.78, "persistence": 0.81,
            "origin": "Iran",
            "desc": "Newscaster campaign"
        },
        "COBALT_MIRAGE": {
            "skill": 0.80, "stealth": 0.76, "persistence": 0.79,
            "origin": "Iran",
            "desc": "Israeli targets"
        },
        "PHOSPHORUS": {
            "skill": 0.81, "stealth": 0.77, "persistence": 0.80,
            "origin": "Iran",
            "desc": "US political campaigns"
        },
        "LYCEUM": {
            "skill": 0.79, "stealth": 0.75, "persistence": 0.78,
            "origin": "Iran",
            "desc": "Middle East energy and telecom"
        },
        "AGRIUS": {
            "skill": 0.78, "stealth": 0.74, "persistence": 0.77,
            "origin": "Iran",
            "desc": "Wiper attacks on Israel"
        },
        "SEEDWORM": {
            "skill": 0.82, "stealth": 0.78, "persistence": 0.81,
            "origin": "Iran (MuddyWater)",
            "desc": "Middle East and Europe"
        },
        "HEXANE": {
            "skill": 0.80, "stealth": 0.76, "persistence": 0.79,
            "origin": "Iran",
            "desc": "Industrial control systems"
        },
        "CRAMBUS": {
            "skill": 0.77, "stealth": 0.73, "persistence": 0.76,
            "origin": "Iran",
            "desc": "Middle Eastern telecom"
        },
        "FOX_KITTEN": {
            "skill": 0.79, "stealth": 0.75, "persistence": 0.78,
            "origin": "Iran",
            "desc": "VPN exploits for access"
        },
        
        # ========== 101-110: North Korean Groups ==========
        "ANDARIEL": {
            "skill": 0.84, "stealth": 0.80, "persistence": 0.83,
            "origin": "North Korea (Lazarus sub)",
            "desc": "South Korean military"
        },
        "BLUENOROFF": {
            "skill": 0.90, "stealth": 0.86, "persistence": 0.88,
            "origin": "North Korea (Lazarus sub)",
            "desc": "Financial institution heists"
        },
        "STARDUST_CHOLLIMA": {
            "skill": 0.87, "stealth": 0.83, "persistence": 0.85,
            "origin": "North Korea",
            "desc": "Cryptocurrency exchanges"
        },
        "SILENT_CHOLLIMA": {
            "skill": 0.83, "stealth": 0.79, "persistence": 0.82,
            "origin": "North Korea",
            "desc": "Media and aerospace"
        },
        "RICOCHET_CHOLLIMA": {
            "skill": 0.85, "stealth": 0.81, "persistence": 0.84,
            "origin": "North Korea",
            "desc": "Cryptocurrency and DeFi"
        },
        
        # ========== 111-125: Russian Groups (Beyond APT28/29) ==========
        "BERSERK_BEAR_ENERGETIC": {
            "skill": 0.89, "stealth": 0.86, "persistence": 0.88,
            "origin": "Russia",
            "desc": "Energy sector ICS"
        },
        "VENOMOUS_BEAR": {
            "skill": 0.86, "stealth": 0.82, "persistence": 0.85,
            "origin": "Russia",
            "desc": "Turla variant operations"
        },
        "IRON_TWILIGHT": {
            "skill": 0.88, "stealth": 0.84, "persistence": 0.87,
            "origin": "Russia",
            "desc": "Sednit/APT28 campaigns"
        },
        "PRIMITIVE_BEAR": {
            "skill": 0.87, "stealth": 0.83, "persistence": 0.86,
            "origin": "Russia (FSB)",
            "desc": "Gamaredon targeted Ukraine"
        },
        "WATERBUG_TURLA": {
            "skill": 0.91, "stealth": 0.88, "persistence": 0.90,
            "origin": "Russia (FSB)",
            "desc": "Snake/Uroburos rootkit"
        },
        "SHUCKWORM": {
            "skill": 0.85, "stealth": 0.81, "persistence": 0.84,
            "origin": "Russia (Gamaredon)",
            "desc": "Ukraine government targeted"
        },
        "VOODOO_BEAR": {
            "skill": 0.92, "stealth": 0.88, "persistence": 0.91,
            "origin": "Russia (Sandworm)",
            "desc": "NotPetya unleashed"
        },
        "IRON_VIKING": {
            "skill": 0.83, "stealth": 0.79, "persistence": 0.82,
            "origin": "Russia",
            "desc": "Zebrocy campaigns"
        },
        "SEABORGIUM": {
            "skill": 0.90, "stealth": 0.87, "persistence": 0.89,
            "origin": "Russia (GRU)",
            "desc": "NATO targeted spear phishing"
        },
        "COLDRIVER": {
            "skill": 0.84, "stealth": 0.80, "persistence": 0.83,
            "origin": "Russia (FSB)",
            "desc": "Defense sector phishing"
        },
        
        # ========== 126-135: Ransomware Gangs ==========
        "CONTI_RANSOMWARE": {
            "skill": 0.82, "stealth": 0.78, "persistence": 0.80,
            "origin": "Russia (Wizard Spider)",
            "desc": "Conti ransomware operations"
        },
        "REVIL_SODINOKIBI": {
            "skill": 0.85, "stealth": 0.80, "persistence": 0.83,
            "origin": "Russia (GoldSouthfield)",
            "desc": "REvil ransomware as service"
        },
        "LOCKBIT_GANG": {
            "skill": 0.80, "stealth": 0.76, "persistence": 0.79,
            "origin": "Russia",
            "desc": "LockBit 2.0 and 3.0"
        },
        "BLACKCAT_ALPHV": {
            "skill": 0.83, "stealth": 0.79, "persistence": 0.81,
            "origin": "Russia",
            "desc": "Rust-based ransomware"
        },
        "CLOP_RANSOMWARE": {
            "skill": 0.79, "stealth": 0.75, "persistence": 0.78,
            "origin": "Russia (FIN11)",
            "desc": "Clop double extortion"
        },
        "HIVE_RANSOMWARE": {
            "skill": 0.78, "stealth": 0.74, "persistence": 0.77,
            "origin": "Russia",
            "desc": "Hive leak site operations"
        },
        "DARKSIDE_RANSOMWARE": {
            "skill": 0.81, "stealth": 0.77, "persistence": 0.80,
            "origin": "Russia",
            "desc": "Colonial Pipeline attack"
        },
        "RAGNAR_LOCKER": {
            "skill": 0.77, "stealth": 0.73, "persistence": 0.76,
            "origin": "International",
            "desc": "Ragnar Locker ransomware"
        },
        "MAZE_RANSOMWARE": {
            "skill": 0.80, "stealth": 0.76, "persistence": 0.79,
            "origin": "Russia",
            "desc": "First major data leak"
        },
        "EGREGOR_RANSOMWARE": {
            "skill": 0.78, "stealth": 0.74, "persistence": 0.77,
            "origin": "Russia",
            "desc": "Maze successor operations"
        },
        
        # ========== 136-145: Other Notable Groups ==========
        "DARKHOTEL": {
            "skill": 0.87, "stealth": 0.84, "persistence": 0.86,
            "origin": "South Korea",
            "desc": "Hotel WiFi attacks on executives"
        },
        "TICK_BRONZE_BUTLER": {
            "skill": 0.84, "stealth": 0.80, "persistence": 0.83,
            "origin": "China",
            "desc": "Japanese organizations"
        },
        "EMISSARY_PANDA_APT27": {
            "skill": 0.85, "stealth": 0.81, "persistence": 0.84,
            "origin": "China",
            "desc": "Southeast Asian embassies"
        },
        "SCARCRUFT": {
            "skill": 0.82, "stealth": 0.78, "persistence": 0.81,
            "origin": "North Korea",
            "desc": "South Korean defectors"
        },
        "KONNI": {
            "skill": 0.79, "stealth": 0.75, "persistence": 0.78,
            "origin": "North Korea",
            "desc": "Konni RAT campaigns"
        },
        "BITTER": {
            "skill": 0.76, "stealth": 0.72, "persistence": 0.75,
            "origin": "South Asia",
            "desc": "Pakistan and China targeted"
        },
        "TRANSPARENT_TRIBE": {
            "skill": 0.75, "stealth": 0.71, "persistence": 0.74,
            "origin": "Pakistan",
            "desc": "Indian military targeted"
        },
        "SIDEWINDER": {
            "skill": 0.77, "stealth": 0.73, "persistence": 0.76,
            "origin": "India (suspected)",
            "desc": "Pakistan government targeted"
        },
        "PATCHWORK_DROPPING": {
            "skill": 0.74, "stealth": 0.70, "persistence": 0.73,
            "origin": "India (suspected)",
            "desc": "Pakistan and China"
        },
        "CONFUCIUS": {
            "skill": 0.73, "stealth": 0.69, "persistence": 0.72,
            "origin": "India (suspected)",
            "desc": "South Asian governments"
        },
        
        # ========== 146-150: The Ultimate Elite (95-100%) ==========
        "EQUATION_GROUP": {
            "skill": 0.99, "stealth": 0.98, "persistence": 0.96,
            "origin": "USA (NSA TAO)",
            "desc": "EternalBlue, DoubleP ulsar, firmware implants"
        },
        "DUQU_GROUP": {
            "skill": 0.96, "stealth": 0.93, "persistence": 0.94,
            "origin": "Unknown (Israel suspected)",
            "desc": "Duqu 2.0, Kaspersky hack"
        },
        "REGIN": {
            "skill": 0.97, "stealth": 0.95, "persistence": 0.95,
            "origin": "Five Eyes (NSA/GCHQ)",
            "desc": "5 years undetected, Belgacom"
        },
        "PROJECT_SAURON_STRIDER": {
            "skill": 0.98, "stealth": 0.97, "persistence": 0.96,
            "origin": "Unknown (suspected state)",
            "desc": "Air-gapped networks, USB implants"
        },
        "STUXNET_AUTHORS": {
            "skill": 1.00, "stealth": 0.99, "persistence": 0.98,
            "origin": "USA/Israel (Olympic Games)",
            "desc": "First true cyberweapon, 4 zero-days, ICS destruction"
        },
    }

    def __init__(self):
        super(ComprehensiveHoneynetEnv, self).__init__()

        # State Space: 15 dimensions
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.float32),
            high=np.array([1000, 100, 5000, 1, 1, 1, 1, 500, 1, 1, 100, 1, 1, 100, 100], dtype=np.float32),
            dtype=np.float32
        )

        # 20 Elite Deception Actions
        self.action_space = spaces.Discrete(20)
        self.reset()

    def reset(self, seed=None, options=None):
        if seed is not None:
            np.random.seed(seed)
        
        # اختيار attacker بشكل طبيعي (التوزيع الطبيعي)
        # كلما زادت المهارة، قلّ الاحتمال (واقعي)
        attacker_names = list(self.ATTACKER_PROFILES.keys())
        
        # حساب weights بناءً على skill (inverse: المبتدئين أكثر)
        weights = []
        for name in attacker_names:
            skill = self.ATTACKER_PROFILES[name]["skill"]
            # كلما قلّت المهارة، زاد الوزن
            weight = (1.0 - skill) ** 2  # Quadratic decay
            weights.append(weight)
        
        # Normalize
        weights = np.array(weights) / sum(weights)
        
        # اختيار attacker
        self.current_attacker = np.random.choice(attacker_names, p=weights)
        profile = self.ATTACKER_PROFILES[self.current_attacker]
        
        # Set characteristics
        self.attacker_skill = profile["skill"]
        self.attacker_stealth = profile["stealth"]
        self.attacker_persistence = profile["persistence"]
        self.attacker_origin = profile["origin"]
        self.attacker_desc = profile["desc"]
        
        # حساب detection ease (عكس stealth)
        self.detection_ease = 1.0 - self.attacker_stealth
        
        # حساب data rate (يتناسب مع skill)
        if self.attacker_skill < 0.3:
            self.data_rate_range = (1, 8)
        elif self.attacker_skill < 0.5:
            self.data_rate_range = (5, 15)
        elif self.attacker_skill < 0.7:
            self.data_rate_range = (10, 25)
        elif self.attacker_skill < 0.85:
            self.data_rate_range = (15, 35)
        elif self.attacker_skill < 0.95:
            self.data_rate_range = (25, 50)
        else:
            self.data_rate_range = (30, 70)
        
        # MITRE usage probability
        self.mitre_usage_prob = self.attacker_skill * 0.85
        
        # Initial state
        self.state = np.zeros(15, dtype=np.float32)
        self.state[0] = 0
        self.state[1] = np.random.uniform(0.01, 0.05)
        self.state[4] = self.attacker_skill
        self.state[7] = np.random.uniform(5, 15)
        self.state[9] = self.attacker_skill
        
        self.steps = 0
        self.max_steps = 1000
        self.detected_mitre_tactics = set()
        self.detected = False
        
        return self.state, {
            'attacker': self.current_attacker,
            'skill': self.attacker_skill,
            'origin': self.attacker_origin,
            'description': self.attacker_desc
        }

    def step(self, action):
        self.steps += 1
        self.state[0] += 1
        
        # ========== Suspicion Calculation ==========
        passive_actions = [0, 1, 5, 6, 7]
        moderate_actions = [2, 8, 9, 10]
        aggressive_actions = [3, 4, 11, 12, 13, 14]
        counter_apt_actions = [15, 16, 17, 18, 19]

        if action in passive_actions:
            suspicion_increase = self.detection_ease * 0.020
        elif action in moderate_actions:
            suspicion_increase = self.detection_ease * 0.045
        elif action in aggressive_actions:
            suspicion_increase = self.detection_ease * 0.075
        elif action in counter_apt_actions:
            suspicion_increase = self.detection_ease * 0.110
        else:
            suspicion_increase = self.detection_ease * 0.055
        
        stealth_reduction = self.attacker_stealth * 0.65
        final_suspicion = suspicion_increase * (1 - stealth_reduction)
        
        self.state[1] += final_suspicion
        self.state[1] = min(self.state[1], 100.0)
        
        # ========== Data Collection ==========
        min_data, max_data = self.data_rate_range
        data_collected = np.random.randint(min_data, max_data + 1)
        self.state[2] += data_collected
        
        # ========== MITRE Tactics ==========
        if np.random.random() < self.mitre_usage_prob:
            tactics = list(self.MITRE_TACTICS.keys())
            detected_tactic = np.random.choice(tactics)
            self.detected_mitre_tactics.add(detected_tactic)
        
        # ========== Advanced Techniques ==========
        if self.attacker_skill > 0.75:
            zero_day_chance = (self.attacker_skill - 0.75) * 0.70
            if np.random.random() < zero_day_chance:
                self.state[10] += 1
        
        if self.state[0] > 30 and self.attacker_skill > 0.50:
            lateral_chance = (self.attacker_persistence - 0.35) * 0.40
            if np.random.random() < lateral_chance:
                self.state[11] = 1
        
        if self.attacker_skill > 0.45:
            c2_chance = (self.attacker_skill - 0.45) * 0.45
            if np.random.random() < c2_chance:
                self.state[12] = 1
        
        if self.state[0] > 20 and self.attacker_skill > 0.40:
            priv_esc_chance = self.attacker_skill * 0.35
            if np.random.random() < priv_esc_chance:
                self.state[13] = 1
        
        if self.attacker_skill > 0.70:
            evasion_chance = (self.attacker_skill - 0.70) * 0.55
            if np.random.random() < evasion_chance:
                self.state[14] = 1
        
        # ========== Rewards ==========
        reward = 0.0
        terminated = False
        
        # Engagement reward (scaled by skill)
        if not terminated:
            base_engagement = 2.0
            skill_multiplier = 1 + (self.attacker_skill * 60)
            engagement_reward = base_engagement * skill_multiplier
            reward += engagement_reward
        
        # Intelligence reward
        if data_collected > 0:
            intel_multiplier = 1.0 + (self.attacker_skill * 5.0)
            intel_reward = data_collected * intel_multiplier
            reward += intel_reward
        
        # MITRE tactics
        mitre_count = len(self.detected_mitre_tactics)
        if mitre_count > 0:
            mitre_reward = mitre_count * 25.0 * (1 + self.attacker_skill * 4)
            reward += mitre_reward
        
        # Advanced techniques
        if self.state[10] > 0:
            reward += self.state[10] * 180.0 * (1 + self.attacker_skill * 5)
        if self.state[11] == 1:
            reward += 140.0 * (1 + self.attacker_skill * 3)
        if self.state[12] == 1:
            reward += 170.0 * (1 + self.attacker_skill * 3.5)
        if self.state[13] == 1:
            reward += 130.0 * (1 + self.attacker_skill * 2.5)
        if self.state[14] == 1:
            reward += 160.0 * (1 + self.attacker_skill * 3)
        
        # Time-based rewards
        if terminated:
            if self.state[0] < 15:
                reward -= 350.0
            elif self.state[0] < 35:
                reward -= 120.0
            elif self.state[0] < 100:
                reward += 180.0 * (1 + self.attacker_skill * 4)
            elif self.state[0] < 200:
                reward += 380.0 * (1 + self.attacker_skill * 6)
            else:
                reward += 750.0 * (1 + self.attacker_skill * 10)
        
        # Data milestones
        if self.state[2] > 1000:
            reward += 550.0
        elif self.state[2] > 500:
            reward += 280.0
        elif self.state[2] > 200:
            reward += 130.0
        elif self.state[2] > 100:
            reward += 65.0
        
        # Comprehensive intelligence
        intel_score = 0
        if self.state[10] > 0: intel_score += 1
        if self.state[11] == 1: intel_score += 1
        if self.state[12] == 1: intel_score += 1
        if self.state[13] == 1: intel_score += 1
        if self.state[14] == 1: intel_score += 1
        if mitre_count >= 5: intel_score += 1
        
        if intel_score >= 4:
            reward += 550.0 * (1 + self.attacker_skill * 5)
        
        # ========== Termination ==========
        # Detection threshold (يزيد مع skill)
        if self.attacker_skill < 0.30:
            detection_threshold = 45.0 + (self.attacker_stealth * 18.0)
        elif self.attacker_skill < 0.50:
            detection_threshold = 55.0 + (self.attacker_stealth * 20.0)
        elif self.attacker_skill < 0.70:
            detection_threshold = 70.0 + (self.attacker_stealth * 18.0)
        elif self.attacker_skill < 0.85:
            detection_threshold = 80.0 + (self.attacker_stealth * 15.0)
        elif self.attacker_skill < 0.95:
            detection_threshold = 90.0 + (self.attacker_stealth * 8.0)
        else:
            detection_threshold = 95.0 + (self.attacker_stealth * 4.0)
        
        if self.state[1] >= detection_threshold:
            terminated = True
            self.detected = True
        
        if self.steps >= self.max_steps:
            terminated = True
        
        truncated = False
        
        info = {
            'attacker': self.current_attacker,
            'skill': self.attacker_skill,
            'origin': self.attacker_origin,
            'description': self.attacker_desc,
            'data_collected': self.state[2],
            'suspicion': self.state[1],
            'mitre_tactics': len(self.detected_mitre_tactics),
            'zero_days': self.state[10],
            'detected': self.detected,
            'steps': self.steps
        }
        
        return self.state, float(reward), terminated, truncated, info


# ========== Testing ==========
if __name__ == "__main__":
    print("🌍"*40)
    print("🔥 COMPREHENSIVE Environment - كل أنواع المهاجمين!")
    print("🌍"*40)
    print()
    
    env = ComprehensiveHoneynetEnv()
    
    print(f"📊 Total Attackers: {len(env.ATTACKER_PROFILES)}")
    print()
    
    # Test 5 random attackers
    for i in range(5):
        obs, info = env.reset()
        
        print("="*80)
        print(f"🎯 Test {i+1}: {info['attacker']}")
        print("="*80)
        print(f"💪 Skill: {int(info['skill']*100)}%")
        print(f"🌍 Origin: {info['origin']}")
        print(f"📝 Description: {info['description']}")
        print()
        
        total_reward = 0
        done = False
        step = 0
        
        while not done and step < 50:
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            step += 1
            done = terminated or truncated
        
        print(f"⏱️  Steps: {step}")
        print(f"📊 Data: {int(obs[2])} MB")
        print(f"🔴 Suspicion: {obs[1]:.1f}%")
        print(f"💰 Reward: {total_reward:.0f}")
        print(f"{'✅ Detected' if info['detected'] else '⚠️  Still active'}")
        print()
    
    print("🌍"*40)
    print("✅ COMPREHENSIVE Environment جاهز!")
    print(f"📊 {len(env.ATTACKER_PROFILES)} نوع مهاجم من كل أنحاء العالم!")
    print("🌍"*40)
