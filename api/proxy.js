export const config = { runtime: 'edge' };

export default async function handler(req) {
  const { searchParams } = new URL(req.url);
  const assets = searchParams.get('assets') || 'BTC';
  
  const res = await fetch(
    `http://35.206.227.28:8080/api/funding?assets=${assets}`
  );
  
  const data = await res.json();
  
  return new Response(JSON.stringify(data), {
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*'
    }
  });
}