import olefile
import zipfile
import zlib
import re
from pathlib import Path


def extract_text_from_hwp(file_path: str) -> str:
    """HWP 파일에서 텍스트 추출"""
    try:
        ole = olefile.OleFileIO(file_path)
        extracted_text = []
        
        is_compressed = False
        if ole.exists('FileHeader'):
            with ole.openstream('FileHeader') as s:
                header = s.read()
                if len(header) > 36:
                    is_compressed = bool(header[36] & 1)

        sections = [e for e in ole.listdir() if 'BodyText/Section' in '/'.join(e)]
        
        for entry in sections:
            with ole.openstream(entry) as s:
                data = s.read()
                
                if is_compressed:
                    try:
                        data = zlib.decompress(data, -15)
                    except Exception as e:
                        continue
                
                try:
                    text = data.decode('utf-16le', errors='ignore')
                except:
                    continue
                
                cleaned = ''
                for char in text:
                    code = ord(char)
                    if code == 0:
                        continue
                    elif 1 <= code <= 8 or 11 <= code <= 12 or 14 <= code <= 31:
                        cleaned += ' '
                    else:
                        cleaned += char
                
                final = ''
                for char in cleaned:
                    if (
                        '\uAC00' <= char <= '\uD7A3' or
                        char.isalnum() or
                        char in ' .,-()[]{}원%년월일\t\n\r'
                    ):
                        final += char
                    else:
                        final += ' '
                
                final = re.sub(r' +', ' ', final)
                final = re.sub(r'\n+', '\n', final)
                final = final.strip()
                
                if final and len(final) > 20:
                    extracted_text.append(final)
        
        ole.close()
        
        if extracted_text:
            return "\n".join(extracted_text)
        else:
            return "텍스트를 추출할 수 없습니다."
        
    except Exception as e:
        return f"HWP 파싱 오류: {str(e)}"


def extract_text_from_hwpx(file_path: str) -> str:
    """HWPX 파일에서 텍스트 추출"""
    try:
        extracted_text = []
        with zipfile.ZipFile(file_path, 'r') as zf:
            section_files = sorted([n for n in zf.namelist() if 'section' in n.lower() and n.endswith('.xml')])
            for name in section_files:
                with zf.open(name) as f:
                    content = f.read().decode('utf-8', errors='ignore')
                    matches = re.findall(r'<[^>]*:t[^>]*>(.*?)</[^>]*:t>', content, flags=re.DOTALL)
                    for m in matches:
                        txt = re.sub(r'<[^>]+>', '', m)
                        if txt.strip():
                            extracted_text.append(txt.strip())
        return "\n".join(extracted_text)
    except:
        return "HWPX 추출 실패"


def extract_text_from_pdf(file_path: str) -> str:
    """
    PDF 파일에서 텍스트 추출
    
    Args:
        file_path: PDF 파일 경로
        
    Returns:
        추출된 텍스트 (str)
    """
    try:
        from PyPDF2 import PdfReader
        
        reader = PdfReader(file_path)
        text_parts = []
        
        # 모든 페이지에서 텍스트 추출
        for page_num, page in enumerate(reader.pages, 1):
            try:
                text = page.extract_text()
                if text and text.strip():
                    text_parts.append(text.strip())
            except Exception as e:
                # 개별 페이지 실패해도 계속 진행
                continue
        
        if text_parts:
            return '\n'.join(text_parts)
        else:
            return "PDF에서 텍스트를 추출할 수 없습니다."
        
    except ImportError:
        return "PyPDF2 라이브러리 필요 (uv pip install pypdf2)"
    except Exception as e:
        return f"PDF 파싱 오류: {str(e)}"


def extract_text_from_txt(file_path: str) -> str:
    """텍스트 파일에서 읽기"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def parse_hwp_file(file_path: str) -> dict:
    """
    문서 파일 파싱 (통합 버전)
    
    지원 형식:
    - .hwp (한글 5.0 이상)
    - .hwpx (한글 2014 이상)
    - .pdf (PDF 문서)
    - .txt (텍스트)
    
    Args:
        file_path: 파일 경로
        
    Returns:
        {
            "filename": "test.hwp",
            "text": "추출된 텍스트...",
            "success": True,
            "error": None
        }
    """
    filename = Path(file_path).name
    
    try:
        # 파일 확장자에 따라 다른 함수 사용
        if filename.lower().endswith('.hwpx'):
            text = extract_text_from_hwpx(file_path)
        elif filename.lower().endswith('.pdf'):
            text = extract_text_from_pdf(file_path)  # PDF 추가!
        elif filename.lower().endswith('.txt'):
            text = extract_text_from_txt(file_path)
        else:  # .hwp
            text = extract_text_from_hwp(file_path)
        
        return {
            "filename": filename,
            "text": text,
            "success": True,
            "error": None
        }
        
    except Exception as e:
        return {
            "filename": filename,
            "text": "",
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    print("✅ parser.py 로드 완료 (HWP/HWPX/PDF 지원)")