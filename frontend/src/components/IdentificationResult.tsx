import { Link } from "react-router-dom";
import { ChevronRight, Leaf } from "lucide-react";
import { ConfidenceBadge } from "./ConfidenceBadge";
import { IdentificationResult as IdentificationResultType } from "@/lib/api";

interface IdentificationResultProps {
  result: IdentificationResultType;
}

export function IdentificationResult({ result }: IdentificationResultProps) {
  const showAlternatives = result.confidence < 0.7 && result.alternatives && result.alternatives.length > 0;

  return (
    <div className="space-y-6 animate-slide-up">
      {/* Main Result */}
      <div className="polaroid-card max-w-md mx-auto">
        <div className="aspect-square overflow-hidden rounded-sm mb-4">
          <img
            src={result.primary_image_url}
            alt={result.scientific_name}
            className="w-full h-full object-cover"
          />
        </div>
        <div className="text-center space-y-3">
          <ConfidenceBadge confidence={result.confidence} />
          <h2 className="font-serif text-2xl font-semibold text-foreground">
            {result.common_names[0] || result.scientific_name}
          </h2>
          <p className="text-muted-foreground italic">
            {result.scientific_name}
          </p>
          {result.common_names.length > 1 && (
            <p className="text-sm text-muted-foreground">
              Also known as: {result.common_names.slice(1).join(", ")}
            </p>
          )}
          <Link
            to={`/species/${encodeURIComponent(result.scientific_name)}`}
            className="inline-flex items-center gap-2 btn-botanical mt-4"
          >
            <Leaf className="w-4 h-4" />
            View Details
            <ChevronRight className="w-4 h-4" />
          </Link>
        </div>
      </div>

      {/* Alternative Suggestions */}
      {showAlternatives && (
        <div className="mt-8">
          <h3 className="font-serif text-xl font-medium text-center mb-4 text-foreground">
            Other Possibilities
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {result.alternatives!.map((alt, index) => (
              <Link
                key={index}
                to={`/species/${encodeURIComponent(alt.scientific_name)}`}
                className="polaroid-card group"
              >
                <div className="aspect-square overflow-hidden rounded-sm mb-2">
                  <img
                    src={alt.primary_image_url}
                    alt={alt.scientific_name}
                    className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                  />
                </div>
                <div className="text-center">
                  <ConfidenceBadge confidence={alt.confidence} className="text-xs" />
                  <p className="font-serif text-sm font-medium text-foreground mt-2 truncate">
                    {alt.common_names[0] || alt.scientific_name}
                  </p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}