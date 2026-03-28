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
  result?: FlowerResultData; // For single result mode
  method?: string; // "single" or "list"
  uploadedImage?: string; // For displaying the user's uploaded image
  traits?: any; // For displaying extracted traits in debug mode
  bloom_season?: string[];
}

interface LocationState {
  result?: FlowerResultData;
  candidates?: any[]; // For list mode
  uploadedImage?: string;
  traits?: any;
  method?: string;
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

function GlassCard({
  title,
  items,
  icon,
}: {
  title: string;
  items: string[];
  icon: string;
}) {
  if (!items || items.length === 0) return null;

  return (
    <div className="backdrop-blur-xl bg-white/10 border border-white/20 rounded-2xl p-5 shadow-lg">
      <h3 className="text-sm uppercase tracking-wide text-muted-foreground mb-3 flex items-center gap-2">
        <span>{icon}</span> {title}
      </h3>

      <ul className="space-y-2 text-sm text-foreground">
        {items.map((item, i) => (
          <li key={i} className="leading-relaxed">
            • {item}
          </li>
        ))}
      </ul>
    </div>
  );
}



function formatTraits(traits: any) {
  if (!traits) return null;

  const color = traits.color_traits || {};
  const shape = traits.shape_traits || {};
  const repro = traits.reproductive_traits || {};

  return {
    colorSummary: [
      color.petal_color_primary && `Primary colour: ${color.petal_color_primary}`,
      color.petal_color_secondary && `Secondary tones: ${color.petal_color_secondary}`,
    ].filter(Boolean),

    shapeSummary: [
      shape.petal_count && `${shape.petal_count} petals detected`,
      shape.flower_size && `Flower size appears ${shape.flower_size}`,
      shape.petal_shape && `Petal shape: ${shape.petal_shape}`,
      shape.petal_margin && `Petal edges: ${shape.petal_margin}`,
    ].filter(Boolean),

    reproductiveSummary: [
      repro.centre_morphology && `Centre type: ${repro.centre_morphology}`,
      repro.stamen_visible && `Stamens clearly visible`,
      repro.anther_visible && `Anthers detected`,
      repro.stigma_visible && `Stigma visible`,
    ].filter(Boolean),
  };
}

export default function FlowerResult() {
  const location = useLocation();
  const state = location.state as LocationState;
  const navigate = useNavigate();
  const candidates = state?.candidates || [];
  const traits = state?.traits;
  const method = state?.method;
  const result = state?.result;
  const uploadedImage = state?.uploadedImage;

  const isSingle = !!result;
  const isList = candidates?.length > 0;

  if (!result && candidates.length === 0) {
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
                {traits && (() => {
                  const formatted = formatTraits(traits);

                  return (
                    <div className="max-w-5xl mx-auto mt-10 grid md:grid-cols-3 gap-4">
                      <GlassCard
                        title="Petal Colour"
                        icon="🎨"
                        items={formatted?.colorSummary || []}
                      />

                      <GlassCard
                        title="Flower Structure"
                        icon="🌸"
                        items={formatted?.shapeSummary || []}
                      />

                      <GlassCard
                        title="Reproductive Features"
                        icon="🧬"
                        items={formatted?.reproductiveSummary || []}
                      />
                    </div>
                  );
                })()}

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

              {/* Shortlist results */}
              {isList && (
                <div className="max-w-6xl mx-auto mt-10">
                  <h2 className="text-xl font-semibold mb-4">
                    Possible Matches
                  </h2>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {candidates.slice(0, 20).map((c: any) => (
                      <div key={c.id} className="bg-card p-3 rounded-xl shadow-card">
                        <img
                          src={c.primary_image_url}
                          className="w-full h-32 object-cover rounded-md"
                        />
                        <p className="text-sm mt-2 font-medium">
                          {c.common_names?.[0] || c.scientific_name}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {Math.round((c.confidence || 0) * 100)}%
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )} 
              
                {process.env.NODE_ENV === "development" && traits && (
                  <div className="max-w-4xl mx-auto mt-10 glass-card p-6">
                    <h3 className="text-lg font-semibold mb-4">
                      Debug Traits
                    </h3>

                    <pre className="text-xs text-muted-foreground overflow-x-auto">
                      {JSON.stringify(traits, null, 2)}
                    </pre>
                  </div>
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

