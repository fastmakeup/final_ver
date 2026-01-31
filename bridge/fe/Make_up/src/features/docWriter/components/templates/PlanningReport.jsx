import React, { useMemo } from 'react';

/** 보고서/계획서형 공문 템플릿 (대한민국역사박물관 양식) */
export default function PlanningReport({ data, onChange, isEditable = true }) {
  const s = data || {};
  
  // 목적 항목을 배열로 관리
  const purposeItems = s.purposeItems || [
    { bullet: 'ㅇ', content: '(예산조정) 축제 규모 확대에 따른 추가 예산 확보' },
    { bullet: 'ㅇ', content: '(사업개선) 관광객 편의 시설 보강 및 안전 관리 강화' },
  ];
  
  // 예산 항목을 배열로 관리
  const budgetItems = s.budgetItems || [
    { category: '인건비', detail: '책임연구원 외 2명 (8개월)', amount: '6,294,179' },
    { category: '자료수집비', detail: '조사원 수당, 사례비, 코딩비 등', amount: '10,835,000' },
  ];
  
  // 개요 항목을 행렬 구조로 관리
  const overviewTable = s.overviewTable || {
    rows: [
      { cells: ['사 업 명', '2026년 대한민국역사박물관 관람객 만족도 조사'] },
      { cells: ['사업기간', '계약체결일 ~ 2026.12.11.'] },
      { cells: ['필요예산', '20,000천원(부가세 포함)'] },
    ]
  };
  
  // 추진일정 항목을 배열로 관리
  const scheduleItems = s.scheduleItems || [
    { period: '2월 ~ 3월', content: '계획 수립 및 계약 체결' },
    { period: '4월 ~ 10월', content: '조사 시행 (분기별 1회)' },
    { period: '11월 ~ 12월', content: '최종 결과보고 및 정산' },
  ];
  
  // 합계 자동 계산
  const budgetTotal = useMemo(() => {
    return budgetItems.reduce((sum, item) => {
      const amount = parseInt(item.amount?.replace(/,/g, '') || '0');
      return sum + amount;
    }, 0).toLocaleString();
  }, [budgetItems]);
  
  // 예산 항목 수정
  const updateBudgetItem = (index, field, value) => {
    const newItems = [...budgetItems];
    
    // 금액 필드인 경우 숫자만 추출하고 콤마 포맷 적용
    if (field === 'amount') {
      const numericValue = value.replace(/[^\d]/g, '');
      const formattedValue = numericValue ? parseInt(numericValue).toLocaleString() : '';
      newItems[index] = { ...newItems[index], [field]: formattedValue };
    } else {
      newItems[index] = { ...newItems[index], [field]: value };
    }
    
    onChange('budgetItems', newItems);
  };
  
  // 목적 항목 수정
  const updatePurposeItem = (index, field, value) => {
    const newItems = [...purposeItems];
    newItems[index] = { ...newItems[index], [field]: value };
    onChange('purposeItems', newItems);
  };
  
  // 목적 항목 추가
  const addPurposeItem = () => {
    const newItems = [...purposeItems, { bullet: 'ㅇ', content: '' }];
    onChange('purposeItems', newItems);
  };
  
  // 목적 항목 삭제
  const removePurposeItem = (index) => {
    if (purposeItems.length > 1) {
      const newItems = purposeItems.filter((_, i) => i !== index);
      onChange('purposeItems', newItems);
    }
  };
  
  // 예산 항목 추가
  const addBudgetItem = () => {
    const newItems = [...budgetItems, { category: '', detail: '', amount: '0' }];
    onChange('budgetItems', newItems);
  };
  
  // 예산 항목 삭제
  const removeBudgetItem = (index) => {
    if (budgetItems.length > 1) {
      const newItems = budgetItems.filter((_, i) => i !== index);
      onChange('budgetItems', newItems);
    }
  };
  
  // 개요 항목 수정
  const updateOverviewCell = (rowIndex, cellIndex, value) => {
    const newTable = { ...overviewTable };
    newTable.rows[rowIndex].cells[cellIndex] = value;
    onChange('overviewTable', newTable);
  };
  
  // 개요 행 추가
  const addOverviewRow = (index) => {
    const newTable = { ...overviewTable };
    const columnCount = newTable.rows[0]?.cells.length || 2;
    const newRow = { cells: Array(columnCount).fill('') };
    newTable.rows.splice(index + 1, 0, newRow);
    onChange('overviewTable', newTable);
  };
  
  // 개요 행 삭제
  const removeOverviewRow = (index) => {
    if (overviewTable.rows.length > 1) {
      const newTable = { ...overviewTable };
      newTable.rows.splice(index, 1);
      onChange('overviewTable', newTable);
    }
  };
  
  // 개요 열 추가
  const addOverviewColumn = (cellIndex) => {
    const newTable = { ...overviewTable };
    newTable.rows.forEach(row => {
      row.cells.splice(cellIndex + 1, 0, '');
    });
    onChange('overviewTable', newTable);
  };
  
  // 개요 열 삭제
  const removeOverviewColumn = (cellIndex) => {
    const columnCount = overviewTable.rows[0]?.cells.length || 0;
    if (columnCount > 2) {
      const newTable = { ...overviewTable };
      newTable.rows.forEach(row => {
        row.cells.splice(cellIndex, 1);
      });
      onChange('overviewTable', newTable);
    }
  };
  
  // 추진일정 항목 수정
  const updateScheduleItem = (index, field, value) => {
    const newItems = [...scheduleItems];
    newItems[index] = { ...newItems[index], [field]: value };
    onChange('scheduleItems', newItems);
  };
  
  // 추진일정 항목 추가
  const addScheduleItem = () => {
    const newItems = [...scheduleItems, { period: '', content: '' }];
    onChange('scheduleItems', newItems);
  };
  
  // 추진일정 항목 삭제
  const removeScheduleItem = (index) => {
    if (scheduleItems.length > 1) {
      const newItems = scheduleItems.filter((_, i) => i !== index);
      onChange('scheduleItems', newItems);
    }
  };
  
  // 추가 섹션을 배열로 관리
  const additionalSections = s.additionalSections || [];
  
  // 추가 섹션 추가
  const addAdditionalSection = () => {
    const newSections = [...additionalSections, { title: '', content: '' }];
    onChange('additionalSections', newSections);
  };
  
  // 추가 섹션 수정
  const updateAdditionalSection = (index, field, value) => {
    const newSections = [...additionalSections];
    newSections[index] = { ...newSections[index], [field]: value };
    onChange('additionalSections', newSections);
  };
  
  // 추가 섹션 삭제
  const removeAdditionalSection = (index) => {
    const newSections = additionalSections.filter((_, i) => i !== index);
    onChange('additionalSections', newSections);
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
      
      <div className={`relative w-[210mm] min-h-[297mm] bg-white text-black p-[20mm] pb-[30mm] mx-auto shadow-2xl border border-gray-200 font-serif leading-relaxed ${!isEditable ? 'select-none' : ''}`}
           style={!isEditable ? { pointerEvents: 'none', userSelect: 'text' } : {}}>
        
        {!isEditable && (
          <div className="absolute top-4 right-4 bg-yellow-100 text-yellow-800 px-3 py-1 rounded-lg text-xs font-bold border border-yellow-300 z-50">
            미리보기 모드
          </div>
        )}
      
      {/* 문서 제목 섹션 */}
      <div className="text-center mb-10">
        <h1 className="text-[28pt] font-bold border-b-2 border-black pb-2 tracking-tighter">
          <input
            className="w-full text-center outline-none focus:bg-blue-50"
            value={s.docTitle || ""}
            onChange={(e) => onChange('docTitle', e.target.value)}
            readOnly={!isEditable}
            placeholder="2026년 박물관 관람객 만족도 조사 계획"
          />
        </h1>
        <div className="text-right mt-2 text-[12pt] text-gray-600 flex gap-2 justify-end">
          <input 
            className="w-40 text-right outline-none focus:bg-blue-50"
            value={s.date || ""}
            onChange={(e) => onChange('date', e.target.value)}
            placeholder="2026. 1. 30.(금)"
          />
          <span>/</span>
          <input 
            className="w-32 outline-none focus:bg-blue-50"
            value={s.department || ""}
            onChange={(e) => onChange('department', e.target.value)}
            placeholder="교류홍보과"
          />
        </div>
      </div>

      {/* 1. 목적 섹션 */}
      <section className="mb-8">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-[15pt] font-bold flex items-center gap-2">
            <span>□</span>
            <input 
              className="outline-none focus:bg-blue-50 bg-transparent font-bold"
              value={s.purposeTitle || ""}
              onChange={(e) => onChange('purposeTitle', e.target.value)}
              placeholder="목 적"
            />
          </h3>
          <button
            onClick={addPurposeItem}
            className="text-xs px-3 py-1 bg-primary-500 text-white rounded hover:bg-primary-600 transition-colors"
          >
            + 항목 추가
          </button>
        </div>
        <div className="pl-4 space-y-2 text-[12pt]">
          {purposeItems.map((item, index) => (
            <div key={index} className="flex gap-2 items-start group">
              <input 
                className="w-6 text-center outline-none focus:bg-blue-50 bg-transparent shrink-0"
                value={item.bullet}
                onChange={(e) => updatePurposeItem(index, 'bullet', e.target.value)}
                placeholder="ㅇ"
              />
              <textarea 
                className="flex-1 bg-transparent outline-none focus:bg-blue-50/30 resize-none"
                value={item.content}
                onChange={(e) => updatePurposeItem(index, 'content', e.target.value)}
                rows={2}
                placeholder="내용을 입력하세요"
              />
              {purposeItems.length > 1 && (
                <button
                  onClick={() => removePurposeItem(index)}
                  className="opacity-0 group-hover:opacity-100 text-red-600 hover:text-red-800 text-xs px-2 py-1 transition-opacity"
                  title="삭제"
                >
                  ✕
                </button>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* 2. 개요 섹션 (복합 표 구조) */}
      <section className="mb-8">
        <h3 className="text-[15pt] font-bold mb-3 flex items-center gap-2">
          <span>□</span>
          <input 
            className="outline-none focus:bg-blue-50 bg-transparent font-bold"
            value={s.overviewTitle || ""}
            onChange={(e) => onChange('overviewTitle', e.target.value)}
            placeholder="개 요"
          />
        </h3>
        <table className="w-full border-collapse border border-black text-[11pt]">
          <tbody>
            {overviewTable.rows.map((row, rowIndex) => (
              <tr key={rowIndex}>
                {row.cells.map((cell, cellIndex) => (
                  <td 
                    key={cellIndex}
                    className={`border border-black p-3 relative group ${cellIndex === 0 ? 'bg-gray-50 w-[150px] font-bold text-center' : ''}`}
                  >
                    <input 
                      className={`w-full outline-none ${cellIndex === 0 ? 'bg-gray-50 font-bold text-center' : 'bg-transparent'}`}
                      value={cell}
                      onChange={(e) => updateOverviewCell(rowIndex, cellIndex, e.target.value)}
                      placeholder={cellIndex === 0 ? "항목명" : "내용"}
                    />
                    {/* 행/열 조작 버튼 */}
                    <div className="absolute right-1 top-1 opacity-0 group-hover:opacity-100 flex gap-1 transition-opacity z-10">
                      {/* 행 추가 */}
                      <button
                        onClick={() => addOverviewRow(rowIndex)}
                        className="w-5 h-5 bg-blue-500 text-white rounded text-[10px] hover:bg-blue-600 flex items-center justify-center"
                        title="아래에 행 추가"
                      >
                        ↓
                      </button>
                      {/* 행 삭제 */}
                      {overviewTable.rows.length > 1 && (
                        <button
                          onClick={() => removeOverviewRow(rowIndex)}
                          className="w-5 h-5 bg-red-500 text-white rounded text-[10px] hover:bg-red-600 flex items-center justify-center"
                          title="행 삭제"
                        >
                          ×
                        </button>
                      )}
                      {/* 열 추가 */}
                      <button
                        onClick={() => addOverviewColumn(cellIndex)}
                        className="w-5 h-5 bg-green-500 text-white rounded text-[10px] hover:bg-green-600 flex items-center justify-center"
                        title="오른쪽에 열 추가"
                      >
                        →
                      </button>
                      {/* 열 삭제 */}
                      {row.cells.length > 2 && (
                        <button
                          onClick={() => removeOverviewColumn(cellIndex)}
                          className="w-5 h-5 bg-orange-500 text-white rounded text-[10px] hover:bg-orange-600 flex items-center justify-center"
                          title="열 삭제"
                        >
                          ‖
                        </button>
                      )}
                    </div>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {/* 3. 예산 산출 내역 (상세 표) */}
      <section className="mb-8">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-[15pt] font-bold flex items-center gap-2">
            <span>□</span>
            <input 
              className="outline-none focus:bg-blue-50 bg-transparent font-bold"
              value={s.budgetTitle || ""}
              onChange={(e) => onChange('budgetTitle', e.target.value)}
              placeholder="필요예산 산출내역"
            />
          </h3>
          <button
            onClick={addBudgetItem}
            className="text-xs px-3 py-1 bg-primary-500 text-white rounded hover:bg-primary-600 transition-colors"
          >
            + 항목 추가
          </button>
        </div>
        <table className="w-full border-collapse border border-black text-[10pt] text-center">
          <thead className="bg-gray-50 font-bold">
            <tr>
              <th className="border border-black p-2">구 분</th>
              <th className="border border-black p-2">산출 내역</th>
              <th className="border border-black p-2">금 액 (원)</th>
              <th className="border border-black p-2 w-16">작업</th>
            </tr>
          </thead>
          <tbody>
            {budgetItems.map((item, index) => (
              <tr key={index}>
                <td className="border border-black p-2 font-bold">
                  <input 
                    className="w-full text-center outline-none bg-transparent font-bold"
                    value={item.category}
                    onChange={(e) => updateBudgetItem(index, 'category', e.target.value)}
                    placeholder="구분"
                  />
                </td>
                <td className="border border-black p-2 text-left text-[9pt]">
                  <input 
                    className="w-full text-left outline-none bg-transparent text-[9pt]"
                    value={item.detail}
                    onChange={(e) => updateBudgetItem(index, 'detail', e.target.value)}
                    placeholder="산출 내역"
                  />
                </td>
                <td className="border border-black p-2 text-right">
                  <input 
                    className="w-full text-right outline-none bg-transparent"
                    value={item.amount}
                    onChange={(e) => updateBudgetItem(index, 'amount', e.target.value)}
                    placeholder="0"
                  />
                </td>
                <td className="border border-black p-2">
                  {budgetItems.length > 1 && (
                    <button
                      onClick={() => removeBudgetItem(index)}
                      className="text-red-600 hover:text-red-800 text-xs"
                      title="삭제"
                    >
                      ✕
                    </button>
                  )}
                </td>
              </tr>
            ))}
            <tr className="bg-blue-50/30 font-bold">
              <td colSpan={2} className="border border-black p-2">합 계</td>
              <td className="border border-black p-2 text-right text-blue-700">
                {budgetTotal}
              </td>
              <td className="border border-black p-2"></td>
            </tr>
          </tbody>
        </table>
      </section>

      {/* 4. 추진일정 */}
      <section className="mb-12">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-[15pt] font-bold flex items-center gap-2">
            <span>□</span>
            <input 
              className="outline-none focus:bg-blue-50 bg-transparent font-bold"
              value={s.scheduleTitle || ""}
              onChange={(e) => onChange('scheduleTitle', e.target.value)}
              placeholder="추진일정"
            />
          </h3>
          <button
            onClick={addScheduleItem}
            className="text-xs px-3 py-1 bg-primary-500 text-white rounded hover:bg-primary-600 transition-colors"
          >
            + 일정 추가
          </button>
        </div>
        <div className="flex flex-col gap-3 pl-4">
          {scheduleItems.map((item, index) => (
            <div key={index} className="flex items-center gap-4 group">
              <input 
                className="w-32 font-bold text-gray-500 outline-none focus:bg-blue-50"
                value={item.period}
                onChange={(e) => updateScheduleItem(index, 'period', e.target.value)}
                placeholder="기간"
              />
              <div className="border-l-2 border-black pl-4 flex-1">
                <input 
                  className="w-full outline-none focus:bg-blue-50"
                  value={item.content}
                  onChange={(e) => updateScheduleItem(index, 'content', e.target.value)}
                  placeholder="내용"
                />
              </div>
              {scheduleItems.length > 1 && (
                <button
                  onClick={() => removeScheduleItem(index)}
                  className="opacity-0 group-hover:opacity-100 text-red-600 hover:text-red-800 text-xs px-2 py-1 transition-opacity"
                  title="삭제"
                >
                  ✕
                </button>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* 추가 자유 작성 영역 */}
      {isEditable && (
        <div className="flex justify-end mb-3">
          <button
            onClick={addAdditionalSection}
            className="text-xs px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600 transition-colors shadow-sm"
          >
            + 섹션 추가
          </button>
        </div>
      )}
      
      {additionalSections.map((section, index) => (
        <section key={index} className="mb-12 mt-8 group relative">
          <div className="flex items-center gap-2 mb-3">
            <h3 className="text-[15pt] font-bold flex items-center gap-2 flex-1">
              <span>□</span>
              <input 
                className="outline-none focus:bg-blue-50 bg-transparent font-bold flex-1"
                value={section.title}
                onChange={(e) => updateAdditionalSection(index, 'title', e.target.value)}
                placeholder="섹션 제목을 입력하세요"
              />
            </h3>
            {isEditable && (
              <button
                onClick={() => removeAdditionalSection(index)}
                className="opacity-0 group-hover:opacity-100 text-red-600 hover:text-red-800 text-xs px-2 py-1 transition-opacity"
                title="삭제"
              >
                ✕
              </button>
            )}
          </div>
          <div className="pl-4">
            <textarea 
              className="w-full bg-transparent outline-none focus:bg-blue-50/30 resize-none text-[12pt] min-h-[100px]"
              value={section.content}
              onChange={(e) => updateAdditionalSection(index, 'content', e.target.value)}
              placeholder="내용을 입력하세요..."
              rows={5}
            />
          </div>
        </section>
      ))}
      </div>
    </div>
  );
}