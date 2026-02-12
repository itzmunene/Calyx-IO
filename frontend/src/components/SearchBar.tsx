import { useState, useEffect, useRef } from "react";
import { Search, X, Loader2 } from "lucide-react";
import { useDebounce } from "@/hooks/useDebounce";
import { searchFlowers, SearchResult } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useNavigate } from "react-router-dom";

interface SearchBarProps {
  onSearch?: (query: string) => void;
  showSuggestions?: boolean;
  className?: string;
  placeholder?: string;
}

export function SearchBar({
  onSearch,
  showSuggestions = true,
  className,
  placeholder = "Search flowers by name...",
}: SearchBarProps) {
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const debouncedQuery = useDebounce(query, 300);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (debouncedQuery.length >= 2 && showSuggestions) {
      setIsLoading(true);
      searchFlowers(debouncedQuery, 5)
        .then((results) => {
          setSuggestions(results);
          setShowDropdown(true);
        })
        .catch(() => setSuggestions([]))
        .finally(() => setIsLoading(false));
    } else {
      setSuggestions([]);
      setShowDropdown(false);
    }
  }, [debouncedQuery, showSuggestions]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      setShowDropdown(false);
      onSearch?.(query.trim());
      navigate(`/search?q=${encodeURIComponent(query.trim())}`);
    }
  };

  const handleSuggestionClick = (result: SearchResult) => {
    setShowDropdown(false);
    setQuery("");
    navigate(`/species/${result.id}`);
  };

  const clearQuery = () => {
    setQuery("");
    setSuggestions([]);
    setShowDropdown(false);
    inputRef.current?.focus();
  };

  return (
    <div className={cn("relative", className)}>
      <form onSubmit={handleSubmit}>
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => suggestions.length > 0 && setShowDropdown(true)}
            placeholder={placeholder}
            className="w-full pl-12 pr-12 py-4 bg-card border border-border rounded-full text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all shadow-soft"
          />
          {query && (
            <button
              type="button"
              onClick={clearQuery}
              className="absolute right-4 top-1/2 -translate-y-1/2 w-6 h-6 flex items-center justify-center text-muted-foreground hover:text-foreground transition-colors"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <X className="w-4 h-4" />
              )}
            </button>
          )}
        </div>
      </form>

      {/* Suggestions Dropdown */}
      {showDropdown && suggestions.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-card border border-border rounded-2xl shadow-elevated overflow-hidden z-50">
          {suggestions.map((result) => (
            <button
              key={result.id}
              onClick={() => handleSuggestionClick(result)}
              className="w-full flex items-center gap-4 p-3 hover:bg-muted/50 transition-colors text-left"
            >
              <img
                src={result.primary_image_url}
                alt={result.scientific_name}
                className="w-12 h-12 rounded-lg object-cover"
              />
              <div className="flex-1 min-w-0">
                <p className="font-medium text-foreground truncate">
                  {result.common_names[0] || result.scientific_name}
                </p>
                <p className="text-sm text-muted-foreground italic truncate">
                  {result.scientific_name}
                </p>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}