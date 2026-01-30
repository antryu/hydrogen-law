const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');

const envContent = fs.readFileSync(path.join(__dirname, '.env.local'), 'utf8');
const envVars = {};
envContent.split('\n').forEach(line => {
  const match = line.match(/^([^=]+)=(.*)$/);
  if (match) {
    envVars[match[1].trim()] = match[2].trim();
  }
});

const supabase = createClient(envVars.NEXT_PUBLIC_SUPABASE_URL, envVars.SUPABASE_SERVICE_ROLE_KEY);

async function main() {
  // LIKE로 직접 검색
  const { data } = await supabase
    .from('law_documents')
    .select('id, metadata, content')
    .like('content', '%유통%');

  console.log(`"유통" 포함 문서: ${data.length}개\n`);

  // 법령별 분류
  const byLaw = {};
  data.forEach(d => {
    const law = d.metadata.law_name;
    if (!byLaw[law]) byLaw[law] = [];
    byLaw[law].push(d);
  });

  console.log('법령별 분포:');
  Object.entries(byLaw).forEach(([law, docs]) => {
    const shortName = law.includes('시행규칙') ? '시행규칙' :
                      law.includes('시행령') ? '시행령' : '법률';
    console.log(`\n${shortName} (${law}): ${docs.length}개`);

    docs.forEach((d, i) => {
      const count = (d.content.match(/유통/g) || []).length;
      console.log(`  ${i + 1}. ${d.metadata.article_number} (${d.metadata.title || '제목없음'})`);
      console.log(`     출현 횟수: ${count}회`);

      // 첫 출현 위치 보기
      const idx = d.content.indexOf('유통');
      if (idx >= 0) {
        const snippet = d.content.substring(Math.max(0, idx - 30), Math.min(d.content.length, idx + 50));
        console.log(`     내용: ...${snippet}...`);
      }
    });
  });

  console.log('\n' + '='.repeat(60));

  // RPC 검색 결과와 비교
  const { data: rpcData } = await supabase.rpc('search_law_documents', {
    search_query: '유통',
    max_results: 10
  });

  console.log(`\nRPC 검색 결과: ${rpcData.length}개\n`);
  rpcData.forEach((r, i) => {
    const shortName = r.metadata.law_name.includes('시행규칙') ? '시행규칙' :
                      r.metadata.law_name.includes('시행령') ? '시행령' : '법률';
    console.log(`${i + 1}. ${shortName} ${r.metadata.article_number} (점수: ${r.relevance_score.toFixed(1)})`);
  });
}

main();
