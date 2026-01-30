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

if (!supabaseUrl || !supabaseKey) {
  console.error('Missing Supabase credentials');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

async function updateSearchFunction() {
  try {
    console.log('Testing current search function with "충전"...\n');

    const result = await supabase.rpc('search_law_documents', {
      search_query: '충전',
      max_results: 10
    });

    if (result.error) {
      console.error('Search error:', result.error);
      process.exit(1);
    }

    console.log(`Found ${result.data.length} results:\n`);
    result.data.forEach((r, i) => {
      const score = typeof r.relevance_score === 'number' ? r.relevance_score.toFixed(2) : r.relevance_score;
      console.log(`${i+1}. ${r.id}`);
      console.log(`   Law: ${r.metadata.law_name || 'Unknown'}`);
      console.log(`   Score: ${score}`);
      console.log();
    });

    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('⚠️  Current search function uses full-text search (to_tsvector)');
    console.log('   which does not work well for Korean text.');
    console.log('');
    console.log('✅  New search function uses LIKE pattern matching');
    console.log('   which will find all occurrences of Korean keywords.');
    console.log('');
    console.log('📝 To update the function in Supabase:');
    console.log('   1. Open Supabase Dashboard: https://supabase.com/dashboard');
    console.log('   2. Go to SQL Editor');
    console.log('   3. Copy and run SQL from:');
    console.log('      services/rag-engine/search_function.sql');

  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

updateSearchFunction();
