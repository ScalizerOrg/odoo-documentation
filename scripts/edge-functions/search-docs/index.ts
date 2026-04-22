import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "jsr:@supabase/supabase-js@2";

const VOYAGE_API_URL = "https://api.voyageai.com/v1/embeddings";
const EMBEDDING_MODEL = "voyage-3";

interface SearchRequest {
  query: string;
  section?: string;
  module?: string;
  version?: string;
  source?: string;
  limit?: number;
}

async function generateEmbedding(text: string, inputType: "query" | "document"): Promise<number[]> {
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
      input_type: inputType,
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
    const body: SearchRequest = await req.json();
    const { query, section, module, version, source, limit = 10 } = body;

    if (!query || query.trim().length < 2) {
      return new Response(
        JSON.stringify({ error: "query is required (min 2 chars)" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    // Generate embedding for the search query
    const queryEmbedding = await generateEmbedding(query, "query");

    // Call hybrid search RPC v3
    const supabaseUrl = Deno.env.get("SUPABASE_URL") ?? "";
    const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";
    const supabase = createClient(supabaseUrl, supabaseKey);

    const { data, error } = await supabase.rpc("search_docs", {
      query_text: query,
      query_embedding: JSON.stringify(queryEmbedding),
      filter_section: section || null,
      filter_module: module || null,
      filter_version: version || null,
      filter_source: source || null,
      match_limit: Math.min(limit, 20),
    });

    if (error) {
      return new Response(
        JSON.stringify({ error: `Search failed: ${error.message}` }),
        { status: 500, headers: { "Content-Type": "application/json" } }
      );
    }

    const results = (data || []).map((row: any) => ({
      title: row.title,
      breadcrumb: row.breadcrumb,
      path: row.path,
      section: row.section,
      module: row.module,
      keywords: row.keywords,
      preview: row.preview?.substring(0, 500) || "",
      version: row.version,
      source: row.source,
      oca_repo: row.oca_repo,
      category: row.category,
      score: Math.round(row.combined_score * 1000) / 1000,
      similarity: Math.round(row.similarity * 1000) / 1000,
    }));

    return new Response(
      JSON.stringify({
        query,
        filters: { version: version || "all", source: source || "all" },
        results_count: results.length,
        results,
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
