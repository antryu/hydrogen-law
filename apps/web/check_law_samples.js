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
  // Get all documents
  const { data: allDocs } = await supabase
    .from('law_documents')
    .select('id, content, metadata')
    .limit(200);

  // Group by law
  const byLaw = {};
  allDocs.forEach(doc => {
    const lawName = doc.metadata.law_name;
    if (!byLaw[lawName]) {
      byLaw[lawName] = [];
    }
    byLaw[lawName].push(doc);
  });

  console.log('데이터베이스 통계:');
  console.log('='.repeat(60));

  Object.entries(byLaw).forEach(([law, docs]) => {
    console.log('\n' + law + ': ' + docs.length + '개 문서');

    // Calculate average content length
    const avgLength = docs.reduce((sum, d) => sum + d.content.length, 0) / docs.length;
    console.log('  평균 문서 길이: ' + avgLength.toFixed(0) + ' 자');

    // Check for common terms
    const terms = ['고압가스', '압력', '충전', '안전', '허가'];
    terms.forEach(term => {
      const count = docs.filter(d => d.content.includes(term)).length;
      console.log('  "' + term + '" 포함 문서: ' + count + '개 (' + (count / docs.length * 100).toFixed(1) + '%)');
    });

    // Show first document sample
    console.log('\n  샘플 (첫 200자):');
    console.log('  ' + docs[0].content.substring(0, 200).replace(/\n/g, ' ') + '...');
  });
}

main();
