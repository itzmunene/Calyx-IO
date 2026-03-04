import { Link } from "react-router-dom";
import { cn } from "@/lib/utils";
import { useMemo, useState } from "react";
import type { CatalogueItem } from "@/lib/api";
import { TrendingUp } from "lucide-react";
import FloatingGrowingInfo from "@/components/FloatingGrowingInfo";

const COLOR_MAP: Record<string, string> = {
  red: "bg-red-500",
  pink: "bg-pink-400",
  white: "bg-white border border-border",
  yellow: "bg-yellow-400",
  orange: "bg-orange-500",
  purple: "bg-purple-500",
  blue: "bg-blue-500",
  green: "bg-green-500",
};

interface CatalogueCardProps {
  item: CatalogueItem;
  className?: string;
}

export function CatalogueCard({ item, className }: CatalogueCardProps) {
  const rotation = useMemo(() => Math.random() * 4 - 2, []);
  const [showGrowingInfo, setShowGrowingInfo] = useState(false);

  const colors = useMemo(() => {
    if (Array.isArray(item.colors) && item.colors.length > 0) return item.colors;

    const traitColors = (item as any).traits?.color_primary;
    if (Array.isArray(traitColors) && traitColors.length > 0) return traitColors;

    return [];
  }, [item]);

  const imgSrc = item.primary_image_url || "/placeholder-flower.jpg";
  const displayName = item.common_names?.[0] || item.scientific_name;

  return (
    <>
      <Link to={`/species/${item.id}`} className={cn("block group", className)}>
        <div
          className="bg-card rounded-sm shadow-card transition-all duration-300 group-hover:shadow-elevated group-hover:-translate-y-2"
          style={{
            padding: "16px 16px 40px 16px",
            transform: `rotate(${rotation}deg)`,
          }}
        >
          {/* Image */}
          <div className="aspect-square overflow-hidden rounded-sm mb-4 bg-muted/30">
            <img
              src={imgSrc}
              alt={displayName}
              className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
              loading="lazy"
            />
          </div>

          {/* Info */}
          <div className="text-center space-y-1.5">
            <h3 className="font-serif text-lg font-semibold text-foreground truncate">
              {displayName}
            </h3>

            <p className="text-sm text-muted-foreground italic truncate">
              {item.scientific_name}
            </p>

            {colors.length > 0 && (
              <div className="flex items-center justify-center gap-1.5 pt-1">
                {colors.map((color) => (
                  <span
                    key={String(color)}
                    className={cn(
                      "w-3 h-3 rounded-full",
                      COLOR_MAP[String(color).toLowerCase()] || "bg-muted"
                    )}
                    title={String(color)}
                  />
                ))}
              </div>
            )}

            {typeof item.search_count === "number" && item.search_count > 0 && (
              <div className="flex items-center justify-center gap-1 text-xs text-muted-foreground pt-1">
                <TrendingUp className="w-3 h-3" />
                <span>{item.search_count.toLocaleString()} searches</span>
              </div>
            )}

            {/* Growing Info button */}
            <div className="pt-3">
              <button
                type="button"
                onClick={(e) => {
                  e.preventDefault(); // stop Link navigation
                  e.stopPropagation();
                  setShowGrowingInfo(true);
                }}
                className="mx-auto inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm
                           bg-primary text-primary-foreground hover:opacity-90 transition"
              >
                <span>🌱</span>
                Growing Info
              </button>
            </div>
          </div>
        </div>
      </Link>

      <FloatingGrowingInfo
        isOpen={showGrowingInfo}
        onClose={() => setShowGrowingInfo(false)}
        growingInfo={(item as any).growing_info || {}}
        flowerName={displayName}
      />
    </>
  );
}

export function CatalogueCardSkeleton({ className }: { className?: string }) {
  const rotation = useMemo(() => Math.random() * 4 - 2, []);

  return (
    <div
      className={cn(
        "bg-card rounded-sm shadow-card overflow-hidden",
        "motion-safe:animate-pulse",
        className
      )}
      style={{
        padding: "16px 16px 40px 16px",
        transform: `rotate(${rotation}deg)`,
      }}
    >
      {/* Image placeholder */}
      <div className="aspect-square rounded-sm mb-4 bg-muted/40" />

      {/* Text placeholders */}
      <div className="text-center space-y-2">
        <div className="h-5 w-3/4 mx-auto rounded bg-muted/40" />
        <div className="h-4 w-1/2 mx-auto rounded bg-muted/30" />

        {/* Colour dots placeholders */}
        <div className="flex items-center justify-center gap-1.5 pt-1">
          <div className="w-3 h-3 rounded-full bg-muted/35" />
          <div className="w-3 h-3 rounded-full bg-muted/35" />
          <div className="w-3 h-3 rounded-full bg-muted/35" />
        </div>

        {/* Button placeholder */}
        <div className="pt-3">
          <div className="h-9 w-32 mx-auto rounded-lg bg-muted/35" />
        </div>
      </div>
    </div>
  );
}