import { Search, X, SlidersHorizontal } from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

const SORT_OPTIONS = [
  { value: "alphabetical", label: "Alphabetical" },
  { value: "popular", label: "Most Popular" },
  { value: "recent", label: "Recently Added" },
];

const COLOR_OPTIONS = [
  { value: "red", label: "Red", className: "bg-red-500" },
  { value: "pink", label: "Pink", className: "bg-pink-400" },
  { value: "white", label: "White", className: "bg-white border border-border" },
  { value: "yellow", label: "Yellow", className: "bg-yellow-400" },
  { value: "orange", label: "Orange", className: "bg-orange-500" },
  { value: "purple", label: "Purple", className: "bg-purple-500" },
  { value: "blue", label: "Blue", className: "bg-blue-500" },
];

interface CatalogueFiltersProps {
  searchValue: string;
  onSearchChange: (value: string) => void;
  sortBy: string;
  onSortChange: (value: string) => void;
  selectedColors: string[];
  onColorToggle: (color: string) => void;
  selectedCountry: string;
  onCountryChange: (country: string) => void;
  countries: string[];
  activeFilterCount: number;
  onClearAll: () => void;
}

export function CatalogueFilters({
  searchValue,
  onSearchChange,
  sortBy,
  onSortChange,
  selectedColors,
  onColorToggle,
  selectedCountry,
  onCountryChange,
  countries,
  activeFilterCount,
  onClearAll,
}: CatalogueFiltersProps) {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <SlidersHorizontal className="w-5 h-5 text-primary" />
          <h3 className="font-serif text-lg font-semibold text-foreground">Filters</h3>
          {activeFilterCount > 0 && (
            <Badge className="bg-primary text-primary-foreground text-xs px-2 py-0.5">
              {activeFilterCount}
            </Badge>
          )}
        </div>
        {activeFilterCount > 0 && (
          <button
            onClick={onClearAll}
            className="text-sm text-accent-foreground hover:text-primary transition-colors flex items-center gap-1"
          >
            <X className="w-3.5 h-3.5" />
            Clear All
          </button>
        )}
      </div>

      {/* Search */}
      <div>
        <label className="text-sm font-medium text-foreground mb-2 block">Search</label>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            value={searchValue}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search flowers..."
            className="w-full pl-9 pr-4 py-2.5 rounded-lg bg-background border border-border text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all text-sm"
          />
          {searchValue && (
            <button
              onClick={() => onSearchChange("")}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Sort */}
      <div>
        <label className="text-sm font-medium text-foreground mb-2 block">Sort By</label>
        <select
          value={sortBy}
          onChange={(e) => onSortChange(e.target.value)}
          className="w-full px-3 py-2.5 rounded-lg bg-background border border-border text-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all text-sm appearance-none cursor-pointer"
        >
          {SORT_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      {/* Color chips */}
      <div>
        <label className="text-sm font-medium text-foreground mb-3 block">Colors</label>
        <div className="flex flex-wrap gap-2">
          {COLOR_OPTIONS.map((color) => {
            const isSelected = selectedColors.includes(color.value);
            return (
              <button
                key={color.value}
                onClick={() => onColorToggle(color.value)}
                className={cn(
                  "flex items-center gap-2 px-3 py-1.5 rounded-full text-sm transition-all border",
                  isSelected
                    ? "border-primary bg-primary/10 text-primary font-medium"
                    : "border-border bg-background text-muted-foreground hover:border-primary/40"
                )}
              >
                <span className={cn("w-3.5 h-3.5 rounded-full shrink-0", color.className)} />
                {color.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Country */}
      <div>
        <label className="text-sm font-medium text-foreground mb-2 block">Country</label>
        <select
          value={selectedCountry}
          onChange={(e) => onCountryChange(e.target.value)}
          className="w-full px-3 py-2.5 rounded-lg bg-background border border-border text-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all text-sm appearance-none cursor-pointer"
        >
          <option value="">All Countries</option>
          {countries.map((country) => (
            <option key={country} value={country}>
              {country}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
