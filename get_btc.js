const WebSocket = require('ws');
const url = 'wss://fstream.binance.com/ws/btcusdt@aggTrade';
const ws = new WebSocket(url);

let lastLogTime = 0; // 記錄上一次印出的時間

ws.on('message', (data) => {
    const now = Date.now();
    
    // 只有距離上次印出超過 1000 毫秒（1秒）時才執行
    if (now - lastLogTime > 1000) {
        const msg = JSON.parse(data);
        console.log(`[BTC 即時價] ${msg.p}`);
        
        lastLogTime = now; // 更新紀錄時間
    }
});

ws.on('open', () => console.log('✅ 已連線，設定為每秒顯示一次...'));