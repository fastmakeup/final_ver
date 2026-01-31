import ElectronicDoc from '@/features/docWriter/components/templates/ElectronicDoc';
import PlanningReport from '@/features/docWriter/components/templates/PlanningReport';

/**
 * AI 분석 결과(templateType)에 따른 템플릿 컴포넌트 매핑
 */
export const TEMPLATE_COMPONENTS = {
  // 1. 서울시교육청 용산도서관 등 전자결재 양식 
  'GOV_ELECTRONIC': ElectronicDoc,
  
  // 2. 대한민국역사박물관 등 보고서/계획서 양식 [cite: 1]
  'PLANNING_REPORT': PlanningReport,
  
  // 3. 타입을 알 수 없거나 기본값일 때
  'DEFAULT': ElectronicDoc
};