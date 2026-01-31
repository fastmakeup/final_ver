# -*- coding: utf-8 -*-
"""
저사양 환경 검증 스크립트
LOW_SPEC_TEST.md의 체크리스트 자동 검증
"""

import os
import sys
import time
import psutil
import traceback
from pathlib import Path
from datetime import datetime


def get_build_size():
    """빌드 크기 측정"""
    try:
        dist_path = Path("dist/HandOverAI")
        
        if not dist_path.exists():
            return None, "빌드 폴더가 존재하지 않습니다"
        
        total_size = 0
        file_count = 0
        
        for file in dist_path.rglob("*"):
            if file.is_file():
                total_size += file.stat().st_size
                file_count += 1
        
        size_mb = total_size / (1024 * 1024)
        
        return {
            "total_size_mb": round(float(size_mb), 2),
            "file_count": file_count,
            "exe_path": str(dist_path / "HandOverAI.exe"),
            "exe_exists": (dist_path / "HandOverAI.exe").exists()
        }, None
    except Exception as e:
        return None, f"빌드 크기 측정 실패: {str(e)}"


def get_system_info():
    """시스템 정보 수집"""
    try:
        mem = psutil.virtual_memory()
        cpu_count = psutil.cpu_count(logical=False) or psutil.cpu_count() or 1
        
        return {
            "total_ram_gb": round(mem.total / (1024**3), 2),
            "available_ram_gb": round(mem.available / (1024**3), 2),
            "cpu_cores": cpu_count,
            "cpu_percent": psutil.cpu_percent(interval=1),
            "is_low_spec": mem.total / (1024**3) <= 6
        }, None
    except Exception as e:
        return None, f"시스템 정보 수집 실패: {str(e)}"


def measure_startup_time():
    """초기 로딩 시간 측정 (모듈 import)"""
    start = time.time()
    
    try:
        # 주요 모듈 import 시간 측정
        import webview
        import_time = time.time() - start
        
        return {
            "import_time_sec": round(import_time, 3),
            "status": "success"
        }, None
    except Exception as e:
        return None, f"모듈 로드 실패: {str(e)}"


def check_dependencies():
    """의존성 설치 확인"""
    try:
        import webview
        import typing_extensions
        
        return {
            "pywebview": webview.__version__ if hasattr(webview, '__version__') else "installed",
            "typing_extensions": "installed",
            "status": "all_installed"
        }, None
    except ImportError as e:
        return None, f"의존성 누락: {str(e)}"


def generate_report():
    """검증 리포트 생성"""
    try:
        # Windows 콘솔 UTF-8 출력 설정
        if sys.platform == 'win32':
            try:
                sys.stdout.reconfigure(encoding='utf-8')
            except:
                pass
        
        print("=" * 60)
        print("저사양 환경 검증 리포트")
        print("=" * 60)
        print(f"생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 1. 시스템 정보
        print("[시스템 정보]")
        print("-" * 60)
        sys_info, sys_error = get_system_info()
        if sys_error:
            print(f"  [X] {sys_error}")
            sys_info = {"total_ram_gb": 0, "available_ram_gb": 0, "cpu_cores": 0, "cpu_percent": 0, "is_low_spec": False}
        else:
            print(f"  RAM: {sys_info['total_ram_gb']} GB (사용 가능: {sys_info['available_ram_gb']} GB)")
            print(f"  CPU: {sys_info['cpu_cores']} Core (사용률: {sys_info['cpu_percent']}%)")
            print(f"  저사양 모드: {'예' if sys_info['is_low_spec'] else '아니오'}")
        print()
        
        # 2. 빌드 크기
        print("[빌드 크기]")
        print("-" * 60)
        build_info, error = get_build_size()
        if error:
            print(f"  [X] {error}")
            print(f"  [i] 먼저 handover.bat build를 실행하세요")
        else:
            print(f"  전체 크기: {build_info['total_size_mb']} MB")
            print(f"  파일 개수: {build_info['file_count']}개")
            print(f"  실행 파일: {'[O] 존재' if build_info['exe_exists'] else '[X] 없음'}")
            
            # 목표 달성 여부
            if build_info['total_size_mb'] <= 100:
                print(f"  [O] 목표 달성 (100MB 이하)")
            else:
                print(f"  [!] 목표 미달 (목표: 100MB, 현재: {build_info['total_size_mb']}MB)")
        print()
        
        # 3. 의존성 확인
        print("[의존성 확인]")
        print("-" * 60)
        deps, dep_error = check_dependencies()
        if dep_error:
            print(f"  [X] {dep_error}")
        else:
            print(f"  pywebview: {deps['pywebview']}")
            print(f"  typing_extensions: {deps['typing_extensions']}")
            print(f"  [O] 모든 의존성 설치됨")
        print()
        
        # 4. 성능 측정
        print("[성능 측정]")
        print("-" * 60)
        startup, st_error = measure_startup_time()
        if st_error:
            print(f"  [X] {st_error}")
        else:
            print(f"  모듈 로드 시간: {startup['import_time_sec']}초")
            if startup['import_time_sec'] <= 1.0:
                print(f"  [O] 빠른 로딩")
            else:
                print(f"  [!] 로딩 시간 개선 필요")
        print()
        
        # 5. 저사양 환경 적합성 평가
        print("[저사양 환경 적합성 평가]")
        print("-" * 60)
        
        checks = []
        if sys_info['total_ram_gb'] >= 4:
            checks.append(("RAM 4GB 이상", True))
        else:
            checks.append(("RAM 4GB 이상", False))
        
        if build_info and build_info['total_size_mb'] <= 100:
            checks.append(("빌드 크기 100MB 이하", True))
        else:
            checks.append(("빌드 크기 100MB 이하", False))
        
        if deps:
            checks.append(("의존성 설치 완료", True))
        else:
            checks.append(("의존성 설치 완료", False))
        
        for check_name, passed in checks:
            status = "[O]" if passed else "[X]"
            print(f"  {status} {check_name}")
        
        passed_count = sum(1 for _, passed in checks if passed)
        total_count = len(checks)
        
        print()
        print(f"  총 {passed_count}/{total_count} 항목 통과")
        
        if passed_count == total_count:
            print(f"  [SUCCESS] 저사양 환경 테스트 준비 완료!")
        else:
            print(f"  [WARNING] 일부 항목 미달성")
        
        print()
        print("=" * 60)
        
    except Exception:
        print("\n[ERROR] 리포트 생성 중 예상치 못한 오류 발생:")
        traceback.print_exc()


if __name__ == "__main__":
    generate_report()
