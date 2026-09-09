"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { AppSidebar } from "./AppSidebar";
import { Topbar } from "./Topbar";
import { SidebarProvider, SidebarInset } from "@/components/ui/sidebar";

export function AppShell({
  title,
  adminOnly = false,
  children,
}: {
  title: string;
  adminOnly?: boolean;
  children: React.ReactNode;
}) {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    } else if (!loading && adminOnly && user?.role !== "ADMIN") {
      router.replace("/dashboard");
    }
  }, [loading, user, adminOnly, router]);

  if (loading || !user || (adminOnly && user.role !== "ADMIN")) {
    return (
      <div className="flex items-center justify-center h-screen text-muted-foreground text-sm">
        Loading SecurePrint&hellip;
      </div>
    );
  }

  return (
    <SidebarProvider
      open={sidebarOpen}
      onOpenChange={setSidebarOpen}
      style={{ "--sidebar-width": "15rem" } as React.CSSProperties}
    >
      <AppSidebar onMouseEnter={() => setSidebarOpen(true)} onMouseLeave={() => setSidebarOpen(false)} />
      <SidebarInset>
        <Topbar title={title} />
        <main className="flex-1 p-6 overflow-x-hidden bg-muted/30">{children}</main>
      </SidebarInset>
    </SidebarProvider>
  );
}
