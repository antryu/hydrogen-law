'use client';

import { useState } from 'react';
import { Search, Scale, Clock, CheckCircle2 } from 'lucide-react';
import type { SearchResponse } from '@/types/search';
import { SearchResults } from '@/components/SearchResults';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';

export default function HomePage() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) {
      setError('검색어를 입력해주세요.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query.trim(), top_k: 100 }),
      });

      const text = await response.text();
      let data;
      try {
        data = JSON.parse(text);
      } catch {
        throw new Error('서버 응답을 처리할 수 없습니다. 잠시 후 다시 시도해주세요.');
      }

      if (!response.ok) {
        throw new Error(data?.error || '검색 중 오류가 발생했습니다.');
      }

      setResults(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : '검색 서버 연결에 실패했습니다. 잠시 후 다시 시도해주세요.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen px-4 sm:px-6 lg:px-8 py-8 sm:py-12 md:py-16">
      {/* Search Section */}
      <section className="text-center space-y-6 sm:space-y-8 max-w-6xl mx-auto w-full mb-8">
        <div className="space-y-3 sm:space-y-4">
          <div className="flex justify-center">
            <div className="p-2.5 sm:p-3 bg-primary/10 rounded-xl">
              <Scale className="w-6 h-6 sm:w-8 sm:h-8 text-primary" />
            </div>
          </div>
          <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold">법령 검색</h2>
          <p className="text-sm sm:text-base text-muted-foreground max-w-xl mx-auto px-4">
            자연어로 질문하시면 관련 법령을 즉시 찾아드립니다
          </p>
        </div>

        <div className="max-w-4xl mx-auto space-y-4">
          <form onSubmit={handleSearch} className="space-y-3 sm:space-y-4">
            <Input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSearch(e as unknown as React.FormEvent);
                }
              }}
              placeholder="예: 수소충전소, 안전기준 (콤마 또는 공백으로 키워드 구분)"
              className="h-12 sm:h-14 lg:h-16 text-base sm:text-lg px-4 sm:px-6"
            />
            <Button
              type="submit"
              disabled={loading || !query}
              className="w-full h-12 sm:h-14 text-base sm:text-lg font-semibold"
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

          <div className="flex flex-wrap gap-2 sm:gap-3 items-center justify-center text-xs sm:text-sm">
            <Badge variant="secondary" className="gap-1 sm:gap-1.5 py-1 sm:py-1.5 px-2 sm:px-3">
              <CheckCircle2 className="w-3 h-3 sm:w-4 sm:h-4" />
              LLM 미사용
            </Badge>
            <Separator orientation="vertical" className="h-4 sm:h-5 hidden sm:block" />
            <span className="font-medium text-muted-foreground">1초 이내</span>
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
      {results && (
        <>
          <div className="text-xs text-gray-400 text-center mb-2">
            v1.0.1 - 검색 결과 최대 100개 표시
          </div>
          <SearchResults results={results} />
        </>
      )}
    </div>
  );
}
