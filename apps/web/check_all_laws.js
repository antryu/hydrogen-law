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
    max_results: 10
  });

  if (error) {
    console.error('Error:', error);
    return;
  }

  console.log('\n"' + query + '" 검색 결과: ' + data.length + '개');
  console.log('='.repeat(60));

  // Group by law name
  const byLaw = {};
  data.forEach(r => {
    const lawName = r.metadata.law_name || 'Unknown';
    if (!byLaw[lawName]) {
      byLaw[lawName] = 0;
    }
    byLaw[lawName]++;
  });

  Object.entries(byLaw).forEach(([law, count]) => {
    console.log('  ' + law + ': ' + count + '개');
  });
}

async function main() {
  await testSearch('고압가스');
  await testSearch('압력');
  await testSearch('충전');
  await testSearch('안전');
  await testSearch('허가');
}

main();
