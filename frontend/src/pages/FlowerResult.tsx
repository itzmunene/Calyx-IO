import { useLocation, useNavigate } from "react-router-dom";
import { Navbar } from "@/components/Navbar";
import { RefreshCw } from "lucide-react";

export default function FlowerResult() {
  const { state } = useLocation();
  const navigate = useNavigate();

  const result = state?.result;
  const debugImage = result?.debug_image_url;
  const candidates = result?.alternatives || [];
  const traits = result?.traits_extracted;
  const method = result?.method;

  const isShortlist =
    method === "trait_shortlist" || method === "vector_shortlist";

  if (!result) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p>No result found.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <main className="pt-24 pb-16">
        <div className="container mx-auto px-4 max-w-6xl space-y-10">

          {/* 🔥 DEBUG IMAGE (FULL WIDTH HERO) */}
          {debugImage && (
            <div className="w-full">
              <img
                src={debugImage}
                className="w-full h-auto object-contain rounded-2xl shadow-lg"
                onError={(e) => {
                  (e.target as HTMLImageElement).style.display = "none";
                }}
              />
              <p className="text-xs text-center text-muted-foreground mt-2">
                Visual Analysis Overlay
              </p>
            </div>
          )}

          {/* 🔥 TOP 5 RESULTS (CATALOG GRID) */}
          {candidates.length > 0 && (
            <div>
              <h2 className="text-2xl font-semibold mb-4">
                {isShortlist ? "Likely Matches" : "Top Matches"}
              </h2>

              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
                {candidates.slice(0, 5).map((c: any, index: number) => (
                  <div
                    key={`${c.scientific_name}-${index}`}
                    className="bg-card rounded-xl overflow-hidden shadow hover:shadow-lg transition"
                  >
                    <div className="h-32 bg-muted">
                      {c.primary_image_url && (
                        <img
                          src={c.primary_image_url}
                          className="w-full h-full object-cover"
                        />
                      )}
                    </div>

                    <div className="p-3">
                      <p className="text-sm font-medium">
                        {c.common_names?.[0] || c.scientific_name}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {Math.round((c.confidence || 0) * 100)}%
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 🔥 MAIN IDENTIFICATION CARD */}
          <div className="bg-card border border-border rounded-2xl p-6 shadow-soft">
            <div className="grid md:grid-cols-[160px_1fr] gap-6 items-start">

              <div className="aspect-square rounded-xl overflow-hidden bg-muted">
                {result.primary_image_url && (
                  <img
                    src={result.primary_image_url}
                    className="w-full h-full object-cover"
                  />
                )}
              </div>

              <div>
                <h2 className="text-2xl font-serif font-semibold mb-2">
                  {result.common_names?.[0] || result.scientific_name}
                </h2>

                <p className="italic text-muted-foreground mb-4">
                  {result.scientific_name}
                </p>

                <div className="space-y-1 text-sm">
                  <p>Confidence: {(result.confidence * 100).toFixed(1)}%</p>
                  {method && <p>Match mode: {method}</p>}
                  {result.response_time_ms && (
                    <p>Response time: {result.response_time_ms} ms</p>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* 🔥 TRAITS */}
          {traits && (
            <div className="bg-card border border-border rounded-2xl p-6 shadow-soft">
              <h3 className="text-xl font-semibold mb-4">
                Extracted Traits
              </h3>

              <div className="grid md:grid-cols-2 gap-4 text-sm">
                {Object.entries(traits).map(([key, value]) => (
                  <div key={key}>
                    <p className="font-medium mb-1 capitalize">
                      {key.replace("_traits", "")}
                    </p>
                    <pre className="text-muted-foreground whitespace-pre-wrap break-words">
                      {JSON.stringify(value ?? {}, null, 2)}
                    </pre>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 🔥 FULL ALTERNATIVES GRID */}
          {candidates.length > 5 && (
            <div className="bg-card border border-border rounded-2xl p-6 shadow-soft">
              <h3 className="text-xl font-semibold mb-4">
                All Alternatives
              </h3>

              <div className="grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {candidates.slice(5).map((alt: any, index: number) => (
                  <div
                    key={`${alt.scientific_name}-${index}`}
                    className="border rounded-xl p-4"
                  >
                    <div className="aspect-square bg-muted rounded-lg mb-3 overflow-hidden">
                      {alt.primary_image_url && (
                        <img
                          src={alt.primary_image_url}
                          className="w-full h-full object-cover"
                        />
                      )}
                    </div>

                    <p className="font-medium text-sm">
                      {alt.common_names?.[0] || alt.scientific_name}
                    </p>

                    <p className="text-xs text-muted-foreground italic">
                      {alt.scientific_name}
                    </p>

                    <p className="text-xs mt-1">
                      {(alt.confidence * 100).toFixed(1)}%
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 🔁 RETRY */}
          <div className="text-center">
            <button
              onClick={() => navigate("/")}
              className="btn-botanical-outline inline-flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              Identify Another
            </button>
          </div>

        </div>
      </main>
    </div>
  );
}