import { createClient } from '@supabase/supabase-js';
import { NextResponse } from 'next/server';

const MAX_QUERY_LENGTH = 500;
const MAX_RESULTS = 100;
const MAX_KEYWORDS = 20;

interface SupabaseSearchResult {
  id: string;
  content: string;
  relevance_score: number;
  metadata: {
    law_name?: string;
    article_number?: string;
    title?: string;
    article_type?: 'article' | 'appendix';
  };
}

function escapeRegex(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

export async function POST(request: Request) {
  try {
    const { query, top_k = 10 } = await request.json();

    if (!query || typeof query !== 'string' || !query.trim()) {
      return NextResponse.json(
        { error: '검색어를 입력해주세요' },
        { status: 400 }
      );
    }

    const sanitizedQuery = query.trim().slice(0, MAX_QUERY_LENGTH);
    const validatedTopK = Math.min(Math.max(1, Number(top_k) || 10), MAX_RESULTS);

    // Initialize Supabase client
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

    if (!supabaseUrl || !supabaseKey) {
      console.error('Missing Supabase environment variables');
      return NextResponse.json(
        { error: 'Server configuration error' },
        { status: 500 }
      );
    }

    const supabase = createClient(supabaseUrl, supabaseKey);

    // Call Supabase RPC function for keyword search
    const { data, error } = await supabase.rpc('search_law_documents', {
      search_query: sanitizedQuery,
      max_results: validatedTopK
    });

    if (error) {
      console.error('Supabase error:', error);
      return NextResponse.json(
        { error: 'Search failed' },
        { status: 500 }
      );
    }

    // Normalize relevance scores to 0-100 range
    const maxScore = Math.max(...data.map((row: SupabaseSearchResult) => row.relevance_score), 0.0001);

    // Parse and limit keywords (support both comma and space separation)
    const keywords = sanitizedQuery
      .split(/[\s,]+/)
      .filter((k: string) => k.length > 0)
      .slice(0, MAX_KEYWORDS);

    // Build single regex for all keywords (escaped to prevent ReDoS)
    const keywordRegex = keywords.length > 0
      ? new RegExp(`(${keywords.map(escapeRegex).join('|')})`, 'gi')
      : null;

    // Transform results to match frontend expectations
    const articles = data.map((row: SupabaseSearchResult) => {
      let highlightedContent = row.content;

      // Highlight search keywords in content (single pass with escaped regex)
      if (keywordRegex) {
        highlightedContent = highlightedContent.replace(
          keywordRegex,
          '<mark style="background-color: #fef08a; padding: 2px 4px; border-radius: 2px;">$1</mark>'
        );
      }

      // Smart newline handling (same for all content types)
      // 1. Double newlines -> paragraph break
      highlightedContent = highlightedContent.replace(/\n\n+/g, '<br><br>');
      // 2. Single newlines -> space (allow text to flow naturally)
      highlightedContent = highlightedContent.replace(/\n/g, ' ');

      // Normalize score: highest result = 100%, others scaled proportionally
      const normalizedScore = (row.relevance_score / maxScore) * 100;

      return {
        article_id: row.id,
        law_name: row.metadata.law_name || '수소경제육성및수소안전관리에관한법률',
        article_number: row.metadata.article_number || row.id.split('_')[1],
        title: row.metadata.title || '',
        content: row.content,
        highlighted_content: highlightedContent,
        relevance_score: normalizedScore,
        article_type: row.metadata.article_type || 'article',
        related_articles: []
      };
    });

    return NextResponse.json({
      query: sanitizedQuery,
      total_found: articles.length,
      keywords,
      relevant_laws: [...new Set(articles.map((a: { law_name: string }) => a.law_name))],
      articles,
      metadata: {
        search_time_ms: 0,
        llm_used: false,
        search_method: 'keyword'
      }
    });

  } catch (error) {
    console.error('API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
