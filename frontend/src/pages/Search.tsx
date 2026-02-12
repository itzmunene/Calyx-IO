import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { Navbar } from "@/components/Navbar";
import { SearchBar } from "@/components/SearchBar";
import { SpeciesCard } from "@/components/SpeciesCard";
import { searchFlowers, SearchResult } from "@/lib/api";
import { Loader2, Flower2 } from "lucide-react";

export default function Search() {
  const [searchParams] = useSearchParams();
  const initialQuery = searchParams.get("q") || "";
  
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [currentQuery, setCurrentQuery] = useState(initialQuery);

  useEffect(() => {
    if (initialQuery) {
      performSearch(initialQuery);
    }
  }, [initialQuery]);

  const performSearch = async (query: string) => {
    if (!query.trim()) return;
    
    setIsLoading(true);
    setHasSearched(true);
    setCurrentQuery(query);

    try {
      const searchResults = await searchFlowers(query);
      setResults(searchResults);
    } catch (err) {
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <main className="pt-24 pb-16">
        <div className="container mx-auto px-4">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-serif font-bold text-foreground mb-4">
              Search Flowers
            </h1>
            <p className="text-muted-foreground max-w-lg mx-auto mb-8">
              Explore our database of beautiful flowers by name.
            </p>
            <SearchBar
              onSearch={performSearch}
              showSuggestions={true}
              className="max-w-xl mx-auto"
            />
          </div>

          {/* Results */}
          <div className="max-w-6xl mx-auto">
            {isLoading && (
              <div className="flex flex-col items-center justify-center py-20">
                <Loader2 className="w-10 h-10 text-primary animate-spin mb-4" />
                <p className="text-muted-foreground">Searching flowers...</p>
              </div>
            )}

            {!isLoading && hasSearched && results.length === 0 && (
              <div className="text-center py-20">
                <Flower2 className="w-16 h-16 text-muted-foreground/50 mx-auto mb-4" />
                <h3 className="font-serif text-xl font-medium text-foreground mb-2">
                  No flowers found
                </h3>
                <p className="text-muted-foreground">
                  Try searching for a different flower name.
                </p>
              </div>
            )}

            {!isLoading && results.length > 0 && (
              <>
                <p className="text-sm text-muted-foreground mb-6">
                  Found {results.length} results for "{currentQuery}"
                </p>
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4 md:gap-6">
                  {results.map((result) => (
                    <SpeciesCard
                      key={result.id}
                      id={result.id}
                      scientificName={result.scientific_name}
                      commonNames={result.common_names}
                      imageUrl={result.primary_image_url}
                    />
                  ))}
                </div>
              </>
            )}

            {!isLoading && !hasSearched && (
              <div className="text-center py-20">
                <Flower2 className="w-16 h-16 text-muted-foreground/50 mx-auto mb-4 animate-float" />
                <h3 className="font-serif text-xl font-medium text-foreground mb-2">
                  Start Exploring
                </h3>
                <p className="text-muted-foreground">
                  Search for any flower by common or scientific name.
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}