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
  const separator = '='.repeat(60);
  console.log('\n' + separator);
  console.log('검색어: "' + query + '"');
  console.log(separator);

  const { data, error } = await supabase.rpc('search_law_documents', {
    search_query: query,
    max_results: 10
  });

  if (error) {
    console.error('Error:', error);
    return;
  }

  console.log('\n총 ' + data.length + '개 결과 발견\n');

  data.forEach((r, i) => {
    console.log((i + 1) + '. ' + (r.metadata.law_name || 'Unknown'));
    console.log('   조항: ' + (r.metadata.article_number || r.id));
    console.log('   관련도: ' + r.relevance_score.toFixed(2));

    // Show first occurrence
    const index = r.content.indexOf(query);
    if (index !== -1) {
      const start = Math.max(0, index - 30);
      const end = Math.min(r.content.length, index + query.length + 30);
      const snippet = r.content.substring(start, end);
      console.log('   내용: ...' + snippet + '...');
    }
    console.log();
  });
}

async function main() {
  await testSearch('충전압');
  await testSearch('충전압력');
}

main();
