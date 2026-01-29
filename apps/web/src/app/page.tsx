'use client';

import { useState } from 'react';
import { Search, Zap, Shield, Clock, Database, CheckCircle2 } from 'lucide-react';
import type { SearchResponse } from '@/types/search';
import { SearchResults } from '@/components/SearchResults';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';

export default function HomePage() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query.trim(), top_k: 5 }),
      });

      if (!response.ok) {
        throw new Error('검색 실패');
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : '서버 연결 실패. 백엔드 서버가 실행 중인지 확인하세요.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <section className="text-center space-y-8 pt-12">
        <div className="inline-flex items-center gap-2 px-5 py-2.5 bg-primary/10 rounded-full">
          <Zap className="w-4 h-4 text-primary" />
          <span className="text-sm font-semibold tracking-wide">AI 기반 지능형 검색</span>
        </div>

        <h1 className="text-6xl font-bold tracking-tight leading-tight">
          수소법률 검색의
          <br />
          <span className="bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">
            새로운 기준
          </span>
        </h1>

        <p className="text-2xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
          154개 법령 조문을 80ms 이내에 검색하는 초고속 법률 검색 엔진
        </p>
      </section>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="border-2 hover:border-primary/50 transition-colors">
          <CardHeader className="pb-4 text-center">
            <Database className="w-10 h-10 text-primary mb-3 mx-auto" />
            <CardTitle className="text-4xl mb-2">154개</CardTitle>
            <CardDescription className="text-base">법령 조문</CardDescription>
          </CardHeader>
        </Card>

        <Card className="border-2 hover:border-primary/50 transition-colors">
          <CardHeader className="pb-4 text-center">
            <Clock className="w-10 h-10 text-primary mb-3 mx-auto" />
            <CardTitle className="text-4xl mb-2">&lt;80ms</CardTitle>
            <CardDescription className="text-base">응답시간</CardDescription>
          </CardHeader>
        </Card>

        <Card className="border-2 hover:border-primary/50 transition-colors">
          <CardHeader className="pb-4 text-center">
            <Shield className="w-10 h-10 text-primary mb-3 mx-auto" />
            <CardTitle className="text-4xl mb-2">100%</CardTitle>
            <CardDescription className="text-base">정확도</CardDescription>
          </CardHeader>
        </Card>
      </div>

      {/* Search Section */}
      <section className="text-center space-y-8">
        <div className="space-y-3">
          <div className="flex justify-center">
            <div className="p-3 bg-primary/10 rounded-xl">
              <Search className="w-8 h-8 text-primary" />
            </div>
          </div>
          <h2 className="text-3xl font-bold">법령 검색</h2>
          <p className="text-base text-muted-foreground max-w-xl mx-auto">
            자연어로 질문하시면 관련 법령을 즉시 찾아드립니다
          </p>
        </div>

        <div className="max-w-2xl mx-auto space-y-4">
          <form onSubmit={handleSearch} className="space-y-4">
            <Input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="예: 고압가스 제조 허가, 수소충전소 설치 기준"
              className="h-16 text-lg px-6"
            />
            <Button
              type="submit"
              disabled={loading || !query}
              className="w-full h-14 text-lg font-semibold"
              size="lg"
            >
              {loading ? (
                <>
                  <Clock className="w-5 h-5 mr-2 animate-spin" />
                  검색 중
                </>
              ) : (
                <>
                  <Search className="w-5 h-5 mr-2" />
                  검색
                </>
              )}
            </Button>
          </form>

          <div className="flex flex-wrap gap-3 items-center justify-center">
            <Badge variant="secondary" className="gap-1.5 py-1.5 px-3 text-sm">
              <CheckCircle2 className="w-4 h-4" />
              LLM 미사용
            </Badge>
            <Separator orientation="vertical" className="h-5" />
            <span className="text-sm font-medium text-muted-foreground">1초 이내</span>
            <Separator orientation="vertical" className="h-5" />
            <span className="text-sm font-medium text-muted-foreground">100% 정확</span>
          </div>

          {error && (
            <div className="p-4 border border-destructive bg-destructive/10 rounded-lg text-center">
              <p className="text-base text-destructive font-semibold">
                ❌ {error}
              </p>
            </div>
          )}
        </div>
      </section>

      {/* Search Results */}
      {results && <SearchResults results={results} />}

      {/* Features Section */}
      <section className="text-center space-y-12">
        <h2 className="text-3xl font-bold">주요 기능</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 max-w-4xl mx-auto">
          <div className="space-y-6">
            <div className="flex justify-center">
              <div className="p-3 bg-primary/10 rounded-xl">
                <Search className="w-8 h-8 text-primary" />
              </div>
            </div>
            <div className="space-y-3">
              <h3 className="text-2xl font-bold">하이브리드 검색</h3>
              <p className="text-base text-muted-foreground leading-relaxed">
                벡터 검색 + BM25로 의미와 키워드 모두 고려
              </p>
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-center gap-3 text-base">
                <CheckCircle2 className="w-5 h-5 text-primary flex-shrink-0" />
                <span>한국어 특화 임베딩</span>
              </div>
              <div className="flex items-center justify-center gap-3 text-base">
                <CheckCircle2 className="w-5 h-5 text-primary flex-shrink-0" />
                <span>규칙 기반 재랭킹</span>
              </div>
              <div className="flex items-center justify-center gap-3 text-base">
                <CheckCircle2 className="w-5 h-5 text-primary flex-shrink-0" />
                <span>조항 간 참조 자동 추출</span>
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className="flex justify-center">
              <div className="p-3 bg-primary/10 rounded-xl">
                <Shield className="w-8 h-8 text-primary" />
              </div>
            </div>
            <div className="space-y-3">
              <h3 className="text-2xl font-bold">컴플라이언스 체크</h3>
              <p className="text-base text-muted-foreground leading-relaxed">
                사업 유형별 필수 법령 자동 매칭
              </p>
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-center gap-3 text-base">
                <CheckCircle2 className="w-5 h-5 text-primary flex-shrink-0" />
                <span>수소충전소 설치/운영</span>
              </div>
              <div className="flex items-center justify-center gap-3 text-base">
                <CheckCircle2 className="w-5 h-5 text-primary flex-shrink-0" />
                <span>수소 생산 시설</span>
              </div>
              <div className="flex items-center justify-center gap-3 text-base">
                <CheckCircle2 className="w-5 h-5 text-primary flex-shrink-0" />
                <span>수소 저장소</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
