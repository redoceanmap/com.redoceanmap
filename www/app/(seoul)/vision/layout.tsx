import TabGuard from "@/components/seoul/TabGuard";

// /vision과 /vision/faces를 함께 커버한다 (중첩 라우트 공용 레이아웃)
export default function Layout({ children }: { children: React.ReactNode }) {
  return <TabGuard tab="vision">{children}</TabGuard>;
}
