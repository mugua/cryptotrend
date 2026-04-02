"use client";

import { useState } from "react";
import {
  LayoutDashboard,
  BarChart3,
  FileText,
  Star,
  Settings,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { type Locale, locales } from "@/i18n";

interface NavItem {
  key: string;
  href: string;
  icon: React.ElementType;
}

const navItems: NavItem[] = [
  { key: "dashboard", href: "/dashboard", icon: LayoutDashboard },
  { key: "analysis", href: "/analysis", icon: BarChart3 },
  { key: "reports", href: "/reports", icon: FileText },
  { key: "watchlist", href: "/watchlist", icon: Star },
  { key: "settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();
  const t = useTranslations("nav");

  // Extract current locale from pathname
  const currentLocale = (locales.find(
    (locale) => pathname.startsWith(`/${locale}/`) || pathname === `/${locale}`
  ) ?? "en") as Locale;

  const isActive = (href: string) => {
    const localizedHref = `/${currentLocale}${href}`;
    return pathname === localizedHref || pathname.startsWith(`${localizedHref}/`);
  };

  return (
    <aside
      className={cn(
        "fixed left-0 top-16 z-40 h-[calc(100vh-4rem)] border-r bg-background transition-all duration-300 ease-in-out",
        collapsed ? "w-16" : "w-60"
      )}
    >
      <div className="flex h-full flex-col">
        {/* Navigation */}
        <nav className="flex-1 space-y-1 p-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);
            const localizedHref = `/${currentLocale}${item.href}`;

            return (
              <Link
                key={item.key}
                href={localizedHref}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  active
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
                  collapsed && "justify-center px-2"
                )}
                title={collapsed ? t(item.key) : undefined}
              >
                <Icon className="h-5 w-5 shrink-0" />
                {!collapsed && (
                  <span className="truncate">{t(item.key)}</span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Collapse toggle */}
        <div className="p-2">
          <Separator className="mb-2" />
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setCollapsed((prev) => !prev)}
            className={cn(
              "w-full transition-colors",
              collapsed ? "justify-center px-2" : "justify-start gap-2"
            )}
          >
            {collapsed ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <>
                <ChevronLeft className="h-4 w-4" />
                <span>Collapse</span>
              </>
            )}
          </Button>
        </div>
      </div>
    </aside>
  );
}
