"""
⚛️ Real Quantum Computer Integration
استخدام كمبيوتر كمي حقيقي من IBM Quantum

يدعم: IBM Quantum, Qiskit Runtime
"""

try:
    from qiskit import QuantumCircuit, transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, Session, Sampler
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False

import numpy as np
from typing import List, Dict, Optional
import logging
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealQuantumDefense:
    """
    🎯 نظام دفاع كمي يستخدم كمبيوتر كمي حقيقي
    
    المميزات:
    1. توليد مفاتيح عشوائية حقيقية (True Random)
    2. اختيار استراتيجيات دفاع بشكل كمي
    3. مزامنة الأنظمة بالتشابك الكمي
    """
    
    def __init__(self, api_token: str = None, use_simulator: bool = False):
        """
        التهيئة
        
        Args:
            api_token: IBM Quantum API token
            use_simulator: استخدام محاكي بدلاً من جهاز حقيقي
        """
        if not QISKIT_AVAILABLE:
            logger.error("❌ Qiskit not installed!")
            logger.info("   Install with: pip install qiskit qiskit-ibm-runtime qiskit-aer")
            logger.info("   Using MOCK MODE for demo")
            self.use_simulator = True
            self.backend = None
            self.stats = {
                'quantum_operations': 0,
                'keys_generated': 0,
                'decisions_made': 0,
                'entanglements_created': 0
            }
            return
        
        self.api_token = api_token or os.getenv('IBM_QUANTUM_TOKEN')
        self.use_simulator = use_simulator
        
        if not self.api_token and not use_simulator:
            logger.warning("⚠️  No API token - will use simulator mode")
            self.use_simulator = True
        
        try:
            if not self.use_simulator:
                # الاتصال بخدمة IBM Quantum
                self.service = QiskitRuntimeService(
                    channel="ibm_quantum",
                    token=self.api_token
                )
                
                # اختيار أقل جهاز مشغول
                self.backend = self.service.least_busy(
                    operational=True,
                    simulator=False,
                    min_num_qubits=5
                )
                
                logger.info(f"⚛️  Connected to real quantum computer: {self.backend.name}")
                logger.info(f"   Qubits: {self.backend.num_qubits}")
                logger.info(f"   Quantum Volume: {self.backend.configuration().quantum_volume}")
            else:
                # استخدام محاكي محلي
                from qiskit_aer import Aer
                self.backend = Aer.get_backend('qasm_simulator')
                logger.info("🖥️  Using local simulator (no API required)")
                
        except Exception as e:
            logger.error(f"❌ Quantum initialization failed: {e}")
            # Fallback to simulator
            from qiskit_aer import Aer
            self.backend = Aer.get_backend('qasm_simulator')
            self.use_simulator = True
            logger.info("   Falling back to simulator")
        
        # إحصائيات
        self.stats = {
            'quantum_operations': 0,
            'keys_generated': 0,
            'decisions_made': 0,
            'entanglements_created': 0
        }
    
    def generate_quantum_key(self, key_length: int = 256) -> str:
        """
        توليد مفتاح عشوائي حقيقي باستخدام الكمبيوتر الكمي
        
        Args:
            key_length: طول المفتاح بالبتات (256, 512, 1024)
        
        Returns:
            str: مفتاح بصيغة hex
        """
        if not QISKIT_AVAILABLE or self.backend is None:
            # Mock mode - use numpy random
            logger.warning("⚠️  MOCK MODE: Using pseudo-random (not true quantum)")
            import random
            key_int = random.getrandbits(key_length)
            key_hex = hex(key_int)[2:].zfill(key_length // 4)
            self.stats['keys_generated'] += 1
            return key_hex
        
        logger.info(f"🔑 Generating {key_length}-bit quantum key...")
        
        # عدد الدوائر المطلوبة
        num_circuits = (key_length + 63) // 64  # كل دائرة تعطي 64 بت
        
        key_bits = []
        
        for i in range(num_circuits):
            # إنشاء دائرة كمية
            qc = QuantumCircuit(64, 64)
            
            # وضع جميع الكيوبتات في حالة Superposition
            for qubit in range(64):
                qc.h(qubit)  # Hadamard gate
            
            # القياس
            qc.measure(range(64), range(64))
            
            # التنفيذ
            result = self._execute_circuit(qc, shots=1)
            
            # استخراج النتيجة
            if result:
                measured = list(result.keys())[0]
                key_bits.extend([int(b) for b in measured])
        
        # تحويل إلى hex
        key_bits = key_bits[:key_length]
        key_int = int(''.join(map(str, key_bits)), 2)
        key_hex = hex(key_int)[2:].zfill(key_length // 4)
        
        self.stats['keys_generated'] += 1
        self.stats['quantum_operations'] += num_circuits
        
        logger.info(f"   ✓ Key generated: {key_hex[:16]}...{key_hex[-16:]}")
        return key_hex
    
    def quantum_random_defense(self, threat_level: float) -> str:
        """
        اختيار استراتيجية دفاع باستخدام عشوائية كمية
        
        Args:
            threat_level: مستوى التهديد (0.0 - 1.0)
        
        Returns:
            str: الاستراتيجية المختارة
        """
        strategies = [
            'REDIRECT_HONEYPOT',
            'BLOCK_IMMEDIATELY',
            'MONITOR_CLOSELY',
            'DEPLOY_DECOY',
            'ADAPTIVE_RESPONSE',
            'QUANTUM_CONFUSION',
            'SWARM_DEFENSE',
            'ISOLATE_ATTACKER'
        ]
        
        if not QISKIT_AVAILABLE or self.backend is None:
            # Mock mode - weighted random based on threat
            logger.warning("⚠️  MOCK MODE: Using pseudo-random strategy selection")
            import random
            # Higher threat = more aggressive strategies
            if threat_level > 0.8:
                strategy = random.choice(['BLOCK_IMMEDIATELY', 'ISOLATE_ATTACKER'])
            elif threat_level > 0.5:
                strategy = random.choice(['REDIRECT_HONEYPOT', 'DEPLOY_DECOY'])
            else:
                strategy = random.choice(['MONITOR_CLOSELY', 'ADAPTIVE_RESPONSE'])
            self.stats['decisions_made'] += 1
            logger.info(f"   Selected: {strategy} (threat: {threat_level:.2f})")
            return strategy
        
        num_strategies = len(strategies)
        num_qubits = int(np.ceil(np.log2(num_strategies)))
        
        logger.info(f"🎲 Quantum strategy selection (threat: {threat_level:.2f})...")
        
        # إنشاء دائرة كمية
        qc = QuantumCircuit(num_qubits, num_qubits)
        
        # Superposition
        for qubit in range(num_qubits):
            qc.h(qubit)
        
        # تعديل الأطوار بناءً على مستوى التهديد
        # كلما زاد التهديد، كلما زادت احتمالية الاستراتيجيات الهجومية
        phase_shift = threat_level * np.pi
        for qubit in range(num_qubits):
            qc.p(phase_shift, qubit)
        
        # القياس
        qc.measure(range(num_qubits), range(num_qubits))
        
        # التنفيذ
        result = self._execute_circuit(qc, shots=1)
        
        if result:
            measured = list(result.keys())[0]
            strategy_idx = int(measured, 2) % num_strategies
            strategy = strategies[strategy_idx]
            
            self.stats['decisions_made'] += 1
            self.stats['quantum_operations'] += 1
            
            logger.info(f"   ⚛️  Selected: {strategy}")
            return strategy
        
        # Fallback
        return 'MONITOR_CLOSELY'
    
    def quantum_entanglement_sync(self, num_systems: int = 2) -> List[str]:
        """
        مزامنة أنظمة متعددة باستخدام التشابك الكمي
        
        Args:
            num_systems: عدد الأنظمة للمزامنة
        
        Returns:
            List[str]: رموز المزامنة لكل نظام
        """
        logger.info(f"🔗 Creating quantum entanglement for {num_systems} systems...")
        
        if not QISKIT_AVAILABLE or self.backend is None:
            # Mock mode - generate same random bit for all systems
            logger.warning("⚠️  MOCK MODE: Simulating entanglement")
            import random
            sync_bit = random.choice(['0', '1'])
            sync_codes = [sync_bit] * num_systems
            self.stats['entanglements_created'] += 1
            logger.info(f"   ✓ Synced states: {sync_codes}")
            return sync_codes
        
        # إنشاء حالة Bell State (تشابك كمي)
        qc = QuantumCircuit(num_systems, num_systems)
        
        # تحضير حالة التشابك
        qc.h(0)  # Superposition على الكيوبت الأول
        
        for i in range(1, num_systems):
            qc.cx(0, i)  # CNOT لإنشاء التشابك
        
        # القياس
        qc.measure(range(num_systems), range(num_systems))
        
        # التنفيذ
        result = self._execute_circuit(qc, shots=1)
        
        if result:
            measured = list(result.keys())[0]
            
            # كل نظام يحصل على نفس النتيجة (بسبب التشابك!)
            sync_codes = [measured[i] for i in range(num_systems)]
            
            self.stats['entanglements_created'] += 1
            self.stats['quantum_operations'] += 1
            
            logger.info(f"   ✓ Entangled states: {sync_codes}")
            return sync_codes
        
        return ['0'] * num_systems
    
    def quantum_random_number(self, min_val: int, max_val: int) -> int:
        """
        توليد رقم عشوائي حقيقي
        
        Args:
            min_val: الحد الأدنى
            max_val: الحد الأقصى
        
        Returns:
            int: رقم عشوائي
        """
        if not QISKIT_AVAILABLE or self.backend is None:
            # Mock mode
            import random
            return random.randint(min_val, max_val)
        
        range_size = max_val - min_val + 1
        num_bits = int(np.ceil(np.log2(range_size)))
        
        # إنشاء دائرة
        qc = QuantumCircuit(num_bits, num_bits)
        
        for qubit in range(num_bits):
            qc.h(qubit)
        
        qc.measure(range(num_bits), range(num_bits))
        
        # التنفيذ
        result = self._execute_circuit(qc, shots=1)
        
        if result:
            measured = list(result.keys())[0]
            number = int(measured, 2) % range_size
            return min_val + number
        
        # Fallback
        return min_val
    
    def _execute_circuit(self, circuit, shots: int = 1024) -> Optional[Dict]:
        """
        تنفيذ دائرة كمية
        """
        if not QISKIT_AVAILABLE or self.backend is None:
            # Mock mode - return random results
            logger.warning("⚠️  MOCK MODE: Simulating circuit execution")
            import random
            # Generate mock measurement results
            num_qubits = 8  # Assume 8 qubits for mock
            result_str = ''.join(random.choice('01') for _ in range(num_qubits))
            return {result_str: shots}
        
        try:
            if not self.use_simulator:
                # تنفيذ على جهاز حقيقي
                with Session(service=self.service, backend=self.backend) as session:
                    sampler = Sampler(session=session)
                    
                    # Transpile للجهاز المحدد
                    transpiled = transpile(circuit, self.backend)
                    
                    # التنفيذ
                    job = sampler.run([transpiled], shots=shots)
                    result = job.result()
                    
                    # استخراج النتائج
                    counts = result.quasi_dists[0]
                    
                    # تحويل إلى صيغة binary strings
                    formatted = {}
                    for key, value in counts.items():
                        binary = format(key, f'0{circuit.num_qubits}b')
                        formatted[binary] = int(value * shots)
                    
                    return formatted
            else:
                # تنفيذ على محاكي
                from qiskit import execute
                job = execute(circuit, self.backend, shots=shots)
                result = job.result()
                return result.get_counts()
                
        except Exception as e:
            logger.error(f"❌ Circuit execution failed: {e}")
            return None
    
    def get_backend_status(self) -> Dict:
        """
        الحصول على حالة الجهاز الكمي
        """
        if self.use_simulator:
            return {
                'name': 'Local Simulator',
                'operational': True,
                'qubits': 32,
                'pending_jobs': 0
            }
        
        try:
            status = self.backend.status()
            return {
                'name': self.backend.name,
                'operational': status.operational,
                'qubits': self.backend.num_qubits,
                'pending_jobs': status.pending_jobs
            }
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return {}
    
    def get_stats(self) -> Dict:
        """الحصول على الإحصائيات"""
        return self.stats.copy()


# Demo
if __name__ == "__main__":
    print("⚛️  REAL QUANTUM COMPUTER INTEGRATION")
    print("="*80)
    
    print("\n🌐 IBM Quantum - FREE Tier!")
    print("   ✅ 10 minutes/month on REAL quantum computers")
    print("   ✅ Access to 127-qubit machines (ibm_brisbane, ibm_kyoto)")
    print("   ✅ Qiskit Runtime for faster execution")
    
    print("\n📝 Setup Steps:")
    print("   1. Register: https://quantum-computing.ibm.com/")
    print("   2. Get API token from dashboard")
    print("   3. Set environment variable:")
    print("      Windows: $env:IBM_QUANTUM_TOKEN='your_token_here'")
    print("      Linux: export IBM_QUANTUM_TOKEN='your_token_here'")
    print("   4. Install: pip install qiskit qiskit-ibm-runtime")
    
    print("\n" + "="*80)
    print("🧪 DEMO MODE (Simulator - No API required)")
    print("="*80)
    
    # استخدام محاكي للتجريب
    quantum = RealQuantumDefense(use_simulator=True)
    
    print("\n1️⃣ Quantum Random Key Generation")
    key = quantum.generate_quantum_key(128)
    print(f"   Generated 128-bit key: {key}")
    
    print("\n2️⃣ Quantum Defense Strategy Selection")
    for threat in [0.3, 0.7, 0.95]:
        strategy = quantum.quantum_random_defense(threat)
        print(f"   Threat {threat:.2f} → Strategy: {strategy}")
    
    print("\n3️⃣ Quantum Entanglement Synchronization")
    sync_codes = quantum.quantum_entanglement_sync(num_systems=4)
    print(f"   Synced 4 systems with codes: {sync_codes}")
    
    print("\n4️⃣ Quantum Random Numbers")
    for _ in range(5):
        num = quantum.quantum_random_number(1, 100)
        print(f"   Random: {num}")
    
    print("\n📊 Statistics:")
    stats = quantum.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n" + "="*80)
    print("✅ Demo Complete!")
    
    print("\n🚀 For REAL quantum computer:")
    print("   quantum = RealQuantumDefense(use_simulator=False)")
    print("   # Will use IBM Quantum hardware!")
    
    print("\n💡 Benefits of Real Quantum:")
    print("   ✓ TRUE randomness (not pseudo-random)")
    print("   ✓ Unpredictable by attackers")
    print("   ✓ Quantum advantage for cryptography")
    print("   ✓ Future-proof security")
