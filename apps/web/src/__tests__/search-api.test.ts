import { describe, it, expect } from 'vitest';

// Extract pure functions for testing
function escapeRegex(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function parseKeywords(query: string, maxKeywords: number = 20): string[] {
  return query
    .split(/[\s,]+/)
    .filter((k: string) => k.length > 0)
    .slice(0, maxKeywords);
}

function validateQuery(query: unknown): { valid: boolean; error?: string; sanitized?: string } {
  if (!query || typeof query !== 'string' || !query.trim()) {
    return { valid: false, error: '검색어를 입력해주세요' };
  }
  return { valid: true, sanitized: query.trim().slice(0, 500) };
}

function normalizeScore(score: number, maxScore: number): number {
  return (score / maxScore) * 100;
}

describe('escapeRegex', () => {
  it('should escape special regex characters', () => {
    expect(escapeRegex('hello.world')).toBe('hello\\.world');
    expect(escapeRegex('a+b*c?')).toBe('a\\+b\\*c\\?');
    expect(escapeRegex('(test)')).toBe('\\(test\\)');
    expect(escapeRegex('[bracket]')).toBe('\\[bracket\\]');
  });

  it('should not modify plain text', () => {
    expect(escapeRegex('수소충전소')).toBe('수소충전소');
    expect(escapeRegex('hello')).toBe('hello');
  });

  it('should handle empty string', () => {
    expect(escapeRegex('')).toBe('');
  });
});

describe('parseKeywords', () => {
  it('should split by spaces', () => {
    expect(parseKeywords('수소 충전소')).toEqual(['수소', '충전소']);
  });

  it('should split by commas', () => {
    expect(parseKeywords('수소,충전소,안전')).toEqual(['수소', '충전소', '안전']);
  });

  it('should split by mixed separators', () => {
    expect(parseKeywords('수소, 충전소 안전')).toEqual(['수소', '충전소', '안전']);
  });

  it('should filter empty strings', () => {
    expect(parseKeywords('수소  충전소')).toEqual(['수소', '충전소']);
  });

  it('should limit keywords', () => {
    const many = Array.from({ length: 30 }, (_, i) => `kw${i}`).join(' ');
    expect(parseKeywords(many)).toHaveLength(20);
  });
});

describe('validateQuery', () => {
  it('should reject empty query', () => {
    expect(validateQuery('')).toEqual({ valid: false, error: '검색어를 입력해주세요' });
  });

  it('should reject null', () => {
    expect(validateQuery(null)).toEqual({ valid: false, error: '검색어를 입력해주세요' });
  });

  it('should reject whitespace-only', () => {
    expect(validateQuery('   ')).toEqual({ valid: false, error: '검색어를 입력해주세요' });
  });

  it('should accept valid query', () => {
    const result = validateQuery('수소충전소');
    expect(result.valid).toBe(true);
    expect(result.sanitized).toBe('수소충전소');
  });

  it('should trim whitespace', () => {
    const result = validateQuery('  수소  ');
    expect(result.sanitized).toBe('수소');
  });

  it('should truncate long queries to 500 chars', () => {
    const long = 'a'.repeat(600);
    const result = validateQuery(long);
    expect(result.sanitized).toHaveLength(500);
  });
});

describe('normalizeScore', () => {
  it('should normalize max score to 100', () => {
    expect(normalizeScore(10, 10)).toBe(100);
  });

  it('should normalize proportionally', () => {
    expect(normalizeScore(5, 10)).toBe(50);
  });

  it('should handle zero score', () => {
    expect(normalizeScore(0, 10)).toBe(0);
  });
});
