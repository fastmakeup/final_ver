"""
docs 폴더 관리 시스템
백업 플랜 및 실제 데이터 제공
"""
import os
from typing import List, Dict
from datetime import datetime


class DocsManager:
    """docs 폴더 관리 및 메타데이터 제공"""
    
    def __init__(self, docs_path: str = "./docs"):
        self.docs_path = docs_path
        self.files = self._scan_files()
    
    def _scan_files(self) -> List[Dict]:
        """docs 폴더 스캔"""
        if not os.path.exists(self.docs_path):
            print(f"[DocsManager] 경고: {self.docs_path} 폴더가 없습니다")
            return []
        
        files = []
        for filename in os.listdir(self.docs_path):
            if filename.endswith(('.hwp', '.hwpx', '.pdf')):
                filepath = os.path.join(self.docs_path, filename)
                try:
                    stat = os.stat(filepath)
                    files.append({
                        'filename': filename,
                        'path': filepath,
                        'size': stat.st_size,
                        'size_mb': round(stat.st_size / (1024 * 1024), 2),
                        'extension': os.path.splitext(filename)[1],
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                except Exception as e:
                    print(f"[DocsManager] 파일 정보 읽기 실패: {filename} - {e}")
        
        return sorted(files, key=lambda x: x['filename'])
    
    def get_file_list(self) -> List[str]:
        """파일명 목록 반환"""
        return [f['filename'] for f in self.files]
    
    def get_file_info(self, filename: str) -> Dict:
        """특정 파일 정보 반환"""
        for f in self.files:
            if f['filename'] == filename:
                return f
        return None
    
    def get_stats(self) -> Dict:
        """통계 정보 반환"""
        return {
            'total_files': len(self.files),
            'hwp_count': sum(1 for f in self.files if f['extension'] == '.hwp'),
            'hwpx_count': sum(1 for f in self.files if f['extension'] == '.hwpx'),
            'pdf_count': sum(1 for f in self.files if f['extension'] == '.pdf'),
            'total_size_mb': round(sum(f['size'] for f in self.files) / (1024 * 1024), 2)
        }
    
    def get_files_by_type(self, extension: str) -> List[Dict]:
        """확장자별 파일 필터링"""
        return [f for f in self.files if f['extension'] == extension]
    
    def print_summary(self):
        """요약 정보 출력"""
        stats = self.get_stats()
        
        print("\n" + "=" * 60)
        print("docs 폴더 요약")
        print("=" * 60)
        print(f"전체 파일: {stats['total_files']}개")
        print(f"  - HWP: {stats['hwp_count']}개")
        print(f"  - HWPX: {stats['hwpx_count']}개")
        print(f"  - PDF: {stats['pdf_count']}개")
        print(f"전체 크기: {stats['total_size_mb']} MB")
        print("\n파일 목록:")
        for f in self.files:
            print(f"  - {f['filename']} ({f['size_mb']} MB)")
        print("=" * 60)
    
    def get_demo_files(self, count: int = 3) -> List[str]:
        """
        데모용 파일 선택
        
        Args:
            count: 선택할 파일 개수
            
        Returns:
            파일 경로 리스트
        """
        # 크기가 작은 파일부터 선택 (빠른 데모)
        sorted_files = sorted(self.files, key=lambda x: x['size'])
        demo_files = sorted_files[:count]
        return [f['path'] for f in demo_files]


if __name__ == "__main__":
    # 테스트 코드
    print("=" * 60)
    print("docs 폴더 관리 시스템 테스트")
    print("=" * 60)
    
    manager = DocsManager()
    
    # 요약 출력
    manager.print_summary()
    
    # 통계 정보
    stats = manager.get_stats()
    print(f"\n[통계] 전체 {stats['total_files']}개 파일, {stats['total_size_mb']} MB")
    
    # 파일 타입별 필터링
    hwp_files = manager.get_files_by_type('.hwp')
    print(f"\n[HWP 파일] {len(hwp_files)}개")
    for f in hwp_files:
        print(f"  - {f['filename']}")
    
    # 데모용 파일 선택
    demo_files = manager.get_demo_files(3)
    print(f"\n[데모 파일] {len(demo_files)}개 선택")
    for path in demo_files:
        print(f"  - {os.path.basename(path)}")
    
    print("\n[OK] docs 관리 시스템 테스트 완료")
