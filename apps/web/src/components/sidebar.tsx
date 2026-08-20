"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { FileText, FolderSync, MessagesSquare, Settings, Upload, Activity, Mic } from 'lucide-react';
import { cn } from "@/lib/utils"

const navItems = [
  { name: 'Home', href: '/', icon: FolderSync },
  { name: 'Knowledge Base', href: '/knowledge', icon: Upload },
  { name: 'Research Assistant', href: '/research', icon: MessagesSquare },
  { name: 'Evaluations', href: '/evaluations', icon: Activity },
];

export function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="flex h-full w-64 flex-col border-r bg-card/50 backdrop-blur-sm">
      <div className="flex h-16 items-center gap-2 px-6 border-b">
        <Mic className="h-6 w-6 text-primary" />
        <span className="font-semibold text-lg tracking-tight">VoiceRAG</span>
      </div>
      <nav className="flex-1 space-y-1 p-4">
        {navItems.map((item) => {
          const isActive = pathname === item.href || (item.href !== "/" && pathname?.startsWith(item.href))
          const Icon = item.icon
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive 
                  ? "bg-primary/10 text-primary" 
                  : "text-muted-foreground hover:bg-secondary hover:text-foreground"
              )}
            >
              <Icon className="h-4 w-4" />
              {item.name}
            </Link>
          )
        })}
      </nav>
      <div className="p-4 border-t">
        <div className="rounded-lg bg-secondary p-3">
          <div className="text-xs font-medium mb-1">Local AI Status</div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
            </span>
            Ollama running
          </div>
        </div>
      </div>
    </div>
  )
}
