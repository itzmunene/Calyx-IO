import { Flower2, SearchX } from "lucide-react";

interface CatalogueEmptyStateProps {
  hasFilters: boolean;
  onClearFilters: () => void;
}

export function CatalogueEmptyState({ hasFilters, onClearFilters }: CatalogueEmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center mb-6">
        {hasFilters ? (
          <SearchX className="w-10 h-10 text-primary" />
        ) : (
          <Flower2 className="w-10 h-10 text-primary" />
        )}
      </div>
      <h3 className="font-serif text-2xl font-semibold text-foreground mb-2">
        {hasFilters ? "No flowers found" : "No flowers yet"}
      </h3>
      <p className="text-muted-foreground max-w-sm mb-6">
        {hasFilters
          ? "Try adjusting your filters or search term to find what you're looking for."
          : "The catalogue is empty. Check back soon for beautiful blooms!"}
      </p>
      {hasFilters && (
        <button
          onClick={onClearFilters}
          className="btn-botanical-outline text-sm"
        >
          Clear All Filters
        </button>
      )}
    </div>
  );
}
