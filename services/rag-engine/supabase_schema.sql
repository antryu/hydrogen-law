-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create law_documents table with vector embeddings
CREATE TABLE IF NOT EXISTS law_documents (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(768),  -- ko-sroberta-multitask embedding dimension
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index for vector similarity search
CREATE INDEX IF NOT EXISTS law_documents_embedding_idx
ON law_documents USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create index for metadata queries
CREATE INDEX IF NOT EXISTS law_documents_metadata_idx
ON law_documents USING gin(metadata);

-- Create index for full-text search on content (using simple tokenizer)
CREATE INDEX IF NOT EXISTS law_documents_content_idx
ON law_documents USING gin(to_tsvector('simple', content));
