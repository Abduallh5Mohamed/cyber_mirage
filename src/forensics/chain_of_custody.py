"""
Chain of Custody - سلسلة الحفظ
Cyber Mirage Forensics Module

يقوم بـ:
- توثيق سلسلة حفظ الأدلة
- تتبع من تعامل مع الأدلة
- ضمان سلامة الأدلة
"""

import json
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CustodyAction(Enum):
    """أنواع الإجراءات على الأدلة"""
    COLLECTED = "collected"
    TRANSFERRED = "transferred"
    ANALYZED = "analyzed"
    COPIED = "copied"
    STORED = "stored"
    RETRIEVED = "retrieved"
    SEALED = "sealed"
    UNSEALED = "unsealed"
    VERIFIED = "verified"
    DISPOSED = "disposed"


class EvidenceStatus(Enum):
    """حالة الدليل"""
    ACTIVE = "active"
    SEALED = "sealed"
    ANALYZED = "analyzed"
    ARCHIVED = "archived"
    DISPOSED = "disposed"


@dataclass
class CustodyEntry:
    """سجل في سلسلة الحفظ"""
    entry_id: str
    timestamp: str
    action: str
    performed_by: str
    location: str
    notes: str
    hash_before: Optional[str] = None
    hash_after: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class EvidenceItem:
    """عنصر دليل"""
    evidence_id: str
    case_id: str
    description: str
    source: str
    file_path: Optional[str]
    collected_at: str
    collected_by: str
    original_hash: str
    current_hash: str
    status: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    custody_chain: List[CustodyEntry] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['custody_chain'] = [e.to_dict() if hasattr(e, 'to_dict') else e for e in self.custody_chain]
        return data


