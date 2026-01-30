-- Test how the 'simple' tokenizer handles Korean text
SELECT to_tsvector('simple', '수소충전소 설치 기준') as tokens;
SELECT to_tsquery('simple', '충전') as query;
SELECT plainto_tsquery('simple', '충전') as plain_query;

-- Test if the search would match
SELECT 
  to_tsvector('simple', '수소충전소 설치 기준') @@ plainto_tsquery('simple', '충전') as matches;
