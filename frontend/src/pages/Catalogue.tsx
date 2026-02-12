import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Flower2, SlidersHorizontal, X } from "lucide-react";
import { Navbar } from "@/components/Navbar";
import { CatalogueCard, CatalogueCardSkeleton } from "@/components/catalogue/CatalogueCard";
import { CatalogueFilters } from "@/components/catalogue/CatalogueFilters";
import { CatalogueEmptyState } from "@/components/catalogue/CatalogueEmptyState";
import { CataloguePagination } from "@/components/catalogue/CataloguePagination";
import { useCatalogueParams } from "@/hooks/useCatalogueParams";
import { useDebounce } from "@/hooks/useDebounce";
import { getCatalogue, getCatalogueFilters } from "@/lib/api";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

export default function Catalogue() {
  const { params, setParam, clearAll, activeFilterCount } = useCatalogueParams();
  const [localSearch, setLocalSearch] = useState(params.name);
  const debouncedSearch = useDebounce(localSearch, 300);
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false);

  // Sync debounced search to URL params
  const searchToUse = debouncedSearch !== params.name ? debouncedSearch : params.name;
  if (debouncedSearch !== params.name) {
    setParam("name", debouncedSearch);
  }

  // Fetch filters
  const { data: filterOptions } = useQuery({
    queryKey: ["catalogue-filters"],
    queryFn: getCatalogueFilters,
    staleTime: 5 * 60 * 1000,
  });

  // Fetch catalogue
  const { data, isLoading, isError } = useQuery({
    queryKey: [
      "catalogue",
      searchToUse,
      params.colors.join(","),
      params.country,
      params.sortBy,
      params.page,
    ],
    queryFn: () =>
      getCatalogue({
        name: searchToUse || undefined,
        color: params.colors.length > 0 ? params.colors.join(",") : undefined,
        country: params.country || undefined,
        sort_by: params.sortBy,
        page: params.page,
      }),
  });

  const handleColorToggle = (color: string) => {
    const current = params.colors;
    const updated = current.includes(color)
      ? current.filter((c) => c !== color)
      : [...current, color];
    setParam("color", updated);
  };

  const handleSearchChange = (value: string) => {
    setLocalSearch(value);
  };

  const handleClearAll = () => {
    setLocalSearch("");
    clearAll();
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <div className="pt-24 pb-16">
        <div className="container mx-auto px-4">
          {/* Header */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-full text-primary text-sm font-medium mb-4">
              <Flower2 className="w-4 h-4" />
              Explore Our Collection
            </div>
            <h1 className="text-4xl md:text-5xl font-serif font-bold text-foreground mb-3">
              Flower Catalogue
            </h1>
            {data && (
              <p className="text-muted-foreground">
                {data.total.toLocaleString()} {data.total === 1 ? "species" : "species"} found
              </p>
            )}
          </div>

          {/* Mobile filter toggle */}
          <div className="lg:hidden mb-6">
            <button
              onClick={() => setMobileFiltersOpen(!mobileFiltersOpen)}
              className="w-full flex items-center justify-between px-4 py-3 rounded-xl bg-card border border-border shadow-soft"
            >
              <div className="flex items-center gap-2">
                <SlidersHorizontal className="w-5 h-5 text-primary" />
                <span className="font-medium text-foreground">Filters</span>
                {activeFilterCount > 0 && (
                  <Badge className="bg-primary text-primary-foreground text-xs px-2 py-0.5">
                    {activeFilterCount}
                  </Badge>
                )}
              </div>
              <X
                className={cn(
                  "w-4 h-4 text-muted-foreground transition-transform",
                  !mobileFiltersOpen && "rotate-45"
                )}
              />
            </button>
          </div>

          <div className="flex gap-8">
            {/* Sidebar - Desktop */}
            <aside
              className={cn(
                "w-72 shrink-0",
                "hidden lg:block"
              )}
            >
              <div className="sticky top-24 bg-card rounded-2xl border border-border p-6 shadow-soft">
                <CatalogueFilters
                  searchValue={localSearch}
                  onSearchChange={handleSearchChange}
                  sortBy={params.sortBy}
                  onSortChange={(v) => setParam("sort_by", v)}
                  selectedColors={params.colors}
                  onColorToggle={handleColorToggle}
                  selectedCountry={params.country}
                  onCountryChange={(v) => setParam("country", v)}
                  countries={filterOptions?.countries || []}
                  activeFilterCount={activeFilterCount}
                  onClearAll={handleClearAll}
                />
              </div>
            </aside>

            {/* Mobile filters panel */}
            {mobileFiltersOpen && (
              <div className="lg:hidden fixed inset-x-0 top-16 bottom-0 z-40 bg-background/95 backdrop-blur-sm overflow-y-auto p-4">
                <div className="bg-card rounded-2xl border border-border p-6 shadow-soft">
                  <CatalogueFilters
                    searchValue={localSearch}
                    onSearchChange={handleSearchChange}
                    sortBy={params.sortBy}
                    onSortChange={(v) => setParam("sort_by", v)}
                    selectedColors={params.colors}
                    onColorToggle={handleColorToggle}
                    selectedCountry={params.country}
                    onCountryChange={(v) => setParam("country", v)}
                    countries={filterOptions?.countries || []}
                    activeFilterCount={activeFilterCount}
                    onClearAll={handleClearAll}
                  />
                  <button
                    onClick={() => setMobileFiltersOpen(false)}
                    className="btn-botanical w-full mt-6 text-center"
                  >
                    Show Results
                  </button>
                </div>
              </div>
            )}

            {/* Main content */}
            <main className="flex-1 min-w-0">
              {isLoading ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
                  {Array.from({ length: 9 }).map((_, i) => (
                    <CatalogueCardSkeleton key={i} />
                  ))}
                </div>
              ) : isError ? (
                <div className="text-center py-20">
                  <p className="text-muted-foreground mb-4">
                    Something went wrong loading the catalogue.
                  </p>
                  <button
                    onClick={() => window.location.reload()}
                    className="btn-botanical-outline text-sm"
                  >
                    Try Again
                  </button>
                </div>
              ) : data && data.items.length > 0 ? (
                <>
                  <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
                    {data.items.map((item) => (
                      <CatalogueCard key={item.id} item={item} />
                    ))}
                  </div>
                  <CataloguePagination
                    currentPage={data.page}
                    totalPages={data.total_pages}
                    onPageChange={(p) => setParam("page", p)}
                  />
                </>
              ) : (
                <CatalogueEmptyState
                  hasFilters={activeFilterCount > 0}
                  onClearFilters={handleClearAll}
                />
              )}
            </main>
          </div>
        </div>
      </div>
    </div>
  );
}
