-- Korean-optimized keyword search function using LIKE
-- Supports multi-keyword queries by splitting on spaces/commas and using OR logic
CREATE OR REPLACE FUNCTION search_law_documents(
  search_query TEXT,
  max_results INT DEFAULT 100
)
RETURNS TABLE (
  id TEXT,
  content TEXT,
  metadata JSONB,
  relevance_score FLOAT
) AS $$
DECLARE
  keywords TEXT[];
  keyword TEXT;
  sanitized_keyword TEXT;
BEGIN
  -- Validate input: reject empty or whitespace-only queries
  IF LENGTH(TRIM(search_query)) = 0 THEN
    RAISE EXCEPTION 'search_query cannot be empty';
  END IF;

  -- Split query into keywords by spaces and commas
  keywords := regexp_split_to_array(TRIM(search_query), '[\s,]+');

  -- Remove empty strings from array
  keywords := array_remove(keywords, '');

  IF array_length(keywords, 1) IS NULL THEN
    RAISE EXCEPTION 'search_query cannot be empty';
  END IF;

  -- Single keyword: simple LIKE search (original behavior)
  IF array_length(keywords, 1) = 1 THEN
    -- Sanitize LIKE wildcards in user input
    sanitized_keyword := REPLACE(REPLACE(keywords[1], '%', '\%'), '_', '\_');

    RETURN QUERY
    SELECT
      ld.id,
      ld.content,
      ld.metadata,
      (LENGTH(ld.content) - LENGTH(REPLACE(ld.content, keywords[1], '')))::FLOAT / LENGTH(keywords[1])::FLOAT AS relevance_score
    FROM law_documents ld
    WHERE ld.content LIKE '%' || sanitized_keyword || '%'
    ORDER BY relevance_score DESC
    LIMIT max_results;

  ELSE
    -- Multiple keywords: OR logic with combined scoring
    -- Documents matching more keywords rank higher
    RETURN QUERY
    WITH keyword_matches AS (
      SELECT
        ld.id,
        ld.content,
        ld.metadata,
        kw.keyword AS matched_keyword,
        (LENGTH(ld.content) - LENGTH(REPLACE(ld.content, kw.keyword, '')))::FLOAT / LENGTH(kw.keyword)::FLOAT AS kw_score
      FROM law_documents ld
      CROSS JOIN LATERAL (
        SELECT unnest(keywords) AS keyword
      ) kw
      WHERE ld.content LIKE '%' || REPLACE(REPLACE(kw.keyword, '%', '\%'), '_', '\_') || '%'
    ),
    aggregated AS (
      SELECT
        km.id,
        km.content,
        km.metadata,
        SUM(km.kw_score) * (1 + (COUNT(DISTINCT km.matched_keyword) - 1) * 0.5) AS relevance_score
      FROM keyword_matches km
      GROUP BY km.id, km.content, km.metadata
    )
    SELECT
      a.id,
      a.content,
      a.metadata,
      a.relevance_score
    FROM aggregated a
    ORDER BY relevance_score DESC
    LIMIT max_results;
  END IF;
END;
$$ LANGUAGE plpgsql;
