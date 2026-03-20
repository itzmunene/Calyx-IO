// frontend/src/lib/api.ts

// Vite: uses import.meta.env.*
// Local default: http://localhost:8000
const API_BASE =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ||
  "http://localhost:8000";


const allowedTypes = ["image/jpeg", "image/png", "image/webp"];
const maxSize = 5 * 1024 * 1024;

const API_KEY = import.meta.env.VITE_API_KEY;


function validateBeforeUpload(file: File): string | null {
  if (!allowedTypes.includes(file.type)) {
    return "Please upload a JPG, PNG, or WEBP image.";
  }

  if (file.size > maxSize) {
    return "File too large. Maximum allowed size is 5MB.";
  }

  return null;
}

export interface AlternativeResult {
  id?: string;
  scientific_name: string;
  common_names: string[];
  confidence: number;
  primary_image_url: string | null;
  trait_score?: number;
}

export interface IdentificationResult {
  species_id?: string;
  scientific_name: string;
  common_names: string[];
  confidence: number;
  primary_image_url: string | null;
  method?: string;
  traits_extracted?: Record<string, any>;
  alternatives?: AlternativeResult[];
  response_time_ms?: number;
}

export interface SearchResult {
  id: string;
  scientific_name: string;
  common_names: string[];
  primary_image_url: string | null;
  family?: string | null;
}

export interface SpeciesDetail {
  id?: string;
  scientific_name: string;
  common_names: string[];
  description?: string | null;
  care_tips?: string | null;
  bloom_season?: string[];
  primary_image_url?: string | null;
  // if you return growing_info etc, add later
}

export interface CatalogueItem {
  id: string;
  scientific_name: string;
  common_names: string[];
  primary_image_url: string | null;

  traits?: { color_primary?: string[] };
  colors?: string[];
  search_count?: number;
  country?: string;
}

export interface CatalogueResponse {
  items: CatalogueItem[];
  total: number;
  page: number;
  total_pages?: number;
  pages?: number;
}

export type FilterOption = {
  value: string;
  label: string;
  count?: number;
};
export interface CatalogueFilters {
  colors: FilterOption[];
  countries: FilterOption[];
  sort_options?: { value: string; label: string }[];
}


export type SortBy = "name" | "popularity" | "recent";

export interface CatalogueParams {
  name?: string;
  color?: string;
  country?: string;
  sort_by?: SortBy;
  page?: number;
  limit?: number;
}


async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, init);

  if (!res.ok) {
    // return useful error text from FastAPI if present
    const text = await res.text().catch(() => "");
    throw new Error(`API ${res.status} ${res.statusText}: ${text || "Request failed"}`);
  }

  return res.json() as Promise<T>;
}

export async function identifyFlower(image: File): Promise<IdentificationResult> {
  const validationError = validateBeforeUpload(image);
  if (validationError) {
    throw new Error(validationError);
  }

  const formData = new FormData();
  formData.append("image", image);

  const response = await fetch(`${API_BASE}/api/v1/identify`, {
  method: "POST",
  headers: {
    Authorization: `Bearer ${import.meta.env.VITE_API_KEY}`,
  },
  body: formData,
});

  if (!response.ok) {
    let message = "Unable to identify the flower.";
    try {
      const data = await response.json();
      message = data.detail || data.error || message;
    } catch {
      // keep fallback message
    }
    throw new Error(message);
  }

  return response.json();
}

export async function searchFlowers(query: string, limit = 20): Promise<SearchResult[]> {
  const params = new URLSearchParams({
    q: query,
    limit: String(limit),
  });

  return request<SearchResult[]>(`/api/v1/search?${params.toString()}`);
}

export async function getSpeciesDetail(id: string): Promise<SpeciesDetail> {
  return request<SpeciesDetail>(`/api/v1/species/${encodeURIComponent(id)}`);
}

export async function getCatalogue(params: CatalogueParams): Promise<CatalogueResponse> {
  const searchParams = new URLSearchParams();

  if (params.name) searchParams.set("name", params.name);
  if (params.color) searchParams.set("color", params.color);
  if (params.country) searchParams.set("country", params.country);
  if (params.sort_by) searchParams.set("sort_by", params.sort_by);
  if (params.page) searchParams.set("page", String(params.page));
  if (params.limit) searchParams.set("limit", String(params.limit));

  return request<CatalogueResponse>(`/api/v1/catalogue?${searchParams.toString()}`);
}

export async function getCatalogueFilters(): Promise<CatalogueFilters> {
  return request<CatalogueFilters>("/api/v1/catalogue/filters");
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/health`);
    return res.ok;
  } catch {
    return false;
  }
}