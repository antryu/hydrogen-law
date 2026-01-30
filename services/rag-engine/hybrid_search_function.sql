-- Hybrid search function combining semantic (vector) and keyword search
-- Uses Reciprocal Rank Fusion (RRF) to combine results
CREATE OR REPLACE FUNCTION hybrid_search_law_documents(
  search_query TEXT,
  query_embedding vector(768),
  max_results INT DEFAULT 10,
  keyword_weight FLOAT DEFAULT 0.3,
  semantic_weight FLOAT DEFAULT 0.7
)
RETURNS TABLE (
  id TEXT,
  content TEXT,
  metadata JSONB,
  relevance_score FLOAT,
  semantic_score FLOAT,
  keyword_score FLOAT
) AS $$
DECLARE
  k_constant INT := 60; -- RRF k constant
BEGIN
  RETURN QUERY
  WITH semantic_results AS (
    SELECT
      ld.id,
      ld.content,
      ld.metadata,
      1 - (ld.embedding <=> query_embedding) AS similarity,
      ROW_NUMBER() OVER (ORDER BY ld.embedding <=> query_embedding) AS rank
    FROM law_documents ld
    ORDER BY ld.embedding <=> query_embedding
    LIMIT max_results * 2
  ),
  keyword_results AS (
    SELECT
      ld.id,
      ld.content,
      ld.metadata,
      ts_rank(
        to_tsvector('simple', ld.content),
        plainto_tsquery('simple', search_query)
      ) AS score,
      ROW_NUMBER() OVER (
        ORDER BY ts_rank(
          to_tsvector('simple', ld.content),
          plainto_tsquery('simple', search_query)
        ) DESC
      ) AS rank
    FROM law_documents ld
    WHERE to_tsvector('simple', ld.content) @@ plainto_tsquery('simple', search_query)
    ORDER BY score DESC
    LIMIT max_results * 2
  ),
  combined_results AS (
    SELECT
      COALESCE(s.id, k.id) AS id,
      COALESCE(s.content, k.content) AS content,
      COALESCE(s.metadata, k.metadata) AS metadata,
      COALESCE(s.similarity, 0) AS semantic_score,
      COALESCE(k.score, 0) AS keyword_score,
      -- Reciprocal Rank Fusion score
      (
        semantic_weight * (1.0 / (k_constant + COALESCE(s.rank, 999999))) +
        keyword_weight * (1.0 / (k_constant + COALESCE(k.rank, 999999)))
      ) * 100 AS rrf_score
    FROM semantic_results s
    FULL OUTER JOIN keyword_results k ON s.id = k.id
  )
  SELECT
    cr.id,
    cr.content,
    cr.metadata,
    cr.rrf_score AS relevance_score,
    cr.semantic_score,
    cr.keyword_score
  FROM combined_results cr
  ORDER BY cr.rrf_score DESC
  LIMIT max_results;
END;
$$ LANGUAGE plpgsql;
