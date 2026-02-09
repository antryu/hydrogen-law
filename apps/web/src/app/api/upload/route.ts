import { createClient } from '@supabase/supabase-js';
import { NextResponse } from 'next/server';

const RAG_ENGINE_URL = process.env.RAG_ENGINE_URL || 'http://localhost:8000';
const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const file = formData.get('file') as File | null;
    const lawName = formData.get('law_name') as string | null;
    const lawId = formData.get('law_id') as string | null;

    if (!file) {
      return NextResponse.json(
        { error: 'PDF 파일을 선택해주세요' },
        { status: 400 }
      );
    }

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      return NextResponse.json(
        { error: 'PDF 파일만 업로드 가능합니다' },
        { status: 400 }
      );
    }

    if (file.size > MAX_FILE_SIZE) {
      return NextResponse.json(
        { error: '파일 크기는 50MB를 초과할 수 없습니다' },
        { status: 400 }
      );
    }

    if (!lawName || !lawName.trim()) {
      return NextResponse.json(
        { error: '법령명을 입력해주세요' },
        { status: 400 }
      );
    }

    // Forward to RAG engine for full pipeline processing
    const ragFormData = new FormData();
    ragFormData.append('file', file);
    ragFormData.append('law_name', lawName.trim());
    if (lawId) {
      ragFormData.append('law_id', lawId.trim());
    }

    const ragResponse = await fetch(`${RAG_ENGINE_URL}/upload`, {
      method: 'POST',
      body: ragFormData,
    });

    if (!ragResponse.ok) {
      const errorData = await ragResponse.json().catch(() => ({}));
      const detail = errorData.detail || 'RAG 엔진 처리 실패';
      return NextResponse.json(
        { error: detail },
        { status: ragResponse.status }
      );
    }

    const result = await ragResponse.json();

    // Verify data is in Supabase
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

    let supabaseVerification = null;
    if (supabaseUrl && supabaseKey) {
      const supabase = createClient(supabaseUrl, supabaseKey);
      const generatedLawId = lawId?.trim() || lawName.trim().replace(/[^a-zA-Z0-9가-힣]/g, '_').slice(0, 50);

      const { count, error } = await supabase
        .from('law_documents')
        .select('id', { count: 'exact', head: true })
        .filter('metadata->>law_id', 'eq', generatedLawId);

      if (!error) {
        supabaseVerification = { document_count: count };
      }
    }

    return NextResponse.json({
      ...result,
      supabase_verification: supabaseVerification,
    });

  } catch (error) {
    console.error('Upload API error:', error);

    if (error instanceof TypeError && (error as TypeError).message.includes('fetch')) {
      return NextResponse.json(
        { error: 'RAG 엔진에 연결할 수 없습니다. RAG 엔진이 실행 중인지 확인해주세요. (uvicorn main:app --reload)' },
        { status: 503 }
      );
    }

    return NextResponse.json(
      { error: '업로드 처리 중 오류가 발생했습니다' },
      { status: 500 }
    );
  }
}
