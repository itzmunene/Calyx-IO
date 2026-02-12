import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { Navbar } from "@/components/Navbar";
import { getSpeciesDetail, SpeciesDetail as SpeciesDetailType } from "@/lib/api";
import { ArrowLeft, Loader2, Calendar, Droplets, Sun, AlertCircle } from "lucide-react";

export default function SpeciesDetail() {
  const { id } = useParams<{ id: string }>();
  const [species, setSpecies] = useState<SpeciesDetailType | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      fetchSpecies(id);
    }
  }, [id]);

  const fetchSpecies = async (speciesId: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await getSpeciesDetail(speciesId);
      setSpecies(data);
    } catch (err) {
      setError("Unable to load species details. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="pt-24 flex items-center justify-center min-h-[60vh]">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="w-10 h-10 text-primary animate-spin" />
            <p className="text-muted-foreground">Loading species details...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !species) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="pt-24 container mx-auto px-4">
          <div className="max-w-lg mx-auto text-center py-20">
            <AlertCircle className="w-16 h-16 text-destructive mx-auto mb-4" />
            <h2 className="font-serif text-2xl font-bold text-foreground mb-4">
              Species Not Found
            </h2>
            <p className="text-muted-foreground mb-6">
              {error || "We couldn't find the species you're looking for."}
            </p>
            <Link to="/search" className="btn-botanical">
              Browse Flowers
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <main className="pt-24 pb-16">
        <div className="container mx-auto px-4">
          {/* Back Button */}
          <Link
            to="/search"
            className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors mb-8"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Search
          </Link>

          <div className="grid lg:grid-cols-2 gap-12 max-w-6xl mx-auto">
            {/* Image */}
            <div className="polaroid-card self-start">
              <div className="aspect-square overflow-hidden rounded-sm">
                <img
                  src={species.primary_image_url}
                  alt={species.scientific_name}
                  className="w-full h-full object-cover"
                />
              </div>
            </div>

            {/* Details */}
            <div className="space-y-8">
              {/* Header */}
              <div>
                <h1 className="text-4xl md:text-5xl font-serif font-bold text-foreground mb-2">
                  {species.common_names[0] || species.scientific_name}
                </h1>
                <p className="text-xl text-muted-foreground italic">
                  {species.scientific_name}
                </p>
                {species.common_names.length > 1 && (
                  <p className="text-sm text-muted-foreground mt-2">
                    Also known as: {species.common_names.slice(1).join(", ")}
                  </p>
                )}
              </div>

              {/* Description */}
              {species.description && (
                <div>
                  <h2 className="font-serif text-xl font-semibold text-foreground mb-3">
                    About
                  </h2>
                  <p className="text-muted-foreground leading-relaxed">
                    {species.description}
                  </p>
                </div>
              )}

              {/* Bloom Season */}
              {species.bloom_season && species.bloom_season.length > 0 && (
                <div className="bg-card rounded-2xl p-6 shadow-soft">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-10 h-10 rounded-full bg-pink/20 flex items-center justify-center">
                      <Calendar className="w-5 h-5 text-pink-dark" />
                    </div>
                    <h3 className="font-serif text-lg font-semibold text-foreground">
                      Bloom Season
                    </h3>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {species.bloom_season.map((season) => (
                      <span
                        key={season}
                        className="px-3 py-1 bg-pink/10 text-pink-dark rounded-full text-sm"
                      >
                        {season}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Care Tips */}
              {species.care_tips && (
                <div className="bg-card rounded-2xl p-6 shadow-soft">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                      <Droplets className="w-5 h-5 text-primary" />
                    </div>
                    <h3 className="font-serif text-lg font-semibold text-foreground">
                      Care Tips
                    </h3>
                  </div>
                  <p className="text-muted-foreground leading-relaxed whitespace-pre-line">
                    {species.care_tips}
                  </p>
                </div>
              )}

              {/* Quick Tips */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-muted rounded-xl p-4 text-center">
                  <Sun className="w-6 h-6 text-primary mx-auto mb-2" />
                  <p className="text-sm text-muted-foreground">
                    Check care tips for sunlight needs
                  </p>
                </div>
                <div className="bg-muted rounded-xl p-4 text-center">
                  <Droplets className="w-6 h-6 text-primary mx-auto mb-2" />
                  <p className="text-sm text-muted-foreground">
                    Refer to care tips for watering
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}