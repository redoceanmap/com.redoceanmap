const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export type MarketArea = {
  trdar_code: number;
  trdar_name: string;
  trdar_div_code: string;
  trdar_div_name: string;
  lat: number;
  lng: number;
  district_name: string;
  adm_dong_name: string;
  area_size: number;
  region: string;
};

export async function fetchAreas(district?: string): Promise<MarketArea[]> {
  const url = new URL(`${API_BASE}/market/areas`);
  if (district) url.searchParams.set("district", district);
  const res = await fetch(url.toString(), { cache: "no-store" });
  if (!res.ok) throw new Error("상권 데이터를 불러오지 못했습니다.");
  return res.json();
}
