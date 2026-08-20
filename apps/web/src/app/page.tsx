"use client"

import { useState } from "react"
import Link from "next/link"
import { Mic, Search, BookOpen } from "lucide-react"

export default function Home() {
  const [isListening, setIsListening] = useState(false)

  return (
    <div className="flex h-full flex-col items-center justify-center p-6 relative">
      {/* Background elements */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] pointer-events-none" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-primary/20 rounded-full blur-[120px] pointer-events-none" />
      
      <div className="z-10 flex flex-col items-center max-w-3xl text-center space-y-8">
        <div className="inline-flex items-center rounded-full border border-primary/20 bg-primary/5 px-3 py-1 text-sm text-primary backdrop-blur-md">
          <span className="flex h-2 w-2 rounded-full bg-primary mr-2" />
          Academic VoiceRAG Prototype
        </div>

        <h1 className="text-5xl sm:text-6xl font-extrabold tracking-tight text-foreground drop-shadow-sm">
          Your Intelligent <br className="hidden sm:block" />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-primary/60">
            Research Assistant
          </span>
        </h1>
        
        <p className="text-lg text-muted-foreground max-w-2xl leading-relaxed">
          Ask complex questions across your academic literature. Powered by hybrid retrieval, local LLMs, and fully grounded citations.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 w-full justify-center pt-8">
          <Link href="/research">
            <button className="flex items-center justify-center gap-3 px-8 py-4 rounded-full text-lg font-medium transition-all shadow-lg bg-primary text-primary-foreground hover:bg-primary/90 hover:scale-105">
              <Mic className="h-5 w-5" />
              Start Voice Query
            </button>
          </Link>
          <Link href="/research">
            <button className="flex items-center justify-center gap-2 px-8 py-4 rounded-full text-lg font-medium bg-secondary text-secondary-foreground hover:bg-secondary/80 border border-border transition-all">
              <Search className="h-5 w-5" />
              Text Search
            </button>
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full mt-12 pt-12 border-t border-border/50 text-left">
          <div className="p-6 rounded-2xl bg-card border shadow-sm backdrop-blur-md">
            <BookOpen className="h-6 w-6 text-primary mb-3" />
            <h3 className="font-semibold mb-1">Synthesize Literature</h3>
            <p className="text-sm text-muted-foreground">Compare methodologies across multiple papers with accurate citations.</p>
          </div>
          <div className="p-6 rounded-2xl bg-card border shadow-sm backdrop-blur-md">
            <Search className="h-6 w-6 text-primary mb-3" />
            <h3 className="font-semibold mb-1">Grounded Answers</h3>
            <p className="text-sm text-muted-foreground">Responses are strictly verified against the indexed knowledge base.</p>
          </div>
        </div>
      </div>
    </div>
  )
}
