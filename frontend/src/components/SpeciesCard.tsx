import { Link } from "react-router-dom";
import { cn } from "@/lib/utils";

interface SpeciesCardProps {
  id: string;
  scientificName: string;
  commonNames: string[];
  imageUrl: string;
  className?: string;
}

export function SpeciesCard({
  id,
  scientificName,
  commonNames,
  imageUrl,
  className,
}: SpeciesCardProps) {
  return (
    <Link
      to={`/species/${id}`}
      className={cn("block group", className)}
    >
      <div className="polaroid-card">
        <div className="aspect-square overflow-hidden rounded-sm mb-3">
          <img
            src={imageUrl}
            alt={scientificName}
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
            loading="lazy"
          />
        </div>
        <div className="text-center">
          <h3 className="font-serif text-lg font-medium text-foreground truncate">
            {commonNames[0] || scientificName}
          </h3>
          <p className="text-sm text-muted-foreground italic truncate">
            {scientificName}
          </p>
        </div>
      </div>
    </Link>
  );
}