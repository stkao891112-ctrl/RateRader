export const config = { runtime: 'edge' };

export default async function handler(req) {
  const { searchParams } = new URL(req.url);
  const assets = searchParams.get('assets') || 'BTC';
  
  try {
    const res = await fetch(
      `http://35.206.227.28:8080/api/funding?assets=${assets}`
    );
    
    const text = await res.text(); // 先拿文字
    console.log('GCP response:', text.slice(0, 200)); // 看實際回傳什麼
    
    const data = JSON.parse(text); // 再 parse
    
    return new Response(JSON.stringify(data), {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    });
  } catch(e) {
    return new Response(JSON.stringify({ error: e.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}