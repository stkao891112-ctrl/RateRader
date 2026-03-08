async function directFetchOKX() {
    try {
        const res = await fetch('https://www.okx.com/api/v5/public/interest-rate?ccy=USDT');
        const json = await res.json();

        if (json.data && json.data.length > 0) {
            const rate = parseFloat(json.data[0].interestRate) * 365 * 100;
            console.log(`直接抓取成功！利率：${rate.toFixed(2)}%`);
        }
    } catch (err) {
        console.log("網路連線問題，請檢查是否有阻擋 OKX 網域");
    }
}

directFetchOKX();