"""
성능 모니터링 시스템
각 작업의 실행 시간 측정 및 리포트 생성
"""
import time
from contextlib import contextmanager
from typing import Dict
from datetime import datetime


class PerformanceMonitor:
    """성능 모니터링 클래스"""
    
    def __init__(self):
        self.metrics: Dict[str, float] = {}
        self.start_time = time.time()
    
    @contextmanager
    def measure(self, operation: str):
        """
        작업 시간 측정 컨텍스트 매니저
        
        사용 예시:
            with monitor.measure("BE_PARSING"):
                result = parse_hwp(file)
        
        Args:
            operation: 작업 이름
        """
        start = time.time()
        try:
            yield
        finally:
            elapsed = time.time() - start
            self.metrics[operation] = elapsed
            print(f"[Performance] {operation}: {elapsed:.2f}s")
    
    def record(self, operation: str, elapsed: float):
        """
        수동으로 시간 기록
        
        Args:
            operation: 작업 이름
            elapsed: 소요 시간 (초)
        """
        self.metrics[operation] = elapsed
        print(f"[Performance] {operation}: {elapsed:.2f}s")
    
    def get_report(self) -> dict:
        """
        성능 리포트 생성
        
        Returns:
            {
                'total_time': 전체 소요 시간,
                'breakdown': 작업별 소요 시간,
                'slowest': 가장 느린 작업,
                'timestamp': 리포트 생성 시각
            }
        """
        total_time = sum(self.metrics.values())
        
        # 가장 느린 작업 찾기
        slowest = max(self.metrics.items(), key=lambda x: x[1]) if self.metrics else ("N/A", 0)
        
        return {
            'total_time': round(total_time, 2),
            'breakdown': {k: round(v, 2) for k, v in self.metrics.items()},
            'slowest': {
                'operation': slowest[0],
                'time': round(slowest[1], 2)
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def print_report(self):
        """리포트 출력"""
        report = self.get_report()
        
        print("\n" + "=" * 60)
        print("성능 리포트")
        print("=" * 60)
        print(f"전체 소요 시간: {report['total_time']}초")
        print(f"\n작업별 소요 시간:")
        for op, t in report['breakdown'].items():
            percentage = (t / report['total_time'] * 100) if report['total_time'] > 0 else 0
            print(f"  - {op}: {t}초 ({percentage:.1f}%)")
        print(f"\n가장 느린 작업: {report['slowest']['operation']} ({report['slowest']['time']}초)")
        print("=" * 60)
    
    def reset(self):
        """메트릭 초기화"""
        self.metrics.clear()
        self.start_time = time.time()


# 전역 모니터 인스턴스
global_monitor = PerformanceMonitor()


if __name__ == "__main__":
    # 테스트 코드
    print("=" * 60)
    print("성능 모니터링 테스트")
    print("=" * 60)
    
    monitor = PerformanceMonitor()
    
    # 작업 1: BE 파싱 시뮬레이션
    with monitor.measure("BE_PARSING"):
        time.sleep(0.5)
    
    # 작업 2: 어댑터 변환 시뮬레이션
    with monitor.measure("ADAPTER_CONVERSION"):
        time.sleep(0.1)
    
    # 작업 3: AI 검색 시뮬레이션
    with monitor.measure("AI_SEARCH"):
        time.sleep(0.3)
    
    # 작업 4: 캐싱 시뮬레이션
    with monitor.measure("CACHING"):
        time.sleep(0.05)
    
    # 리포트 출력
    monitor.print_report()
    
    # JSON 형식으로도 가져올 수 있음
    import json
    print("\nJSON 형식:")
    print(json.dumps(monitor.get_report(), indent=2, ensure_ascii=False))
