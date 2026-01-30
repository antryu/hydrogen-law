-- Check how many documents contain "충전"
SELECT 
  COUNT(*) as total_docs_with_충전,
  COUNT(CASE WHEN content LIKE '%충전소%' THEN 1 END) as docs_with_충전소,
  COUNT(CASE WHEN content LIKE '%충전%' THEN 1 END) as docs_with_충전
FROM law_documents;
