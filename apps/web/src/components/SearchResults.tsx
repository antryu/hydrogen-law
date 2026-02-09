'use client';

import { useState } from 'react';
import DOMPurify from 'dompurify';
import { Clock, FileText, Hash, Scale, ChevronDown, ChevronUp, TableProperties } from 'lucide-react';
import type { SearchResponse } from '@/types/search';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Button } from '@/components/ui/button';

const CONTENT_PREVIEW_LENGTH = 300;

interface SearchResultsProps {
  results: SearchResponse;
}

/** Format legal content: add line breaks before numbered items for readability */
function formatLegalContent(html: string): string {
  // Add line breaks before Korean legal numbering patterns
  let formatted = html;
  // Numbered items: 1., 2., 10. etc. (at start or after space)
  formatted = formatted.replace(/(?<=[.\s>])(\d+\.\s)/g, '<br/><br/>$1');
  // Korean letter items: 가., 나., 다. etc.
  formatted = formatted.replace(/(?<=[.\s>])([가-힣]\.\s)/g, '<br/>$1');
  // Circle numbers: ①, ②, ③ etc.
  formatted = formatted.replace(/([\u2460-\u2473\u3251-\u326D])/g, '<br/><br/>$1');
  // Korean ordinal markers: 제1호, 제2호 etc. at line start
  formatted = formatted.replace(/(?<=[.\s>])(제\d+[호조항])/g, '<br/>$1');
  // Clean up excessive line breaks
  formatted = formatted.replace(/(<br\s*\/?>\s*){3,}/g, '<br/><br/>');
  return formatted;
}

function isAppendix(article: SearchResponse['articles'][number]): boolean {
  return article.article_type === 'appendix'
    || article.article_number.includes('별표')
    || article.title.includes('별표');
}

function ArticleCard({ article, index }: { article: SearchResponse['articles'][number]; index: number }) {
  const appendix = isAppendix(article);
  // Appendix: collapsed by default; regular articles: expanded if short
  const [expanded, setExpanded] = useState(false);

  const rawSanitized = DOMPurify.sanitize(article.highlighted_content, {
    ALLOWED_TAGS: ['mark', 'br'],
    ALLOWED_ATTR: ['style'],
  });
  const sanitized = appendix ? formatLegalContent(rawSanitized) : rawSanitized;

  const isLong = article.content.length > CONTENT_PREVIEW_LENGTH;
  // Appendix is always collapsible regardless of length
  const collapsible = appendix || isLong;

  // For appendix: extract a short summary (first sentence or ~100 chars)
  const summaryText = (() => {
    if (!appendix) return '';
    const plain = article.content.replace(/\n/g, ' ').trim();
    const firstSentence = plain.match(/^.{0,150}[.)\]]\s/);
    return firstSentence ? firstSentence[0].trim() : plain.slice(0, 120) + '…';
  })();

  return (
    <Card className={`border-2 hover:border-primary/50 transition-all hover:shadow-lg ${appendix ? 'border-amber-200 dark:border-amber-800' : ''}`}>
      <CardHeader className={appendix ? 'pb-2' : ''}>
        <div className="flex items-start gap-4 flex-1">
          <div className={`flex-shrink-0 w-10 h-10 flex items-center justify-center rounded-full font-bold text-lg ${appendix ? 'bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300' : 'bg-primary text-primary-foreground'}`}>
            {appendix ? <TableProperties className="w-5 h-5" /> : index + 1}
          </div>
          <div className="space-y-1 flex-1">
            <div className="flex items-center gap-2 flex-wrap">
              <CardTitle className="text-xl leading-tight">
                {article.law_name} {article.article_number}
              </CardTitle>
              {appendix && (
                <Badge variant="secondary" className="text-xs bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300">
                  별표
                </Badge>
              )}
            </div>
            <CardDescription className="text-base">
              {article.title}
            </CardDescription>
            {/* Appendix: show summary when collapsed */}
            {appendix && !expanded && summaryText && (
              <p className="text-sm text-muted-foreground mt-2 line-clamp-2">
                {summaryText}
              </p>
            )}
          </div>
        </div>
      </CardHeader>

      {/* Content area: hidden for appendix when collapsed */}
      {(!appendix || expanded) && (
        <CardContent className="space-y-4">
          <div className="relative">
            <div
              className={`text-sm leading-relaxed text-muted-foreground bg-muted/30 p-4 rounded-lg ${!expanded && isLong ? 'max-h-40 overflow-hidden' : ''} ${appendix ? 'max-h-[60vh] overflow-y-auto' : ''}`}
              dangerouslySetInnerHTML={{ __html: sanitized }}
            />
            {!expanded && isLong && !appendix && (
              <div className="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-background to-transparent rounded-b-lg" />
            )}
          </div>

          {article.related_articles && article.related_articles.length > 0 && (
            <div className="space-y-2">
              <Separator />
              <div>
                <p className="text-sm font-semibold text-muted-foreground mb-2">
                  관련 조항
                </p>
                <div className="flex flex-wrap gap-2">
                  {article.related_articles.map((ref) => (
                    <Badge
                      key={ref.id}
                      variant="secondary"
                      className="cursor-pointer hover:bg-secondary/80"
                    >
                      {ref.article_number}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          )}
        </CardContent>
      )}

      {/* Expand/collapse button */}
      {collapsible && (
        <div className="px-6 pb-4">
          <Button
            variant="ghost"
            size="sm"
            className="w-full"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? (
              <>
                <ChevronUp className="w-4 h-4 mr-1" />
                접기
              </>
            ) : (
              <>
                <ChevronDown className="w-4 h-4 mr-1" />
                {appendix ? '별표 내용 보기' : '상세보기'}
              </>
            )}
          </Button>
        </div>
      )}
    </Card>
  );
}

export function SearchResults({ results }: SearchResultsProps) {
  return (
    <div className="space-y-6">
      {/* 검색 요약 */}
      <Card className="border-2">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5" />
              검색 결과: {results.total_found}건
            </CardTitle>
            <div className="flex items-center gap-3">
              <Badge variant="outline" className="gap-1.5">
                <Clock className="w-3.5 h-3.5" />
                {results.metadata.search_time_ms.toFixed(0)}ms
              </Badge>
              {!results.metadata.llm_used && (
                <Badge variant="secondary">AI 분석</Badge>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* 관련 법령 */}
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
              <Scale className="w-4 h-4" />
              관련 법령
            </div>
            <div className="flex flex-wrap gap-2">
              {results.relevant_laws.map((law) => (
                <Badge key={law} variant="default" className="text-sm py-1.5 px-3">
                  {law}
                </Badge>
              ))}
            </div>
          </div>

          <Separator />

          {/* 키워드 */}
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
              <Hash className="w-4 h-4" />
              검색 키워드
            </div>
            <div className="flex flex-wrap gap-2">
              {results.keywords.map((kw) => (
                <Badge key={kw} variant="outline" className="text-xs">
                  {kw}
                </Badge>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 조항 목록 */}
      {results.articles.map((article, i) => (
        <ArticleCard
          key={`${article.law_name}-${article.article_number}-${i}`}
          article={article}
          index={i}
        />
      ))}
    </div>
  );
}
