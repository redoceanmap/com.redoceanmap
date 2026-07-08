"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, MapPin, Bookmark, MessageSquare } from "lucide-react";

const tabs = [
  { icon: Home, label: "홈", href: "/" },
  { icon: MessageSquare, label: "대화", href: "/" },
  { icon: MapPin, label: "지도", href: "/map" },
  { icon: Bookmark, label: "찜한 곳", href: "/" },
];

export default function BottomTabBar() {
  const pathname = usePathname();

  if (pathname?.startsWith("/admin")) return null;

  return (
    <nav
      className="sm:hidden fixed bottom-0 left-0 right-0 z-50 bg-surface/90 backdrop-blur-md border-t border-border"
      style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
    >
      <div className="flex items-center h-14">
        {tabs.map(({ icon: Icon, label, href }) => {
          const active = label === "지도" ? pathname === "/map" : label === "홈" && pathname === "/";

          return (
            <Link
              key={label}
              href={href}
              className={`flex-1 flex flex-col items-center justify-center gap-0.5 py-2 transition-colors ${
                active ? "text-brand" : "text-foreground-muted"
              }`}
            >
              <Icon size={22} strokeWidth={active ? 2.25 : 1.75} />
              <span className="text-[10px] font-medium">{label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
