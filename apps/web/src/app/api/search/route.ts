import { createClient } from '@supabase/supabase-js';
import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const { query, top_k = 10 } = await request.json();

    if (!query || typeof query !== 'string') {
      return NextResponse.json(
        { error: 'Invalid query parameter' },
        { status: 400 }
      );
    }

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
      search_query: query,
      max_results: top_k
    });

    if (error) {
      console.error('Supabase error:', error);
      return NextResponse.json(
        { error: 'Search failed', details: error.message },
        { status: 500 }
      );
    }

    // Normalize relevance scores to 0-100 range
    const maxScore = Math.max(...data.map((row: any) => row.relevance_score), 0.0001);

    // Transform results to match frontend expectations
    const articles = data.map((row: any) => {
      // Debug: Log article_type
      console.log('Article:', row.metadata.article_number, 'Type:', row.metadata.article_type);

      // Highlight search keywords in content
      const keywords = query.trim().split(/\s+/);
      let highlightedContent = row.content;

      keywords.forEach(keyword => {
        const regex = new RegExp(`(${keyword})`, 'gi');
        highlightedContent = highlightedContent.replace(
          regex,
          '<mark style="background-color: #fef08a; padding: 2px 4px; border-radius: 2px;">$1</mark>'
        );
      });

      // Convert newlines to <br> tags for HTML rendering
      highlightedContent = highlightedContent.replace(/\n/g, '<br>');

      // Improve readability with formatting
      // Make article/clause numbers bold
      highlightedContent = highlightedContent.replace(/(제\d+조의?\d*)/g, '<strong class="text-gray-900">$1</strong>');
      highlightedContent = highlightedContent.replace(/(별표\s*\d+)/g, '<strong class="text-gray-900">$1</strong>');

      // Add indentation for items (①, ②, etc.)
      highlightedContent = highlightedContent.replace(/<br>([①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮])/g, '<br><span class="inline-block ml-4">$1');

      // Add indentation for numbered items (1., 2., etc.)
      highlightedContent = highlightedContent.replace(/<br>(\d+\.)/g, '<br><span class="inline-block ml-8">$1');

      // Add indentation for lettered items (가., 나., etc.)
      highlightedContent = highlightedContent.replace(/<br>([가-힣]\.)/g, '<br><span class="inline-block ml-12">$1');

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
      query,
      total_found: articles.length,
      keywords: query.split(' ').filter((k: string) => k.length > 1),
      relevant_laws: [...new Set(articles.map((a: any) => a.law_name))],
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
