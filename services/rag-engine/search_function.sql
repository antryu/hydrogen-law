-- Keyword-based search function for law documents
CREATE OR REPLACE FUNCTION search_law_documents(
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
  RETURN QUERY
  SELECT
    ld.id,
    ld.content,
    ld.metadata,
    ts_rank(
      to_tsvector('simple', ld.content),
      plainto_tsquery('simple', search_query)
    ) * 100 AS relevance_score
  FROM law_documents ld
  WHERE to_tsvector('simple', ld.content) @@ plainto_tsquery('simple', search_query)
  ORDER BY relevance_score DESC
  LIMIT max_results;
END;
$$ LANGUAGE plpgsql;
