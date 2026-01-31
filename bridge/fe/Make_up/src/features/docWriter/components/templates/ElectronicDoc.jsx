import React from 'react';

/** 전자결재형 공문 템플릿 (서울특별시교육청 용산도서관 양식) */
export default function ElectronicDoc({ data, onChange, isEditable = true }) {
  // AI가 분석한 데이터가 없을 경우를 대비한 기본값 설정
  const s = data || {};
  
  // 메인 섹션을 배열로 관리 (1. 관련, 2. 본문 등)
  const mainSections = s.mainSections || [
    {
      label: '1. 관련:',
      content: "독서문화진흥과-112(2026.1.29.) '2026년 디지털·간행물실 주요업무 계획(안)'",
      type: 'simple' // simple: 단순 텍스트, detailed: 세부 항목 포함
    },
    {
      label: '2.',
      content: '이용자의 적극적인 도서관 서비스 활용을 지원하기 위하여 다음과 같이 도서관 이용자 교육을 실시하고자 합니다.',
      type: 'detailed',
      detailItems: [
        { label: '가. 운영기간:', content: '2026. 1.~12.' },
        { label: '나. 운영장소:', content: '4층 시청각실' },
        { label: '다. 운영대상:', content: '도서관 이용자' },
        { label: '라. 운영내용:', content: '도서관 서비스 이용 교육' },
      ]
    }
  ];
  
  // 메인 섹션 수정
  const updateMainSection = (index, field, value) => {
    const newSections = [...mainSections];
    newSections[index] = { ...newSections[index], [field]: value };
    onChange('mainSections', newSections);
  };
  
  // 메인 섹션 추가
  const addMainSection = () => {
    const newSections = [...mainSections, { 
      label: '', 
      content: '', 
      type: 'simple' 
    }];
    onChange('mainSections', newSections);
  };
  
  // 메인 섹션 삭제
  const removeMainSection = (index) => {
    if (mainSections.length > 1) {
      const newSections = mainSections.filter((_, i) => i !== index);
      onChange('mainSections', newSections);
    }
  };
  
  // 세부 항목 수정
  const updateDetailItem = (sectionIndex, itemIndex, field, value) => {
    const newSections = [...mainSections];
    const newDetailItems = [...(newSections[sectionIndex].detailItems || [])];
    newDetailItems[itemIndex] = { ...newDetailItems[itemIndex], [field]: value };
    newSections[sectionIndex] = { ...newSections[sectionIndex], detailItems: newDetailItems };
    onChange('mainSections', newSections);
  };
  
  // 세부 항목 추가
  const addDetailItem = (sectionIndex) => {
    const newSections = [...mainSections];
    const newDetailItems = [...(newSections[sectionIndex].detailItems || []), { label: '', content: '' }];
    newSections[sectionIndex] = { ...newSections[sectionIndex], detailItems: newDetailItems };
    onChange('mainSections', newSections);
  };
  
  // 세부 항목 삭제
  const removeDetailItem = (sectionIndex, itemIndex) => {
    const newSections = [...mainSections];
    const detailItems = newSections[sectionIndex].detailItems || [];
    if (detailItems.length > 1) {
      const newDetailItems = detailItems.filter((_, i) => i !== itemIndex);
      newSections[sectionIndex] = { ...newSections[sectionIndex], detailItems: newDetailItems };
      onChange('mainSections', newSections);
    }
  };
  
  // 섹션 타입 토글 (simple <-> detailed)
  const toggleSectionType = (index) => {
    const newSections = [...mainSections];
    const currentType = newSections[index].type;
    newSections[index] = {
      ...newSections[index],
      type: currentType === 'simple' ? 'detailed' : 'simple',
      detailItems: currentType === 'simple' ? [{ label: '', content: '' }] : undefined
    };
    onChange('mainSections', newSections);
  };

  return (
    <div className="relative">
      {/* 페이지 구분선 (297mm마다) */}
      {isEditable && (
        <>
          <div className="page-break-line absolute left-0 right-0 border-t-2 border-dashed border-blue-400 z-10" style={{ top: '297mm' }}>
            <span className="absolute right-4 -top-3 bg-blue-100 text-blue-600 text-xs px-2 py-1 rounded">페이지 2</span>
          </div>
          <div className="page-break-line absolute left-0 right-0 border-t-2 border-dashed border-blue-400 z-10" style={{ top: '594mm' }}>
            <span className="absolute right-4 -top-3 bg-blue-100 text-blue-600 text-xs px-2 py-1 rounded">페이지 3</span>
          </div>
          <div className="page-break-line absolute left-0 right-0 border-t-2 border-dashed border-blue-400 z-10" style={{ top: '891mm' }}>
            <span className="absolute right-4 -top-3 bg-blue-100 text-blue-600 text-xs px-2 py-1 rounded">페이지 4</span>
          </div>
        </>
      )}
      
      <div className={`relative w-[210mm] min-h-[297mm] bg-white text-black p-[20mm] mx-auto shadow-2xl border border-gray-200 font-serif leading-snug ${!isEditable ? 'select-none' : ''}`}
           style={!isEditable ? { pointerEvents: 'none', userSelect: 'text' } : {}}>
        
        {!isEditable && (
          <div className="absolute top-4 right-4 bg-yellow-100 text-yellow-800 px-3 py-1 rounded-lg text-xs font-bold border border-yellow-300 z-50">
            미리보기 모드
          </div>
        )}
      
      {/* 상단 헤더: 슬로건 및 기관명 */}
      <header className="flex flex-col items-center mb-8 border-b border-gray-300 pb-4">
        <div className="text-[14pt] font-bold text-blue-600 mb-1 w-full">
          <textarea 
            className="text-center outline-none focus:bg-blue-50 w-full resize-none overflow-hidden"
            rows={1}
            value={s.slogan || ""}
            onChange={(e) => {
              onChange('slogan', e.target.value);
              e.target.style.height = 'auto';
              e.target.style.height = e.target.scrollHeight + 'px';
            }}
            onFocus={(e) => {
              e.target.style.height = 'auto';
              e.target.style.height = e.target.scrollHeight + 'px';
            }}
            placeholder="슬로건을 입력하세요"
          />
        </div>
        <div className="text-[22pt] font-extrabold tracking-widest text-gray-900 w-full">
          <textarea 
            className="text-center outline-none focus:bg-blue-50 w-full resize-none overflow-hidden"
            rows={1}
            value={s.institution || ""}
            onChange={(e) => {
              onChange('institution', e.target.value);
              e.target.style.height = 'auto';
              e.target.style.height = e.target.scrollHeight + 'px';
            }}
            onFocus={(e) => {
              e.target.style.height = 'auto';
              e.target.style.height = e.target.scrollHeight + 'px';
            }}
            placeholder="기관명을 입력하세요"
          />
        </div>
      </header>
      {/* 결재선 영역 */}
      <div className="flex justify-end mb-8">
        <table className="border-collapse border border-black text-[9pt]">
          <tbody>
            <tr>
              <td rowSpan={2} className="border border-black p-1 w-6 bg-gray-50 text-center font-bold">결재</td>
              <td className="border border-black p-1 w-20 text-center bg-gray-50">
                <input 
                  className="w-full text-center outline-none focus:bg-blue-50 font-normal"
                  value={s.position1 || ""}
                  onChange={(e) => onChange('position1', e.target.value)}
                  placeholder="주무관"
                />
              </td>
              <td className="border border-black p-1 w-20 text-center bg-gray-50">
                <input 
                  className="w-full text-center outline-none focus:bg-blue-50 font-normal"
                  value={s.position2 || ""}
                  onChange={(e) => onChange('position2', e.target.value)}
                  placeholder="과장"
                />
              </td>
              <td className="border border-black p-1 w-20 text-center bg-gray-50">
                <input 
                  className="w-full text-center outline-none focus:bg-blue-50 font-normal"
                  value={s.position3 || ""}
                  onChange={(e) => onChange('position3', e.target.value)}
                  placeholder="관장"
                />
              </td>
            </tr>
            <tr className="h-16">
              <td className="border border-black p-1 text-center align-middle relative">
                <input 
                  className="w-full text-center text-gray-400 text-[8pt] outline-none focus:bg-blue-50"
                  value={s.approver1 || ""}
                  onChange={(e) => onChange('approver1', e.target.value)}
                  placeholder="최서영"
                />
              </td>
              <td className="border border-black p-1 text-center align-middle">
                <input 
                  className="w-full text-center text-gray-400 text-[8pt] outline-none focus:bg-blue-50"
                  value={s.approver2 || ""}
                  onChange={(e) => onChange('approver2', e.target.value)}
                  placeholder="최영서"
                />
              </td>
              <td className="border border-black p-1 text-center align-middle">
                <input 
                  className="w-full text-center text-gray-400 text-[8pt] outline-none focus:bg-blue-50"
                  value={s.approver3 || ""}
                  onChange={(e) => onChange('approver3', e.target.value)}
                  placeholder="김한국"
                />
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* 문서 기본 정보 */}
      <div className="space-y-1 mb-8 text-[11pt]">
        <div className="flex">
          <input 
            className="w-20 font-bold outline-none focus:bg-blue-50 bg-transparent"
            value={s.receiverLabel || ""}
            onChange={(e) => onChange('receiverLabel', e.target.value)}
            placeholder="수 신"
          />
          <input 
            className="flex-1 outline-none focus:bg-blue-50"
            value={s.receiver || ""}
            onChange={(e) => onChange('receiver', e.target.value)}
            placeholder="내부결재"
          />
        </div>
        <div className="flex">
          <input 
            className="w-20 font-bold outline-none focus:bg-blue-50 bg-transparent"
            value={s.viaLabel || ""}
            onChange={(e) => onChange('viaLabel', e.target.value)}
            placeholder="(경유)"
          />
          <input 
            className="flex-1 outline-none focus:bg-blue-50"
            value={s.via || ""}
            onChange={(e) => onChange('via', e.target.value)}
            placeholder="경유처"
          />
        </div>
        <div className="flex items-start">
          <input 
            className="w-20 font-bold outline-none focus:bg-blue-50 bg-transparent shrink-0 pt-1"
            value={s.titleLabel || ""}
            onChange={(e) => onChange('titleLabel', e.target.value)}
            placeholder="제 목"
          />
          <textarea 
            className="flex-1 font-bold outline-none focus:bg-blue-50 resize-none overflow-hidden"
            rows={1}
            value={s.title || ""}
            onChange={(e) => onChange('title', e.target.value)}
            placeholder="2026년 도서관 이용자 교육 운영 계획"
          />
        </div>
      </div>

      {/* 본문 내용 */}
      <main className="text-[12pt] min-h-[500px]">
        {isEditable && (
          <div className="flex justify-end mb-3">
            <button
              onClick={addMainSection}
              className="text-xs px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600 transition-colors shadow-sm"
            >
              + 섹션 추가
            </button>
          </div>
        )}
        
        <div className="flex flex-col gap-6">
          {mainSections.map((section, sectionIndex) => (
            <div key={sectionIndex} className="group relative">
              <div className="flex gap-2 items-start">
                <input 
                  className="shrink-0 outline-none focus:bg-blue-50 bg-transparent w-24 font-semibold"
                  value={section.label}
                  onChange={(e) => updateMainSection(sectionIndex, 'label', e.target.value)}
                  placeholder="예) 3."
                />
                <textarea 
                  className="flex-1 outline-none focus:bg-blue-50 resize-none"
                  rows={2}
                  value={section.content}
                  onChange={(e) => updateMainSection(sectionIndex, 'content', e.target.value)}
                  placeholder="내용을 입력하세요"
                />
                {isEditable && (
                  <div className="flex gap-1 shrink-0">
                    <button
                      onClick={() => toggleSectionType(sectionIndex)}
                      className="opacity-0 group-hover:opacity-100 text-xs px-2 py-1 bg-purple-500 text-white rounded hover:bg-purple-600 transition-all"
                      title={section.type === 'simple' ? '세부항목 추가' : '단순텍스트'}
                    >
                      {section.type === 'simple' ? '📋' : '📝'}
                    </button>
                    {mainSections.length > 1 && (
                      <button
                        onClick={() => removeMainSection(sectionIndex)}
                        className="opacity-0 group-hover:opacity-100 text-red-600 hover:text-red-800 text-xs px-2 py-1 transition-opacity"
                        title="삭제"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                )}
              </div>
              
              {/* 세부 항목 (가, 나, 다 등) */}
              {section.type === 'detailed' && section.detailItems && (
                <div className="pl-4 mt-3">
                  {isEditable && (
                    <div className="flex items-center justify-end mb-2">
                      <button
                        onClick={() => addDetailItem(sectionIndex)}
                        className="text-xs px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors shadow-sm"
                      >
                        + 항목 추가
                      </button>
                    </div>
                  )}
                  <div className="pl-6 space-y-2">
                    {section.detailItems.map((item, itemIndex) => (
                      <div key={itemIndex} className="flex gap-2 items-start group/item">
                        <input 
                          className="shrink-0 outline-none focus:bg-blue-50 bg-transparent w-32"
                          value={item.label}
                          onChange={(e) => updateDetailItem(sectionIndex, itemIndex, 'label', e.target.value)}
                          placeholder="예) 마. 항목명:"
                        />
                        <input 
                          className="flex-1 outline-none focus:bg-blue-50"
                          value={item.content}
                          onChange={(e) => updateDetailItem(sectionIndex, itemIndex, 'content', e.target.value)}
                          placeholder="내용을 입력하세요"
                        />
                        {isEditable && section.detailItems.length > 1 && (
                          <button
                            onClick={() => removeDetailItem(sectionIndex, itemIndex)}
                            className="opacity-0 group-hover/item:opacity-100 text-red-600 hover:text-red-800 text-xs px-2 py-1 transition-opacity shrink-0"
                            title="삭제"
                          >
                            ✕
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
        
        {/* 추가 자유 작성 영역 */}
        <div className="mt-6 pt-6 border-t border-dashed border-gray-300">
          <textarea 
            className="w-full outline-none focus:bg-blue-50/30 resize-none min-h-[100px] text-[12pt]"
            value={s.additionalContent || ""}
            onChange={(e) => onChange('additionalContent', e.target.value)}
            placeholder="추가 내용을 자유롭게 작성하세요..."
            rows={5}
          />
        </div>
      </main>

      {/* 하단 푸터: 발신 정보 */}
      <footer className="mt-10 pt-6 border-t border-gray-300 text-[9pt] text-gray-600">
        <div className="grid grid-cols-2 gap-y-1">
          <div className="flex gap-2">
            <input 
              className="shrink-0 outline-none focus:bg-blue-50 bg-transparent text-[9pt]"
              value={s.enforcementLabel || ""}
              onChange={(e) => onChange('enforcementLabel', e.target.value)}
              placeholder="시행:"
            />
            <input 
              className="flex-1 outline-none focus:bg-blue-50 text-[9pt]"
              value={s.enforcement || ""}
              onChange={(e) => onChange('enforcement', e.target.value)}
              placeholder="독서문화진흥과-126"
            />
          </div>
          <div className="flex gap-2 justify-end">
            <input 
              className="shrink-0 outline-none focus:bg-blue-50 bg-transparent text-[9pt]"
              value={s.receiptLabel || ""}
              onChange={(e) => onChange('receiptLabel', e.target.value)}
              placeholder="접수:"
            />
            <input 
              className="w-32 outline-none focus:bg-blue-50 text-[9pt] text-right"
              value={s.receiptDate || ""}
              onChange={(e) => onChange('receiptDate', e.target.value)}
              placeholder="( 2026. 1. 30. )"
            />
          </div>
          <div className="flex gap-2">
            <input 
              className="shrink-0 outline-none focus:bg-blue-50 bg-transparent text-[9pt]"
              value={s.postalLabel || ""}
              onChange={(e) => onChange('postalLabel', e.target.value)}
              placeholder="우:"
            />
            <input 
              className="flex-1 outline-none focus:bg-blue-50 text-[9pt]"
              value={s.address || ""}
              onChange={(e) => onChange('address', e.target.value)}
              placeholder="04328 서울특별시 용산구 두텁바위로 160 (후암동)"
            />
          </div>
          <div className="flex gap-2 justify-end">
            <input 
              className="shrink-0 outline-none focus:bg-blue-50 bg-transparent text-[9pt]"
              value={s.phoneLabel || ""}
              onChange={(e) => onChange('phoneLabel', e.target.value)}
              placeholder="전화:"
            />
            <input 
              className="w-32 outline-none focus:bg-blue-50 text-[9pt] text-right"
              value={s.phone || ""}
              onChange={(e) => onChange('phone', e.target.value)}
              placeholder="02-6902-7761"
            />
          </div>
          <div className="flex gap-2">
            <input 
              className="shrink-0 outline-none focus:bg-blue-50 bg-transparent text-[9pt]"
              value={s.emailLabel || ""}
              onChange={(e) => onChange('emailLabel', e.target.value)}
              placeholder="이메일:"
            />
            <input 
              className="flex-1 outline-none focus:bg-blue-50 text-[9pt]"
              value={s.email || ""}
              onChange={(e) => onChange('email', e.target.value)}
              placeholder="west00@sen.go.kr"
            />
          </div>
          <div className="flex gap-2 justify-end">
            <input 
              className="shrink-0 outline-none focus:bg-blue-50 bg-transparent text-[9pt]"
              value={s.homepageLabel || ""}
              onChange={(e) => onChange('homepageLabel', e.target.value)}
              placeholder="홈페이지:"
            />
            <input 
              className="w-48 outline-none focus:bg-blue-50 text-[9pt] text-right"
              value={s.homepage || ""}
              onChange={(e) => onChange('homepage', e.target.value)}
              placeholder="http://yslib.sen.go.kr"
            />
          </div>
        </div>
      </footer>
    </div>
    </div>
  );
}