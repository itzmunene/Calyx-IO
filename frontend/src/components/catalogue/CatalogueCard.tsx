import { Link } from "react-router-dom";
import { cn } from "@/lib/utils";
import { useMemo } from "react";
import type { CatalogueItem } from "@/lib/api";
import { TrendingUp } from "lucide-react";

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

  // derive colours safely
  const colors = useMemo(() => {
    if (Array.isArray(item.colors) && item.colors.length > 0) return item.colors;

    const traitColors = item.traits?.color_primary;
    if (Array.isArray(traitColors) && traitColors.length > 0) return traitColors;

    return [];
  }, [item.colors, item.traits]);

  // safe image fallback (prevents broken <img> from killing layout)
  const imgSrc = item.primary_image_url || "/placeholder-flower.jpg";

  return (
    <Link to={`/species/${item.id}`} className={cn("block group", className)}>
      <div
        className="bg-card rounded-sm shadow-card transition-all duration-300 group-hover:shadow-elevated group-hover:-translate-y-2"
        style={{
          padding: "16px 16px 40px 16px",
          transform: `rotate(${rotation}deg)`,
        }}
      >
        <div className="aspect-square overflow-hidden rounded-sm mb-4">
          <img
            src={imgSrc}
            alt={item.common_names?.[0] || item.scientific_name}
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
            loading="lazy"
          />
        </div>

        <div className="text-center space-y-1.5">
          <h3 className="font-serif text-lg font-semibold text-foreground truncate">
            {item.common_names?.[0] || item.scientific_name}
          </h3>

          <p className="text-sm text-muted-foreground italic truncate">
            {item.scientific_name}
          </p>

          {/* ✅ render derived colours, not only item.colors */}
          {colors.length > 0 && (
            <div className="flex items-center justify-center gap-1.5 pt-1">
              {colors.map((color) => (
                <span
                  key={color}
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
        </div>
      </div>
    </Link>
  );
}

export function CatalogueCardSkeleton() {
  return (
    <div className="bg-card rounded-sm shadow-card animate-pulse" style={{ padding: "16px 16px 40px 16px" }}>
      <div className="aspect-square bg-muted rounded-sm mb-4" />
      <div className="space-y-2 flex flex-col items-center">
        <div className="h-5 w-3/4 bg-muted rounded" />
        <div className="h-4 w-1/2 bg-muted rounded" />
        <div className="flex gap-1.5 pt-1">
          <div className="w-3 h-3 bg-muted rounded-full" />
          <div className="w-3 h-3 bg-muted rounded-full" />
          <div className="w-3 h-3 bg-muted rounded-full" />
        </div>
      </div>
    </div>
  );
}