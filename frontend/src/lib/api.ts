// api.ts

// Vite: uses import.meta.env.*
// Local default: http://localhost:8000
const API_BASE =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ||
  "http://localhost:8000";

export interface IdentificationResult {
  scientific_name: string;
  common_names: string[];
  confidence: number;
  primary_image_url: string | null;
  alternatives?: AlternativeResult[];
}

export interface AlternativeResult {
  scientific_name: string;
  common_names: string[];
  confidence: number;
  primary_image_url: string | null;
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
  colors?: string[];
  search_count?: number;
  countries: FilterOption[];
}

export interface CatalogueResponse {
  items: CatalogueItem[];
  total: number;
  page: number;
  total_pages: number;
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
  const formData = new FormData();
  formData.append("image", image);

  return request<IdentificationResult>("/api/v1/identify", {
    method: "POST",
    body: formData,
  });
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
