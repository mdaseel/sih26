const headers = { "Content-Type": "application/json" };

export function GET() {
  return Response.json({ status: "ok" });
}

export function HEAD() {
  return new Response(null, { headers });
}