class ChainOfCustody:
    """
    إدارة سلسلة حفظ الأدلة الرقمية
    """
    
    def __init__(self, case_id: str, investigator: str, organization: str = "Cyber Mirage"):
        """
        Initialize chain of custody manager
        
        Args:
            case_id: معرف القضية
            investigator: اسم المحقق
            organization: المنظمة
        """
        self.case_id = case_id
        self.investigator = investigator
        self.organization = organization
        self.evidence_items: Dict[str, EvidenceItem] = {}
        self.created_at = datetime.now().isoformat()
        
        logger.info(f"Chain of Custody initialized for case: {case_id}")
    
    def _generate_id(self) -> str:
        """توليد معرف فريد"""
        return f"EV-{uuid.uuid4().hex[:8].upper()}"
    
    def _calculate_hash(self, file_path: str, algorithm: str = "sha256") -> str:
        """
        حساب Hash للملف
        
        Args:
            file_path: مسار الملف
            algorithm: خوارزمية الـ Hash
        
        Returns:
            قيمة الـ Hash
        """
        try:
            hash_func = getattr(hashlib, algorithm)()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash: {e}")
            return "HASH_ERROR"
    
    def add_evidence(self,
                     description: str,
                     source: str,
                     file_path: str = None,
                     collected_by: str = None,
                     location: str = "Digital Collection",
                     metadata: Dict = None) -> EvidenceItem:
        """
        إضافة دليل جديد
        
        Args:
            description: وصف الدليل
            source: مصدر الدليل
            file_path: مسار الملف
            collected_by: من جمع الدليل
            location: موقع الجمع
            metadata: بيانات وصفية إضافية
        
        Returns:
            عنصر الدليل
        """
        evidence_id = self._generate_id()
        collector = collected_by or self.investigator
        timestamp = datetime.now().isoformat()
        
        # حساب Hash إذا كان ملف
        original_hash = ""
        file_size = None
        if file_path and Path(file_path).exists():
            original_hash = self._calculate_hash(file_path)
            file_size = Path(file_path).stat().st_size
        
        evidence = EvidenceItem(
            evidence_id=evidence_id,
            case_id=self.case_id,
            description=description,
            source=source,
            file_path=file_path,
            collected_at=timestamp,
            collected_by=collector,
            original_hash=original_hash,
            current_hash=original_hash,
            status=EvidenceStatus.ACTIVE.value,
            file_size=file_size,
            metadata=metadata or {},
            custody_chain=[]
        )
        
        # إضافة أول سجل في سلسلة الحفظ
        first_entry = CustodyEntry(
            entry_id=f"CE-{uuid.uuid4().hex[:6].upper()}",
            timestamp=timestamp,
            action=CustodyAction.COLLECTED.value,
            performed_by=collector,
            location=location,
            notes=f"Initial collection of evidence: {description}",
            hash_after=original_hash
        )
        evidence.custody_chain.append(first_entry)
        
        self.evidence_items[evidence_id] = evidence
        logger.info(f"Evidence added: {evidence_id} - {description}")
        
        return evidence
    
    def transfer_evidence(self,
                          evidence_id: str,
                          transferred_to: str,
                          new_location: str,
                          notes: str = "") -> CustodyEntry:
        """
        نقل دليل لشخص آخر
        
        Args:
            evidence_id: معرف الدليل
            transferred_to: المستلم
            new_location: الموقع الجديد
            notes: ملاحظات
        
        Returns:
            سجل النقل
        """
        if evidence_id not in self.evidence_items:
            raise ValueError(f"Evidence {evidence_id} not found")
        
        evidence = self.evidence_items[evidence_id]
        timestamp = datetime.now().isoformat()
        
        # التحقق من سلامة الدليل
        current_hash = ""
        if evidence.file_path and Path(evidence.file_path).exists():
            current_hash = self._calculate_hash(evidence.file_path)
        
        entry = CustodyEntry(
            entry_id=f"CE-{uuid.uuid4().hex[:6].upper()}",
            timestamp=timestamp,
            action=CustodyAction.TRANSFERRED.value,
            performed_by=f"{self._get_current_custodian(evidence)} → {transferred_to}",
            location=new_location,
            notes=notes,
            hash_before=evidence.current_hash,
            hash_after=current_hash
        )
        
        evidence.custody_chain.append(entry)
        evidence.current_hash = current_hash
        
        logger.info(f"Evidence {evidence_id} transferred to {transferred_to}")
        
        return entry
    
    def analyze_evidence(self,
                         evidence_id: str,
                         analyst: str,
                         analysis_type: str,
                         findings: str = "") -> CustodyEntry:
        """
        تسجيل تحليل الدليل
        
        Args:
            evidence_id: معرف الدليل
            analyst: المحلل
            analysis_type: نوع التحليل
            findings: النتائج
        
        Returns:
            سجل التحليل
        """
        if evidence_id not in self.evidence_items:
            raise ValueError(f"Evidence {evidence_id} not found")
        
        evidence = self.evidence_items[evidence_id]
        timestamp = datetime.now().isoformat()
        
        entry = CustodyEntry(
            entry_id=f"CE-{uuid.uuid4().hex[:6].upper()}",
            timestamp=timestamp,
            action=CustodyAction.ANALYZED.value,
            performed_by=analyst,
            location="Analysis Lab",
            notes=f"Analysis Type: {analysis_type}. Findings: {findings}",
            hash_before=evidence.current_hash,
            hash_after=evidence.current_hash
        )
        
        evidence.custody_chain.append(entry)
        evidence.status = EvidenceStatus.ANALYZED.value
        
        logger.info(f"Evidence {evidence_id} analyzed by {analyst}")
        
        return entry
    
    def verify_integrity(self, evidence_id: str) -> Dict[str, Any]:
        """
        التحقق من سلامة الدليل
        
        Args:
            evidence_id: معرف الدليل
        
        Returns:
            نتيجة التحقق
        """
        if evidence_id not in self.evidence_items:
            return {"valid": False, "error": "Evidence not found"}
        
        evidence = self.evidence_items[evidence_id]
        
        result = {
            "evidence_id": evidence_id,
            "verified_at": datetime.now().isoformat(),
            "original_hash": evidence.original_hash,
            "stored_current_hash": evidence.current_hash,
            "valid": False,
            "integrity_status": "UNKNOWN"
        }
        
        if evidence.file_path and Path(evidence.file_path).exists():
            actual_hash = self._calculate_hash(evidence.file_path)
            result["actual_current_hash"] = actual_hash
            
            if actual_hash == evidence.original_hash:
                result["valid"] = True
                result["integrity_status"] = "INTACT - No modifications detected"
            elif actual_hash == evidence.current_hash:
                result["valid"] = True
                result["integrity_status"] = "VALID - Hash matches last known state"
            else:
                result["valid"] = False
                result["integrity_status"] = "COMPROMISED - Hash mismatch detected!"
        else:
            result["integrity_status"] = "FILE_NOT_FOUND"
        
        # إضافة سجل التحقق
        entry = CustodyEntry(
            entry_id=f"CE-{uuid.uuid4().hex[:6].upper()}",
            timestamp=datetime.now().isoformat(),
            action=CustodyAction.VERIFIED.value,
            performed_by=self.investigator,
            location="Verification System",
            notes=f"Integrity check: {result['integrity_status']}",
            hash_before=evidence.current_hash,
            hash_after=result.get("actual_current_hash", "")
        )
        evidence.custody_chain.append(entry)
        
        logger.info(f"Evidence {evidence_id} verified: {result['integrity_status']}")
        
        return result
    
    def seal_evidence(self, evidence_id: str, reason: str = "") -> CustodyEntry:
        """
        ختم الدليل (منع التعديل)
        
        Args:
            evidence_id: معرف الدليل
            reason: سبب الختم
        
        Returns:
            سجل الختم
        """
        if evidence_id not in self.evidence_items:
            raise ValueError(f"Evidence {evidence_id} not found")
        
        evidence = self.evidence_items[evidence_id]
        timestamp = datetime.now().isoformat()
        
        entry = CustodyEntry(
            entry_id=f"CE-{uuid.uuid4().hex[:6].upper()}",
            timestamp=timestamp,
            action=CustodyAction.SEALED.value,
            performed_by=self.investigator,
            location="Evidence Vault",
            notes=f"Evidence sealed. Reason: {reason}",
            hash_before=evidence.current_hash,
            hash_after=evidence.current_hash
        )
        
        evidence.custody_chain.append(entry)
        evidence.status = EvidenceStatus.SEALED.value
        
        logger.info(f"Evidence {evidence_id} sealed")
        
        return entry
    
    def _get_current_custodian(self, evidence: EvidenceItem) -> str:
        """الحصول على الحافظ الحالي للدليل"""
        if evidence.custody_chain:
            last_entry = evidence.custody_chain[-1]
            if "→" in last_entry.performed_by:
                return last_entry.performed_by.split("→")[-1].strip()
            return last_entry.performed_by
        return evidence.collected_by
    
    def get_evidence_history(self, evidence_id: str) -> List[Dict]:
        """
        الحصول على تاريخ الدليل الكامل
        
        Args:
            evidence_id: معرف الدليل
        
        Returns:
            قائمة سجلات سلسلة الحفظ
        """
        if evidence_id not in self.evidence_items:
            return []
        
        evidence = self.evidence_items[evidence_id]
        return [
            entry.to_dict() if hasattr(entry, 'to_dict') else entry
            for entry in evidence.custody_chain
        ]
    
    def get_case_summary(self) -> Dict[str, Any]:
        """
        ملخص القضية
        
        Returns:
            ملخص شامل
        """
        return {
            "case_id": self.case_id,
            "investigator": self.investigator,
            "organization": self.organization,
            "created_at": self.created_at,
            "total_evidence": len(self.evidence_items),
            "evidence_by_status": self._count_by_status(),
            "evidence_items": [
                {
                    "id": e.evidence_id,
                    "description": e.description,
                    "status": e.status,
                    "collected_at": e.collected_at,
                    "custody_entries": len(e.custody_chain)
                }
                for e in self.evidence_items.values()
            ]
        }
    
    def _count_by_status(self) -> Dict[str, int]:
        """عد الأدلة حسب الحالة"""
        counts = {}
        for evidence in self.evidence_items.values():
            counts[evidence.status] = counts.get(evidence.status, 0) + 1
        return counts
    
    def export_json(self, file_path: str) -> str:
        """
        تصدير سلسلة الحفظ لملف JSON
        
        Args:
            file_path: مسار الملف
        
        Returns:
            مسار الملف
        """
        export_data = {
            "chain_of_custody": {
                "case_id": self.case_id,
                "investigator": self.investigator,
                "organization": self.organization,
                "created_at": self.created_at,
                "exported_at": datetime.now().isoformat(),
                "evidence_count": len(self.evidence_items)
            },
            "evidence_items": [
                e.to_dict() for e in self.evidence_items.values()
            ]
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Chain of custody exported to {file_path}")
        return file_path
    
    def generate_report(self) -> str:
        """
        توليد تقرير سلسلة الحفظ
        
        Returns:
            التقرير النصي
        """
        summary = self.get_case_summary()
        
        report = f"""
╔══════════════════════════════════════════════════════════════════╗
║           CYBER MIRAGE - CHAIN OF CUSTODY REPORT                 ║
╠══════════════════════════════════════════════════════════════════╣
║  Case ID: {self.case_id:<52} ║
║  Investigator: {self.investigator:<47} ║
║  Organization: {self.organization:<47} ║
║  Created: {self.created_at:<53} ║
╠══════════════════════════════════════════════════════════════════╣

📊 CASE SUMMARY:
═══════════════════════════════════════════════════════════════════
  Total Evidence Items: {summary['total_evidence']}
  
  By Status:
"""
        for status, count in summary['evidence_by_status'].items():
            icon = {
                "active": "🟢",
                "sealed": "🔒",
                "analyzed": "🔍",
                "archived": "📦",
                "disposed": "🗑️"
            }.get(status, "⚪")
            report += f"    {icon} {status.upper()}: {count}\n"
        
        report += "\n📋 EVIDENCE ITEMS:\n"
        report += "═" * 67 + "\n"
        
        for evidence in self.evidence_items.values():
            report += f"""
  📁 {evidence.evidence_id}
     Description: {evidence.description[:50]}...
     Source: {evidence.source}
     Status: {evidence.status.upper()}
     Collected: {evidence.collected_at}
     Hash: {evidence.original_hash[:16]}...
     Custody Chain: {len(evidence.custody_chain)} entries
"""
            
            # آخر 3 سجلات في سلسلة الحفظ
            report += "     Recent Custody Actions:\n"
            for entry in evidence.custody_chain[-3:]:
                entry_dict = entry.to_dict() if hasattr(entry, 'to_dict') else entry
                report += f"       - [{entry_dict['timestamp'][:19]}] {entry_dict['action'].upper()}\n"
                report += f"         By: {entry_dict['performed_by']}\n"
        
        report += """
═══════════════════════════════════════════════════════════════════
  This Chain of Custody report certifies the handling and 
  integrity of all evidence items listed above.
  
  Report Generated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
╚══════════════════════════════════════════════════════════════════╝
"""
        return report


if __name__ == "__main__":
    # اختبار
    coc = ChainOfCustody(
        case_id="CASE_2025_001",
        investigator="Ahmed Mohamed",
        organization="Cyber Mirage Team"
    )
    print(f"Chain of Custody initialized: {coc.case_id}")
