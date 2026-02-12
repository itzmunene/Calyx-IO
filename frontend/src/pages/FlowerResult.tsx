import { useLocation, useNavigate, Link } from "react-router-dom";
import { Navbar } from "@/components/Navbar";
import { ArrowLeft, Bookmark } from "lucide-react";

interface FlowerResultData {
  species_id?: string;
  scientific_name: string;
  common_names: string[];
  primary_image_url: string;
  confidence?: number;
  native_region?: string[];
  traits?: {
    climate?: string;
    hardiness_zone?: string;
    light_requirement?: string;
    water_needs?: string;
    soil_type?: string;
  };
  bloom_season?: string[];
}

function InfoSection({
  icon,
  title,
  children,
}: {
  icon: string;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <h3 className="font-serif text-lg font-semibold text-foreground mb-2 flex items-center gap-2">
        <span>{icon}</span> {title}
      </h3>
      <div className="text-muted-foreground space-y-1 ml-8">{children}</div>
    </div>
  );
}

export default function FlowerResult() {
  const location = useLocation();
  const navigate = useNavigate();
  const result: FlowerResultData | undefined = location.state?.result;
  const uploadedImage: string | undefined = location.state?.uploadedImage;

  if (!result) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="pt-24 flex flex-col items-center justify-center min-h-[60vh] text-center px-4">
          <p className="text-muted-foreground mb-4">No identification result found.</p>
          <button onClick={() => navigate("/identify")} className="btn-botanical">
            Go to Identify
          </button>
        </div>
      </div>
    );
  }

  const imageUrl = uploadedImage || result.primary_image_url;

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <main className="pt-24 pb-16">
        <div className="container mx-auto px-4">
          {/* Back button */}
          <button
            onClick={() => navigate(-1)}
            className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors mb-8"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Identify
          </button>

          {/* Main card */}
          <div className="max-w-6xl mx-auto bg-card rounded-2xl shadow-card overflow-hidden">
            <div className="grid md:grid-cols-2">
              {/* Left: Image */}
              <div className="bg-muted flex items-center justify-center p-8">
                <img
                  src={imageUrl}
                  alt={result.common_names[0] || result.scientific_name}
                  className="w-full max-w-md aspect-square object-cover rounded-lg shadow-card"
                />
              </div>

              {/* Right: Information */}
              <div className="p-8 md:p-10 space-y-6">
                {/* Names */}
                <div>
                  <h1 className="text-3xl md:text-4xl font-serif font-bold text-primary mb-2">
                    {result.common_names[0] || result.scientific_name}
                  </h1>
                  <p className="text-lg text-muted-foreground italic">
                    {result.scientific_name}
                  </p>
                  {result.common_names.length > 1 && (
                    <p className="text-sm text-muted-foreground mt-1">
                      Also known as: {result.common_names.slice(1).join(", ")}
                    </p>
                  )}
                </div>

                {/* Confidence */}
                {result.confidence !== undefined && (
                  <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium confidence-high">
                    {Math.round(result.confidence * 100)}% match
                  </div>
                )}

                {/* Native Region */}
                {result.native_region && result.native_region.length > 0 && (
                  <InfoSection icon="📍" title="Native Region">
                    {result.native_region.map((region, i) => (
                      <p key={i}>• {region}</p>
                    ))}
                  </InfoSection>
                )}

                {/* Where It Grows */}
                {result.traits &&
                  (result.traits.climate || result.traits.hardiness_zone) && (
                    <InfoSection icon="🌍" title="Where It Grows">
                      {result.traits.climate && (
                        <p>• Climate: {result.traits.climate}</p>
                      )}
                      {result.traits.hardiness_zone && (
                        <p>• Hardiness: Zone {result.traits.hardiness_zone}</p>
                      )}
                    </InfoSection>
                  )}

                {/* Growing Conditions */}
                {result.traits &&
                  (result.traits.light_requirement ||
                    result.traits.water_needs ||
                    result.traits.soil_type) && (
                    <InfoSection icon="🌱" title="Growing Conditions">
                      {result.traits.light_requirement && (
                        <p>• Light: {result.traits.light_requirement}</p>
                      )}
                      {result.traits.water_needs && (
                        <p>• Water: {result.traits.water_needs}</p>
                      )}
                      {result.traits.soil_type && (
                        <p>• Soil: {result.traits.soil_type}</p>
                      )}
                    </InfoSection>
                  )}

                {/* Bloom Season */}
                {result.bloom_season && result.bloom_season.length > 0 && (
                  <InfoSection icon="🌸" title="Bloom Season">
                    <p>{result.bloom_season.join(", ")}</p>
                  </InfoSection>
                )}

                {/* Action Buttons */}
                <div className="pt-4 flex flex-col sm:flex-row gap-3">
                  <button className="btn-botanical inline-flex items-center justify-center gap-2">
                    <Bookmark className="w-4 h-4" />
                    Save to Collection
                  </button>
                  {result.species_id && (
                    <Link
                      to={`/species/${result.species_id}`}
                      className="btn-botanical-outline text-center"
                    >
                      View Full Details
                    </Link>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
