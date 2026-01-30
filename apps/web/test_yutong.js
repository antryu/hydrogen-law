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
  const { data, error } = await supabase.rpc('search_law_documents', {
    search_query: '유통',
    max_results: 5
  });

  if (error) {
    console.error('Error:', error);
    return;
  }

  console.log('"유통" 검색: ' + data.length + '개 결과\n');

  data.forEach((r, i) => {
    console.log((i + 1) + '. ' + r.metadata.law_name);
    console.log('   조항: ' + r.metadata.article_number);
    console.log('   관련도: ' + r.relevance_score.toFixed(2));

    const idx = r.content.indexOf('유통');
    if (idx !== -1) {
      const start = Math.max(0, idx - 30);
      const end = Math.min(r.content.length, idx + 35);
      const snippet = r.content.substring(start, end);
      console.log('   내용: ...' + snippet + '...');
    }
    console.log();
  });
}

main();
