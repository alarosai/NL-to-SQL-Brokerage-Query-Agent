const { GoogleGenAI } = require('@google/genai');

const fs = require('fs');
// Load key safely
let key = process.env.GEMINI_API_KEY;
if (!key) {
  const envFile = fs.readFileSync('.env.local', 'utf8');
  const match = envFile.match(/GEMINI_API_KEY=(.*)/);
  if (match) key = match[1].replace(/["']/g, '');
}

const ai = new GoogleGenAI({ apiKey: key });

const prompt = `You are an expert SQL generator for a brokerage database.
Your job is to translate the user's natural language query into a raw SQLite query.

CRITICAL RULES:
- Return ONLY the raw SQL query, absolutely no markdown formatting, no \`\`\`sql block, no explanation.
- ONLY read operations using SELECT are allowed. NEVER use UPDATE, DELETE, DROP, INSERT, etc.
- Always use LIMIT 100 on open-ended queries unless the user asks for aggregation/counts to prevent huge returns.
- Assume all price columns/totals should be rounded appropriately.`;

async function run() {
  console.log("Starting...");
  const resp = await ai.models.generateContent({
    model: 'gemini-2.5-flash',
    contents: 'Show me the top 10 accounts by trading volume last week',
    config: {
      systemInstruction: prompt,
      temperature: 0,
      maxOutputTokens: 300,
    }
  });
  console.log("RESPONSE DATA:");
  console.log(JSON.stringify(resp, null, 2));
}
run().catch(console.error);
