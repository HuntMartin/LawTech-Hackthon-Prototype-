import express from 'express';
import { TinfoilAI } from 'tinfoil';
import fs from 'fs/promises';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';


const app = express();
app.use(express.json());
app.use(cors());
const client = new TinfoilAI({
  apiKey: 'Your_Key_API',
  dangerouslyAllowBrowser: 'true'
});
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const historyFile = path.join(__dirname, 'memoryNotes.json');

async function loadHistory(){
    try{
        const data = await fs.readFile(historyFile, 'utf-8');
        return JSON.parse(data); // format array of {role, content}
    } catch {
        return []; 
    }
}

let chatHistory = await loadHistory();

app.post('/ask', async (req, res) => {
  const { question } = req.body;
  if (!question) return res.status(400).json({ error: 'No question provided' });

  chatHistory.push({ role: 'user', content: question });

  try {
    const completion = await client.chat.completions.create({
      messages: chatHistory,
      model: 'deepseek-r1-0528'
    });

    const reply = completion.choices[0]?.message?.content || 'No answer';
    chatHistory.push({ role: 'assistant', content: reply });
    await fs.writeFile(historyFile, JSON.stringify(chatHistory, null, 2));
    res.json({ answer: reply });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'AI client error' });
  }
});

app.listen(5000, () => {
  console.log('Node.js AI API listening on port 5000');
});
