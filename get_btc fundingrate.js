const WebSocket = require('ws');

// 1. 連接到基礎 Streams 網址
const ws = new WebSocket('wss://fstream.binance.com/ws');

// 準備儲存數據的變數
let data = {
    lastPrice: "0.00",   // 最新成交價 (aggTrade)
    markPrice: "0.00",   // 標記價格 (markPrice)
    fundingRate: "0.00%" // 資金費率 (markPrice)
};

ws.on('open', () => {
    console.log('✅ 已連線，正在訂閱行情與資費...');

    // 2. 一次訂閱兩個頻道：aggTrade 和 markPrice
    const subscribeMsg = {
        "method": "SUBSCRIBE",
        "params": [
            "btcusdt@aggTrade",     // 獲取最新成交價
            "btcusdt@markPrice@1s"  // 獲取標記價格與資金費率
        ],
        "id": 1
    };
    ws.send(JSON.stringify(subscribeMsg));
});

ws.on('message', (rawData) => {
    const msg = JSON.parse(rawData);

    // 3. 根據回傳的事件類型 (e) 來更新對應的數據
    if (msg.e === 'aggTrade') {
        data.lastPrice = parseFloat(msg.p).toFixed(2);
    } else if (msg.e === 'markPriceUpdate') {
        data.markPrice = parseFloat(msg.p).toFixed(2);
        data.fundingRate = (parseFloat(msg.r) * 100).toFixed(5) + '%';
    }

    // 4. 畫面呈現 (使用 console.clear 讓它像個儀表板)
    console.clear();
    console.log(`======== BTCUSDT 即時儀表板 ========`);
    console.log(`🔥 最新成交價: $${data.lastPrice}`);
    console.log(`🏷️ 標記價格　: $${data.markPrice}`);
    console.log(`💰 資金費率　: ${data.fundingRate}`);
    console.log(`====================================`);
    console.log(`(按 Ctrl + C 停止監控)`);
});

ws.on('error', (err) => console.error('連線錯誤:', err));