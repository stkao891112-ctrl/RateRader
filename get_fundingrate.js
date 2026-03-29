const WebSocket = require('ws');
const ws = new WebSocket('wss://fstream.binance.com/ws');

// 儲存所有幣種資訊的資料庫
let marketData = {};

ws.on('open', () => {
    console.log('✅ 連線成功，正在抓取精確結算週期...');
    
    // 同時訂閱：1. 全市場標記價格 (拿費率)  2. 全市場景合約資訊 (拿精確週期)
    const sub = {
        "method": "SUBSCRIBE",
        "params": [
            "!markPrice@arr",   // 全市場標記價格
            "!contractInfo"     // 全市場景合約資訊 (含 fg 欄位)
        ],
        "id": 1
    };
    ws.send(JSON.stringify(sub));
});

ws.on('message', (rawData) => {
    const msg = JSON.parse(rawData);

    // 1. 處理合約資訊 (更新該幣種的官方結算週期)
    if (msg.e === 'contractInfo') {
        const symbol = msg.s;
        if (!marketData[symbol]) marketData[symbol] = {};
        
        // fg 就是官方定義的資金費率週期 (Funding Interval)
        marketData[symbol].interval = msg.fg; 
    }

    // 2. 處理標記價格 (更新價格與費率)
    if (Array.isArray(msg)) { // !markPrice@arr 回傳的是陣列
        msg.forEach(item => {
            const symbol = item.s;
            if (!marketData[symbol]) marketData[symbol] = {};
            
            marketData[symbol].price = parseFloat(item.p).toFixed(2);
            marketData[symbol].rate = (parseFloat(item.r) * 100).toFixed(4) + '%';
        });
        
        // 渲染畫面
        render();
    }
});

function render() {
    console.clear();
    console.log(`| 幣種        | 價格      | 資金費率   | 官方週期 (H) |`);
    console.log(`|-----------|-----------|-----------|------------|`);
    
    // 只列出我們感興趣或有數據的幣 (例如前 10 個)
    Object.keys(marketData).slice(0, 15).forEach(s => {
        const info = marketData[s];
        if (info.price && info.interval) {
            console.log(`| ${s.padEnd(9)} | ${info.price.padEnd(9)} | ${info.rate.padEnd(9)} | ${info.interval}H        |`);
        }
    });
}