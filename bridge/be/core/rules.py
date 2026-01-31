from typing import List, Dict, Optional


class DocumentValidator:
    """문서 검증 엔진"""
    
    def __init__(self, documents: List[Dict]):
        """
        Args:
            documents: process_document()로 처리된 문서 리스트
            [
                {
                    "filename": "01_기안.hwp",
                    "type": "기안",
                    "dates": ["2024.03.01"],
                    "amounts": [{"text": "50,000,000원", "amount": 50000000}],
                    "raw_text": "..."
                },
                ...
            ]
        """
        self.documents = documents
        self.warnings = []
        self.errors = []
        
    
    def validate_all(self) -> Dict:
        """
        모든 검증 실행
        
        Returns:
            {
                "status": "ok" | "warning" | "error",
                "warnings": [...],
                "errors": [...],
                "summary": "..."
            }
        """
        # 1. 문서 타입별 그룹화
        docs_by_type = self._group_by_type()
        
        # 2. 각종 검증 실행
        self._check_required_documents(docs_by_type)
        self._check_amount_consistency(docs_by_type)
        self._check_date_order(docs_by_type)
        self._check_design_change_pair(docs_by_type)
        
        # 3. 결과 반환
        status = "error" if self.errors else ("warning" if self.warnings else "ok")
        
        return {
            "status": status,
            "warnings": self.warnings,
            "errors": self.errors,
            "summary": self._generate_summary()
        }
    
    
    def _group_by_type(self) -> Dict[str, List[Dict]]:
        """문서 타입별로 그룹화"""
        groups = {}
        
        for doc in self.documents:
            doc_type = doc['type']
            if doc_type not in groups:
                groups[doc_type] = []
            groups[doc_type].append(doc)
        
        return groups
    
    
    def _check_required_documents(self, docs_by_type: Dict):
        """필수 문서 존재 확인"""
        
        # 기안서가 있으면 계약서도 있어야 함
        if '기안' in docs_by_type and '계약서' not in docs_by_type:
            self.warnings.append({
                "type": "missing_document",
                "message": "기안서는 있는데 계약서가 없습니다",
                "severity": "warning"
            })
    
    
    def _check_amount_consistency(self, docs_by_type: Dict):
        """기안서와 계약서의 금액 일치 확인"""
        
        if '기안' not in docs_by_type or '계약서' not in docs_by_type:
            return
        
        # 첫 번째 기안서와 계약서 비교
        기안 = docs_by_type['기안'][0]
        계약서 = docs_by_type['계약서'][0]
        
        # 금액 추출
        기안_금액 = 기안['amounts'][0]['amount'] if 기안['amounts'] else None
        계약_금액 = 계약서['amounts'][0]['amount'] if 계약서['amounts'] else None
        
        if 기안_금액 and 계약_금액:
            if 기안_금액 != 계약_금액:
                self.errors.append({
                    "type": "amount_mismatch",
                    "message": f"기안서 금액({기안_금액:,}원)과 계약서 금액({계약_금액:,}원)이 다릅니다",
                    "severity": "error"
                })
    
    
    def _check_date_order(self, docs_by_type: Dict):
        """날짜 순서 확인 (기안 → 계약)"""
        
        if '기안' not in docs_by_type or '계약서' not in docs_by_type:
            return
        
        기안 = docs_by_type['기안'][0]
        계약서 = docs_by_type['계약서'][0]
        
        기안_날짜 = 기안['dates'][0] if 기안['dates'] else None
        계약_날짜 = 계약서['dates'][0] if 계약서['dates'] else None
        
        if 기안_날짜 and 계약_날짜:
            # 날짜 비교 (2024.03.01 형식)
            if 기안_날짜 > 계약_날짜:
                self.warnings.append({
                    "type": "date_order",
                    "message": f"기안 날짜({기안_날짜})가 계약 날짜({계약_날짜})보다 늦습니다",
                    "severity": "warning"
                })
    
    
    def _check_design_change_pair(self, docs_by_type: Dict):
        """설계변경 기안 + 변경계약서 쌍 확인"""
        
        if '설계변경' in docs_by_type and '변경' not in docs_by_type:
            self.warnings.append({
                "type": "missing_change_contract",
                "message": "설계변경 기안은 있는데 변경계약서가 없습니다",
                "severity": "warning"
            })
    
    
    def _generate_summary(self) -> str:
        """검증 결과 요약"""
        
        total_docs = len(self.documents)
        error_count = len(self.errors)
        warning_count = len(self.warnings)
        
        if error_count > 0:
            return f"❌ {total_docs}개 문서 검증 완료: {error_count}개 오류, {warning_count}개 경고"
        elif warning_count > 0:
            return f"⚠️ {total_docs}개 문서 검증 완료: {warning_count}개 경고"
        else:
            return f"✅ {total_docs}개 문서 검증 완료: 문제 없음"


if __name__ == "__main__":
    # 간단한 테스트
    print("✅ rules.py 로드 완료")