import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "jsr:@supabase/supabase-js@2";

const VOYAGE_API_URL = "https://api.voyageai.com/v1/embeddings";
const EMBEDDING_MODEL = "voyage-3";

interface CheckRequest {
  feature: string;
  version?: string;
  limit?: number;
}

async function generateEmbedding(text: string): Promise<number[]> {
  const apiKey = Deno.env.get("VOYAGE_API_KEY");
  if (!apiKey) throw new Error("VOYAGE_API_KEY not configured");

  const response = await fetch(VOYAGE_API_URL, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: EMBEDDING_MODEL,
      input: [text.substring(0, 8000)],
      input_type: "query",
    }),
  });

  if (!response.ok) {
    const err = await response.text();
    throw new Error(`Voyage API error ${response.status}: ${err}`);
  }

  const data = await response.json();
  return data.data[0].embedding;
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response(null, {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
      },
    });
  }

  try {
    const body: CheckRequest = await req.json();
    const { feature, version, limit = 5 } = body;

    if (!feature || feature.trim().length < 2) {
      return new Response(
        JSON.stringify({ error: "feature is required (min 2 chars)" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    const queryEmbedding = await generateEmbedding(feature);

    const supabaseUrl = Deno.env.get("SUPABASE_URL") ?? "";
    const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";
    const supabase = createClient(supabaseUrl, supabaseKey);

    const { data, error } = await supabase.rpc("check_native_or_oca", {
      feature_query: feature,
      query_embedding: JSON.stringify(queryEmbedding),
      filter_version: version || null,
      match_limit: Math.min(limit, 10),
    });

    if (error) {
      return new Response(
        JSON.stringify({ error: `Check failed: ${error.message}` }),
        { status: 500, headers: { "Content-Type": "application/json" } }
      );
    }

    const results = (data || []).map((row: any) => ({
      path: row.path,
      title: row.title,
      source: row.source,
      oca_repo: row.oca_repo,
      oca_module: row.oca_module,
      category: row.category,
      summary: row.summary,
      version: row.version,
      preview: row.preview?.substring(0, 500) || "",
      similarity: Math.round(row.similarity * 1000) / 1000,
    }));

    const nativeResults = results.filter((r: any) => r.source === "native");
    const ocaResults = results.filter((r: any) => r.source === "oca");

    let availability = "unknown";
    if (nativeResults.length > 0 && ocaResults.length > 0) {
      availability = "both";
    } else if (nativeResults.length > 0) {
      availability = "native_only";
    } else if (ocaResults.length > 0) {
      availability = "oca_only";
    } else {
      availability = "not_found";
    }

    return new Response(
      JSON.stringify({
        feature,
        version: version || "all",
        availability,
        native_results: nativeResults,
        oca_results: ocaResults,
      }),
      {
        headers: {
          "Content-Type": "application/json",
          "Connection": "keep-alive",
        },
      }
    );
  } catch (err) {
    return new Response(
      JSON.stringify({ error: err.message }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
});
