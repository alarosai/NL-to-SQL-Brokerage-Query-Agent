const fs = require('fs');
const env = fs.readFileSync('.env.local', 'utf8').split('\n').find(l => l.startsWith('GEMINI_API_KEY')).split('=')[1];
const { GoogleGenAI } = require('@google/genai');
const ai = new GoogleGenAI({ apiKey: env });

async function run() {
  const resp = await ai.models.generateContent({
    model: 'gemini-2.5-flash',
    contents: 'Write a SQL query for top 10 accounts.',
    config: {
      temperature: 0,
    }
  });
  console.log("RESPONSE:", resp.text);
}
run().catch(console.error);
