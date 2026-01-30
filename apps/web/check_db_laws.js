const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');

// Read environment variables from .env.local
const envContent = fs.readFileSync(path.join(__dirname, '.env.local'), 'utf8');
const envVars = {};
envContent.split('\n').forEach(line => {
  const match = line.match(/^([^=]+)=(.*)$/);
  if (match) {
    envVars[match[1].trim()] = match[2].trim();
  }
});

const supabaseUrl = envVars.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = envVars.SUPABASE_SERVICE_ROLE_KEY;

const supabase = createClient(supabaseUrl, supabaseKey);

async function checkDatabaseLaws() {
  try {
    // Get all unique law names
    const { data, error } = await supabase
      .from('law_documents')
      .select('metadata');

    if (error) throw error;

    // Extract unique law names
    const lawNames = new Set();
    data.forEach(doc => {
      if (doc.metadata && doc.metadata.law_name) {
        lawNames.add(doc.metadata.law_name);
      }
    });

    console.log(`\n총 ${data.length}개의 문서가 데이터베이스에 있습니다.\n`);
    console.log('법령 목록:');
    console.log('━'.repeat(50));

    const lawList = Array.from(lawNames).sort();
    lawList.forEach((law, i) => {
      const count = data.filter(d => d.metadata.law_name === law).length;
      console.log(`${i + 1}. ${law}`);
      console.log(`   (${count}개 조문)`);
    });

    console.log('\n━'.repeat(50));
    console.log(`총 ${lawList.length}개의 법령`);

  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

checkDatabaseLaws();
