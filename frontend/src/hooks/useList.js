import { useCallback, useEffect, useState } from "react";
import api from "../api/client";

export function useList(endpoint, initialParams = {}) {
  const [data, setData] = useState({ results: [], count: 0 });
  const [loading, setLoading] = useState(true);
  const [params, setParams] = useState({ page: 1, ...initialParams });

  const fetch = useCallback(() => {
    setLoading(true);
    api
      .get(endpoint, { params })
      .then(({ data }) => {
        if (Array.isArray(data)) setData({ results: data, count: data.length });
        else setData({ results: data.results || [], count: data.count ?? 0 });
      })
      .catch(() => setData({ results: [], count: 0 }))
      .finally(() => setLoading(false));
  }, [endpoint, JSON.stringify(params)]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  function setParam(key, value) {
    setParams((p) => ({ ...p, [key]: value, page: key === "page" ? value : 1 }));
  }

  return { ...data, loading, params, setParam, setParams, refresh: fetch };
}
