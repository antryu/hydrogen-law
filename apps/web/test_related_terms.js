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

async function testSearch(query) {
  const { data, error } = await supabase.rpc('search_law_documents', {
    search_query: query,
    max_results: 5
  });

  if (error) {
    console.error('Error:', error);
    return;
  }

  console.log('\n"' + query + '" 검색: ' + data.length + '개 결과');
  if (data.length > 0) {
    data.slice(0, 2).forEach((r, i) => {
      const index = r.content.indexOf(query);
      if (index !== -1) {
        const start = Math.max(0, index - 40);
        const end = Math.min(r.content.length, index + query.length + 40);
        const snippet = r.content.substring(start, end);
        console.log('  ' + (i + 1) + '. ...' + snippet + '...');
      }
    });
  }
}

async function main() {
  console.log('관련 용어 검색 테스트:');
  console.log('='.repeat(60));

  await testSearch('압력');
  await testSearch('충전');
  await testSearch('압');
  await testSearch('충전압');
  await testSearch('충전압력');
  await testSearch('최고충전압력');
  await testSearch('최고 충전 압력');
}

main();
