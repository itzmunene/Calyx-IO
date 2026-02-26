import { useSearchParams } from "react-router-dom";
import { useCallback, useMemo } from "react";

export function useCatalogueParams() {
  const [searchParams, setSearchParams] = useSearchParams();

  const params = useMemo(() => {
    const rawSort = searchParams.get("sort_by") || "name";
    const sortBy = rawSort === "alphabetical" ? "name" : rawSort; // backwards compat

    return {
      name: searchParams.get("name") || "",
      sortBy,
      colors: searchParams.get("color")?.split(",").filter(Boolean) || [],
      country: searchParams.get("country") || "",
      page: Number(searchParams.get("page")) || 1,
    };
  }, [searchParams]);

  const setParam = useCallback(
    (key: string, value: string | string[] | number) => {
      setSearchParams((prev) => {
        const next = new URLSearchParams(prev);
        const strValue = Array.isArray(value) ? value.join(",") : String(value);

        if (!strValue || strValue === "0") next.delete(key);
        else next.set(key, strValue);

        if (key !== "page") next.delete("page"); // reset pagination when filters change
        return next;
      });
    },
    [setSearchParams]
  );

  const clearAll = useCallback(() => {
    setSearchParams({});
  }, [setSearchParams]);

  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (params.name) count++;
    if (params.colors.length > 0) count++;
    if (params.country) count++;
    if (params.sortBy !== "name") count++;
    return count;
  }, [params]);

  return { params, setParam, clearAll, activeFilterCount };
}
