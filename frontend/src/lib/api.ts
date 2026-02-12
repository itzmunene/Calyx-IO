const API_BASE = "https://calyx-api.onrender.com";

export interface IdentificationResult {
  scientific_name: string;
  common_names: string[];
  confidence: number;
  primary_image_url: string;
  alternatives?: AlternativeResult[];
}

export interface AlternativeResult {
  scientific_name: string;
  common_names: string[];
  confidence: number;
  primary_image_url: string;
}

export interface SearchResult {
  id: string;
  scientific_name: string;
  common_names: string[];
  primary_image_url: string;
}

export interface SpeciesDetail {
  id?: string;
  scientific_name: string;
  common_names: string[];
  description: string;
  care_tips: string;
  bloom_season?: string[];
  primary_image_url: string;
}

export interface CatalogueItem {
  id: string;
  scientific_name: string;
  common_names: string[];
  primary_image_url: string;
  colors?: string[];
  search_count?: number;
  country?: string;
}

export interface CatalogueResponse {
  items: CatalogueItem[];
  total: number;
  page: number;
  total_pages: number;
}

export interface CatalogueFilters {
  colors: string[];
  countries: string[];
}

export interface CatalogueParams {
  name?: string;
  color?: string;
  country?: string;
  sort_by?: string;
  page?: number;
}

export async function identifyFlower(image: File): Promise<IdentificationResult> {
  const formData = new FormData();
  formData.append("image", image);

  const response = await fetch(`${API_BASE}/api/v1/identify`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Failed to identify flower");
  }

  return response.json();
}

export async function searchFlowers(query: string, limit = 20): Promise<SearchResult[]> {
  const response = await fetch(
    `${API_BASE}/api/v1/search?q=${encodeURIComponent(query)}&limit=${limit}`
  );

  if (!response.ok) {
    throw new Error("Failed to search flowers");
  }

  return response.json();
}

export async function getSpeciesDetail(id: string): Promise<SpeciesDetail> {
  const response = await fetch(`${API_BASE}/api/v1/species/${id}`);

  if (!response.ok) {
    throw new Error("Failed to get species details");
  }

  return response.json();
}

export async function getCatalogue(params: CatalogueParams): Promise<CatalogueResponse> {
  const searchParams = new URLSearchParams();
  if (params.name) searchParams.set("name", params.name);
  if (params.color) searchParams.set("color", params.color);
  if (params.country) searchParams.set("country", params.country);
  if (params.sort_by) searchParams.set("sort_by", params.sort_by);
  if (params.page) searchParams.set("page", String(params.page));

  const response = await fetch(`${API_BASE}/api/v1/catalogue?${searchParams.toString()}`);

  if (!response.ok) {
    throw new Error("Failed to fetch catalogue");
  }

  return response.json();
}

export async function getCatalogueFilters(): Promise<CatalogueFilters> {
  const response = await fetch(`${API_BASE}/api/v1/catalogue/filters`);

  if (!response.ok) {
    throw new Error("Failed to fetch filters");
  }

  return response.json();
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/health`);
    return response.ok;
  } catch {
    return false;
  }
}