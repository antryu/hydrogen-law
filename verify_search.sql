-- Create a simpler search function that uses LIKE for Korean text
CREATE OR REPLACE FUNCTION search_law_documents_like(
  search_query TEXT,
  max_results INT DEFAULT 10
)
RETURNS TABLE (
  id TEXT,
  content TEXT,
  metadata JSONB,
  relevance_score FLOAT
) AS $$
BEGIN
  -- Validate input: reject empty or whitespace-only queries
  IF LENGTH(TRIM(search_query)) = 0 THEN
    RAISE EXCEPTION 'search_query cannot be empty';
  END IF;

  -- Sanitize LIKE wildcards in user input
  search_query := REPLACE(REPLACE(search_query, '%', '\%'), '_', '\_');

  RETURN QUERY
  SELECT
    ld.id,
    ld.content,
    ld.metadata,
    -- Simple scoring based on occurrence count (safe from division by zero)
    (LENGTH(ld.content) - LENGTH(REPLACE(ld.content, search_query, ''))) / LENGTH(search_query)::FLOAT * 10 AS relevance_score
  FROM law_documents ld
  WHERE ld.content LIKE '%' || search_query || '%'
  ORDER BY relevance_score DESC
  LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Test the new function
SELECT COUNT(*) FROM law_documents WHERE content LIKE '%충전%';
