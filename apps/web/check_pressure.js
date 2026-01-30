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
    .like('content', '%압력%');

  console.log('"압력" 포함 문서: ' + data.length + '개\n');

  data.forEach((d, i) => {
    const count = (d.content.match(/압력/g) || []).length;
    const shortName = d.metadata.law_name.includes('시행규칙') ? '시행규칙' :
                      d.metadata.law_name.includes('시행령') ? '시행령' : '법률';
    console.log((i + 1) + '. ' + shortName + ' ' + d.metadata.article_number);
    console.log('   출현 횟수: ' + count + '회');

    // 첫 출현 위치 보기
    const idx = d.content.indexOf('압력');
    if (idx >= 0) {
      const snippet = d.content.substring(Math.max(0, idx - 30), Math.min(d.content.length, idx + 35));
      console.log('   내용: ...' + snippet + '...');
    }
    console.log();
  });

  // RPC 검색 결과와 비교
  console.log('='.repeat(60));
  const { data: rpcData } = await supabase.rpc('search_law_documents', {
    search_query: '압력',
    max_results: 10
  });

  console.log('\nRPC 검색 결과: ' + rpcData.length + '개\n');
  rpcData.forEach((r, i) => {
    const shortName = r.metadata.law_name.includes('시행규칙') ? '시행규칙' :
                      r.metadata.law_name.includes('시행령') ? '시행령' : '법률';
    console.log((i + 1) + '. ' + shortName + ' ' + r.metadata.article_number + ' (점수: ' + r.relevance_score.toFixed(1) + ')');
  });
}

main();
