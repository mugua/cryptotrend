"use client";

import Link from "next/link";
import { Github } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t py-6 transition-colors">
      <div className="flex flex-col items-center justify-center gap-2 px-4 md:flex-row md:gap-4">
        <p className="text-sm text-muted-foreground">
          © 2024 CryptoTrend. All rights reserved.
        </p>
        <Link
          href="https://github.com"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1 text-sm text-muted-foreground transition-colors hover:text-foreground"
        >
          <Github className="h-4 w-4" />
          <span>GitHub</span>
        </Link>
      </div>
    </footer>
  );
}
