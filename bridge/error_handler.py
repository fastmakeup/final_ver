"""
통합 에러 핸들링 시스템
모든 모듈의 에러를 통일된 형식으로 변환
"""
from typing import TypedDict, Literal
from datetime import datetime
import traceback
import uuid


class ErrorResponse(TypedDict):
    """통일된 에러 응답 형식"""
    success: bool  # 항상 False
    error_type: Literal[
        'BE_PARSE_ERROR',      # BE 파싱 실패
        'AI_TIMEOUT',          # AI 응답 시간 초과
        'AI_CONNECTION_ERROR', # AI 서버 연결 실패
        'INVALID_INPUT',       # 잘못된 입력
        'FILE_NOT_FOUND',      # 파일 없음
        'PERMISSION_DENIED',   # 권한 없음
        'UNKNOWN_ERROR'        # 알 수 없는 에러
    ]
    error_message: str  # 사용자 친화적 메시지
    detail: str  # 개발자용 상세 정보
    timestamp: str  # ISO 8601 형식
    request_id: str  # 디버깅용 고유 ID


def generate_request_id() -> str:
    """요청 ID 생성"""
    return str(uuid.uuid4())[:8]


def handle_be_error(e: Exception, context: str = "") -> ErrorResponse:
    """
    BE 에러를 표준 형식으로 변환
    
    Args:
        e: 발생한 예외
        context: 에러 발생 컨텍스트
        
    Returns:
        ErrorResponse
    """
    error_type = 'BE_PARSE_ERROR'
    user_message = "문서 분석 중 오류가 발생했습니다"
    
    # 에러 타입별 메시지 커스터마이징
    if isinstance(e, FileNotFoundError):
        error_type = 'FILE_NOT_FOUND'
        user_message = "파일을 찾을 수 없습니다"
    elif isinstance(e, PermissionError):
        error_type = 'PERMISSION_DENIED'
        user_message = "파일 접근 권한이 없습니다"
    
    return {
        'success': False,
        'error_type': error_type,
        'error_message': user_message,
        'detail': f"{context}: {str(e)}\n{traceback.format_exc()}",
        'timestamp': datetime.now().isoformat(),
        'request_id': generate_request_id()
    }


def handle_ai_error(e: Exception, context: str = "") -> ErrorResponse:
    """
    AI 에러를 표준 형식으로 변환
    
    Args:
        e: 발생한 예외
        context: 에러 발생 컨텍스트
        
    Returns:
        ErrorResponse
    """
    error_type = 'AI_CONNECTION_ERROR'
    user_message = "AI 검색 중 오류가 발생했습니다"
    
    # 타임아웃 감지
    if 'timeout' in str(e).lower():
        error_type = 'AI_TIMEOUT'
        user_message = "AI 응답 시간이 초과되었습니다. 다시 시도해주세요"
    
    return {
        'success': False,
        'error_type': error_type,
        'error_message': user_message,
        'detail': f"{context}: {str(e)}\n{traceback.format_exc()}",
        'timestamp': datetime.now().isoformat(),
        'request_id': generate_request_id()
    }


def handle_bridge_error(e: Exception, context: str = "") -> ErrorResponse:
    """
    Bridge 에러를 표준 형식으로 변환
    
    Args:
        e: 발생한 예외
        context: 에러 발생 컨텍스트
        
    Returns:
        ErrorResponse
    """
    return {
        'success': False,
        'error_type': 'UNKNOWN_ERROR',
        'error_message': "시스템 오류가 발생했습니다",
        'detail': f"{context}: {str(e)}\n{traceback.format_exc()}",
        'timestamp': datetime.now().isoformat(),
        'request_id': generate_request_id()
    }


def handle_validation_error(message: str) -> ErrorResponse:
    """
    입력 검증 에러
    
    Args:
        message: 에러 메시지
        
    Returns:
        ErrorResponse
    """
    return {
        'success': False,
        'error_type': 'INVALID_INPUT',
        'error_message': message,
        'detail': message,
        'timestamp': datetime.now().isoformat(),
        'request_id': generate_request_id()
    }


if __name__ == "__main__":
    # 테스트 코드
    print("=" * 60)
    print("에러 핸들링 테스트")
    print("=" * 60)
    
    # BE 에러 시뮬레이션
    try:
        raise FileNotFoundError("01_기안.hwp")
    except Exception as e:
        error = handle_be_error(e, "폴더 분석")
        print("\n[BE 에러]")
        print(f"  타입: {error['error_type']}")
        print(f"  메시지: {error['error_message']}")
        print(f"  ID: {error['request_id']}")
    
    # AI 에러 시뮬레이션
    try:
        raise TimeoutError("AI 서버 응답 없음")
    except Exception as e:
        error = handle_ai_error(e, "AI 검색")
        print("\n[AI 에러]")
        print(f"  타입: {error['error_type']}")
        print(f"  메시지: {error['error_message']}")
        print(f"  ID: {error['request_id']}")
    
    # 검증 에러
    error = handle_validation_error("폴더 경로가 비어있습니다")
    print("\n[검증 에러]")
    print(f"  타입: {error['error_type']}")
    print(f"  메시지: {error['error_message']}")
    print(f"  ID: {error['request_id']}")
    
    print("\n[OK] 에러 핸들링 테스트 완료")
