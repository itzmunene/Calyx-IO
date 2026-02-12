import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Navbar } from "@/components/Navbar";
import { ImageUpload } from "@/components/ImageUpload";
import { identifyFlower } from "@/lib/api";
import { AlertCircle, RefreshCw } from "lucide-react";

export default function Identify() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleImageSelect = async (file: File) => {
    setIsLoading(true);
    setError(null);

    try {
      const identification = await identifyFlower(file);
      const uploadedImage = URL.createObjectURL(file);
      navigate("/result", {
        state: {
          result: {
            species_id: (identification as any).id || undefined,
            scientific_name: identification.scientific_name,
            common_names: identification.common_names,
            primary_image_url: identification.primary_image_url,
            confidence: identification.confidence,
            native_region: (identification as any).native_region,
            traits: (identification as any).traits,
            bloom_season: (identification as any).bloom_season,
          },
          uploadedImage,
        },
      });
    } catch (err) {
      setError(
        "Unable to identify the flower. The API may be waking up (this can take up to 30 seconds on first load). Please try again."
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetry = () => {
    setError(null);
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <main className="pt-24 pb-16">
        <div className="container mx-auto px-4">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-serif font-bold text-foreground mb-4">
              Identify Your Flower
            </h1>
            <p className="text-muted-foreground max-w-lg mx-auto">
              Upload a photo of any flower and our AI will identify it instantly.
            </p>
          </div>

          {/* Content */}
          <div className="max-w-2xl mx-auto">
            {!error && (
              <ImageUpload
                onImageSelect={handleImageSelect}
                isLoading={isLoading}
              />
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
          </div>

          {/* Tips */}
          {!error && !isLoading && (
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