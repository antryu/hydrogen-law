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
  const { data } = await supabase
    .from('law_documents')
    .select('content, metadata')
    .limit(200);

  // Get samples from each law
  const laws = ['고압가스 안전관리법', '고압가스 안전관리법 시행령', '고압가스 안전관리법 시행규칙'];

  laws.forEach(lawName => {
    const samples = data.filter(d => d.metadata.law_name === lawName).slice(0, 2);

    console.log('\n' + '='.repeat(60));
    console.log(lawName);
    console.log('='.repeat(60));

    samples.forEach((doc, i) => {
      console.log('\n[샘플 ' + (i + 1) + '] ' + doc.metadata.article_number);
      console.log('길이: ' + doc.content.length + '자');
      console.log('\n전체 내용:');
      console.log(doc.content);
      console.log('\n' + '-'.repeat(60));
    });
  });
}

main();
