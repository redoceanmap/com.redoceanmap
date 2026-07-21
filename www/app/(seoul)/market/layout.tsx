import TabGuard from "@/components/seoul/TabGuard";

export default function Layout({ children }: { children: React.ReactNode }) {
  return <TabGuard tab="market">{children}</TabGuard>;
}
