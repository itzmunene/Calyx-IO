import { Link } from "react-router-dom";
import { ChevronRight, Leaf } from "lucide-react";
import { ConfidenceBadge } from "./ConfidenceBadge";
import { IdentificationResult as IdentificationResultType } from "@/lib/api";

interface IdentificationResultProps {
  result: IdentificationResultType;
  debugImage?: string | null;
}

export function IdentificationResult({ result, debugImage }: IdentificationResultProps) {
  const candidates = result.alternatives || [];

  return (
    <div className="space-y-10 animate-slide-up">

      {/* 🔥 DEBUG IMAGE (FULL WIDTH HERO) */}
      {debugImage && (
        <div className="w-full">
          <img
            src={debugImage}
            alt="Debug overlay"
            className="w-full h-auto object-contain rounded-xl shadow-lg"
          />
          <p className="text-xs text-center text-muted-foreground mt-2">
            Visual Analysis Overlay
          </p>
        </div>
      )}

      {/* 🔥 TOP 5 CATALOG GRID */}
      {candidates.length > 0 && (
        <div>
          <h3 className="font-serif text-xl font-medium mb-4 text-foreground">
            Top Matches
          </h3>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
            {candidates.slice(0, 5).map((alt, index) => (
              <Link
                key={index}
                to={`/species/${encodeURIComponent(alt.scientific_name)}`}
                className="bg-card rounded-xl overflow-hidden shadow hover:shadow-lg transition group"
              >
                <div className="h-32 bg-muted overflow-hidden">
                  <img
                    src={alt.primary_image_url}
                    alt={alt.scientific_name}
                    className="w-full h-full object-cover group-hover:scale-105 transition"
                  />
                </div>

                <div className="p-3 text-center">
                  <ConfidenceBadge confidence={alt.confidence} className="text-xs" />
                  <p className="font-serif text-sm font-medium mt-1 truncate">
                    {alt.common_names?.[0] || alt.scientific_name}
                  </p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* 🔥 MAIN RESULT (SECONDARY NOW) */}
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

          <h2 className="font-serif text-2xl font-semibold">
            {result.common_names?.[0] || result.scientific_name}
          </h2>

          <p className="italic text-muted-foreground">
            {result.scientific_name}
          </p>

          {result.common_names?.length > 1 && (
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

      {/* 🔥 REMAINING ALTERNATIVES */}
      {candidates.length > 5 && (
        <div>
          <h3 className="font-serif text-lg text-center mb-4">
            More Matches
          </h3>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {candidates.slice(5).map((alt, index) => (
              <Link
                key={index}
                to={`/species/${encodeURIComponent(alt.scientific_name)}`}
                className="polaroid-card group"
              >
                <div className="aspect-square overflow-hidden rounded-sm mb-2">
                  <img
                    src={alt.primary_image_url}
                    className="w-full h-full object-cover group-hover:scale-110 transition"
                  />
                </div>

                <div className="text-center">
                  <ConfidenceBadge confidence={alt.confidence} className="text-xs" />
                  <p className="text-sm font-medium mt-1 truncate">
                    {alt.common_names?.[0] || alt.scientific_name}
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