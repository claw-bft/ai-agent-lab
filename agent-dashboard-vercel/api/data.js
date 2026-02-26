// Vercel Serverless Function - 返回Dashboard数据
export default function handler(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', '*');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  // 读取本地JSON文件
  const fs = require('fs');
  const path = require('path');
  
  try {
    const dataPath = path.join(process.cwd(), 'data', 'dashboard.json');
    const data = fs.readFileSync(dataPath, 'utf8');
    const json = JSON.parse(data);
    
    res.status(200).json(json);
  } catch (error) {
    res.status(500).json({ error: 'Failed to read data', message: error.message });
  }
}
