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

    // Parse and limit keywords (support both comma and space separation)
    const keywords = sanitizedQuery
      .split(/[\s,]+/)
      .filter((k: string) => k.length > 0)
      .slice(0, MAX_KEYWORDS);

    // Search each keyword individually and merge results
    // This fixes the bug where multi-keyword queries (e.g. "수소 안전") returned 0 results
    // because the SQL LIKE searched for the entire string as one substring
    let data: SupabaseSearchResult[];

    if (keywords.length <= 1) {
      // Single keyword: search directly
      const { data: result, error } = await supabase.rpc('search_law_documents', {
        search_query: sanitizedQuery,
        max_results: validatedTopK
      });

      if (error) {
        console.error('Supabase error:', error);
        return NextResponse.json(
          { error: '검색 중 오류가 발생했습니다' },
          { status: 500 }
        );
      }

      data = result;
    } else {
      // Multiple keywords: search each individually and merge
      const searchPromises = keywords.map(keyword =>
        supabase.rpc('search_law_documents', {
          search_query: keyword,
          max_results: validatedTopK
        })
      );

      const searchResults = await Promise.all(searchPromises);

      // Check for errors
      const firstError = searchResults.find(r => r.error);
      if (firstError?.error) {
        console.error('Supabase error:', firstError.error);
        return NextResponse.json(
          { error: '검색 중 오류가 발생했습니다' },
          { status: 500 }
        );
      }

      // Merge results: documents matching more keywords get higher combined scores
      const mergedMap = new Map<string, SupabaseSearchResult & { matchCount: number }>();

      for (const result of searchResults) {
        if (!result.data) continue;
        for (const row of result.data as SupabaseSearchResult[]) {
          const existing = mergedMap.get(row.id);
          if (existing) {
            existing.relevance_score += row.relevance_score;
            existing.matchCount += 1;
          } else {
            mergedMap.set(row.id, { ...row, matchCount: 1 });
          }
        }
      }

      // Boost documents that match more keywords
      for (const entry of mergedMap.values()) {
        entry.relevance_score *= (1 + (entry.matchCount - 1) * 0.5);
      }

      data = [...mergedMap.values()]
        .sort((a, b) => b.relevance_score - a.relevance_score)
        .slice(0, validatedTopK);
    }

    if (!data || data.length === 0) {
      return NextResponse.json({
        query: sanitizedQuery,
        total_found: 0,
        keywords,
        relevant_laws: [],
        articles: [],
        metadata: {
          search_time_ms: 0,
          llm_used: false,
          search_method: 'keyword'
        }
      });
    }

    // Normalize relevance scores to 0-100 range
    const maxScore = Math.max(...data.map((row: SupabaseSearchResult) => row.relevance_score), 0.0001);

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
        law_name: row.metadata.law_name || '(법령명 없음)',
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
