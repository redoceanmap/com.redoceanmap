"use client";

import { useEffect, useRef } from "react";
import type { Area } from "@/lib/mockApi";

declare global {
  interface Window {
    kakao: any;
  }
}

const KAKAO_SDK_URL = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${process.env.NEXT_PUBLIC_KAKAO_MAP_KEY}&autoload=false`;

type Props = {
  areas: Area[];
  selectedId: string | null;
  onSelect: (id: string) => void;
};

function makePinContent(selected: boolean): string {
  const fill = selected ? "#7A1515" : "#991B1B";
  const w = selected ? 34 : 26;
  const h = selected ? 44 : 33;
  const shadow = selected
    ? "filter:drop-shadow(0 3px 6px rgba(0,0,0,0.35))"
    : "filter:drop-shadow(0 1px 3px rgba(0,0,0,0.25))";
  return `<div style="cursor:pointer;${shadow}">
    <svg width="${w}" height="${h}" viewBox="0 0 16 20" aria-hidden="true">
      <path d="M8 0C3.6 0 0 3.6 0 8c0 6 8 12 8 12s8-6 8-12c0-4.4-3.6-8-8-8z" fill="${fill}"/>
      <circle cx="8" cy="8" r="2.5" fill="#FFFFFF"/>
    </svg>
  </div>`;
}

export default function MapView({ areas, selectedId, onSelect }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<any>(null);
  const overlaysRef = useRef<{ id: string; overlay: any }[]>([]);
  const areasRef = useRef(areas);
  const onSelectRef = useRef(onSelect);
  const selectedIdRef = useRef(selectedId);

  areasRef.current = areas;
  onSelectRef.current = onSelect;
  selectedIdRef.current = selectedId;

  function placeMarkers(map: any, list: Area[], currentSelectedId: string | null) {
    overlaysRef.current.forEach(({ overlay }) => overlay.setMap(null));
    overlaysRef.current = [];

    list.forEach((area) => {
      const pos = new window.kakao.maps.LatLng(area.lat, area.lng);
      const isSelected = area.id === currentSelectedId;

      const content = document.createElement("div");
      content.innerHTML = makePinContent(isSelected);
      content.addEventListener("click", () => onSelectRef.current(area.id));

      const overlay = new window.kakao.maps.CustomOverlay({
        position: pos,
        content,
        yAnchor: 1,
        map,
      });

      overlaysRef.current.push({ id: area.id, overlay });
    });
  }

  function initMap() {
    if (!containerRef.current || mapRef.current) return;
    const map = new window.kakao.maps.Map(containerRef.current, {
      center: new window.kakao.maps.LatLng(37.5445, 126.988),
      level: 7,
    });
    mapRef.current = map;
    placeMarkers(map, areasRef.current, selectedIdRef.current);

    const sel = areasRef.current.find((a) => a.id === selectedIdRef.current);
    if (sel) map.setCenter(new window.kakao.maps.LatLng(sel.lat, sel.lng));
  }

  useEffect(() => {
    const load = () => window.kakao.maps.load(initMap);

    if (window.kakao?.maps) { load(); return; }

    if (document.querySelector(`script[src*="dapi.kakao.com"]`)) {
      const id = setInterval(() => {
        if (window.kakao?.maps) { clearInterval(id); load(); }
      }, 100);
      return () => clearInterval(id);
    }

    const script = document.createElement("script");
    script.src = KAKAO_SDK_URL;
    script.async = true;
    script.onload = load;
    document.head.appendChild(script);
  }, []);

  useEffect(() => {
    if (!mapRef.current || areas.length === 0) return;
    placeMarkers(mapRef.current, areas, selectedIdRef.current);
  }, [areas]);

  useEffect(() => {
    if (!mapRef.current) return;
    placeMarkers(mapRef.current, areasRef.current, selectedId);
    const area = areasRef.current.find((a) => a.id === selectedId);
    if (area) mapRef.current.panTo(new window.kakao.maps.LatLng(area.lat, area.lng));
  }, [selectedId]);

  return <div ref={containerRef} className="w-full h-full rounded-2xl overflow-hidden" />;
}
