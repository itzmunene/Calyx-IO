import { useState } from "react";
import { Navbar } from "@/components/Navbar";
import { ImageUpload } from "@/components/ImageUpload";
import { identifyFlower, type IdentificationResult } from "@/lib/api";
import { AlertCircle, RefreshCw } from "lucide-react";

export default function Identify() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<IdentificationResult | null>(null);

  const handleImageSelect = async (file: File) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await identifyFlower(file);
      setResult(result);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to identify the flower.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetry = () => {
    setError(null);
    setResult(null);
  };

  const isShortlist =
    result?.method === "trait_shortlist" || result?.method === "vector_shortlist";

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <main className="pt-24 pb-16">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-serif font-bold text-foreground mb-4">
              Identify Your Flower
            </h1>
            <p className="text-muted-foreground max-w-lg mx-auto">
              Upload a photo of any flower and our AI will identify it instantly.
            </p>
          </div>

          <div className="max-w-5xl mx-auto">
            {!error && !result && (
              <ImageUpload onImageSelect={handleImageSelect} isLoading={isLoading} />
            )}

            {error && (
              <div className="bg-destructive/10 border border-destructive/20 rounded-2xl p-6 text-center">
                <AlertCircle className="w-12 h-12 text-destructive mx-auto mb-4" />
                <p className="text-foreground mb-4">{error}</p>
                <button
                  onClick={handleRetry}
                  className="btn-botanical inline-flex items-center gap-2"
                >
                  <RefreshCw className="w-4 h-4" />
                  Try Again
                </button>
              </div>
            )}

            {result && (
              <div className="space-y-6">
                {isShortlist && (
                  <div className="bg-amber-50 border border-amber-200 rounded-2xl p-5 text-center">
                    <p className="text-foreground font-medium">
                      Sorry, we could not find an exact match.
                    </p>
                    <p className="text-muted-foreground mt-1">
                      Here are the closest likely flowers based on the visible traits.
                    </p>
                  </div>
                )}

                <div className="bg-card border border-border rounded-2xl p-6 shadow-soft">
                  <div className="grid md:grid-cols-[160px_1fr] gap-6 items-start">
                    <div className="aspect-square rounded-xl overflow-hidden bg-muted">
                      {result.primary_image_url ? (
                        <img
                          src={result.primary_image_url}
                          alt={result.common_names?.[0] || result.scientific_name}
                          className="w-full h-full object-cover"
                        />
                      ) : null}
                    </div>

                    <div>
                      <h2 className="text-2xl font-serif font-semibold text-foreground mb-2">
                        {result.common_names?.[0] || result.scientific_name}
                      </h2>
                      <p className="text-muted-foreground italic mb-4">
                        {result.scientific_name}
                      </p>

                      <div className="space-y-2 text-sm">
                        <p className="text-foreground">
                          Confidence: {(result.confidence * 100).toFixed(1)}%
                        </p>
                        {result.method && (
                          <p className="text-muted-foreground">
                            Match mode: {result.method}
                          </p>
                        )}
                        {result.response_time_ms && (
                          <p className="text-muted-foreground">
                            Response time: {result.response_time_ms} ms
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                {result.traits_extracted && (
                  <div className="bg-card border border-border rounded-2xl p-6 shadow-soft">
                    <h3 className="text-xl font-serif font-semibold text-foreground mb-4">
                      Extracted Traits
                    </h3>

                    <div className="grid md:grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="font-medium text-foreground mb-2">Pose</p>
                        <pre className="text-muted-foreground whitespace-pre-wrap break-words">
                          {JSON.stringify(result.traits_extracted.pose_traits ?? {}, null, 2)}
                        </pre>
                      </div>

                      <div>
                        <p className="font-medium text-foreground mb-2">Colour</p>
                        <pre className="text-muted-foreground whitespace-pre-wrap break-words">
                          {JSON.stringify(result.traits_extracted.color_traits ?? {}, null, 2)}
                        </pre>
                      </div>

                      <div>
                        <p className="font-medium text-foreground mb-2">Shape</p>
                        <pre className="text-muted-foreground whitespace-pre-wrap break-words">
                          {JSON.stringify(result.traits_extracted.shape_traits ?? {}, null, 2)}
                        </pre>
                      </div>

                      <div>
                        <p className="font-medium text-foreground mb-2">Reproductive</p>
                        <pre className="text-muted-foreground whitespace-pre-wrap break-words">
                          {JSON.stringify(result.traits_extracted.reproductive_traits ?? {}, null, 2)}
                        </pre>
                      </div>
                    </div>
                  </div>
                )}

                {result.alternatives && result.alternatives.length > 0 && (
                  <div className="bg-card border border-border rounded-2xl p-6 shadow-soft">
                    <h3 className="text-xl font-serif font-semibold text-foreground mb-4">
                      {isShortlist ? "Likely Matches" : "Alternatives"}
                    </h3>

                    <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                      {result.alternatives.slice(0, 20).map((alt, index) => (
                        <div
                          key={`${alt.scientific_name}-${index}`}
                          className="border border-border rounded-xl p-4 bg-background"
                        >
                          <div className="aspect-square rounded-lg overflow-hidden bg-muted mb-3">
                            {alt.primary_image_url ? (
                              <img
                                src={alt.primary_image_url}
                                alt={alt.common_names?.[0] || alt.scientific_name}
                                className="w-full h-full object-cover"
                              />
                            ) : null}
                          </div>

                          <h4 className="font-medium text-foreground">
                            {alt.common_names?.[0] || alt.scientific_name}
                          </h4>
                          <p className="text-sm italic text-muted-foreground">
                            {alt.scientific_name}
                          </p>

                          <div className="mt-2 text-xs text-muted-foreground space-y-1">
                            <p>Confidence: {(alt.confidence * 100).toFixed(1)}%</p>
                            {typeof alt.trait_score === "number" && (
                              <p>Trait score: {alt.trait_score.toFixed(3)}</p>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="text-center">
                  <button
                    onClick={handleRetry}
                    className="btn-botanical-outline inline-flex items-center gap-2"
                  >
                    <RefreshCw className="w-4 h-4" />
                    Identify Another
                  </button>
                </div>
              </div>
            )}
          </div>

          {!error && !isLoading && !result && (
            <div className="max-w-2xl mx-auto mt-12">
              <h3 className="font-serif text-lg font-medium text-foreground mb-4 text-center">
                Tips for Best Results
              </h3>
              <div className="grid sm:grid-cols-3 gap-4">
                {[
                  "Use good lighting - natural daylight works best",
                  "Focus on the flower - get a clear, close-up shot",
                  "Show the whole bloom - include petals and center",
                ].map((tip, index) => (
                  <div
                    key={index}
                    className="bg-card p-4 rounded-xl text-center text-sm text-muted-foreground shadow-soft"
                  >
                    {tip}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}