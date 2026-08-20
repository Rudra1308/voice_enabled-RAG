"use client"

import { useState, useRef, useEffect } from "react"
import { UploadCloud, File as FileIcon, X, CheckCircle2, AlertCircle } from "lucide-react"

export function FileUploader() {
  const [isDragging, setIsDragging] = useState(false)
  const [files, setFiles] = useState<{ id?: string, file: File | { name: string }, status: string; progress: number }[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const res = await fetch("/api/documents/");
        if (res.ok) {
          const data = await res.json();
          const existingFiles = data.documents.map((doc: any) => ({
            id: doc.id,
            file: { name: doc.filename },
            status: doc.status.toLowerCase() === 'ready' || doc.status.toLowerCase() === 'pending' ? 'success' : 'error',
            progress: 100
          }));
          setFiles(existingFiles);
        }
      } catch (err) {
        console.error("Failed to fetch documents", err);
      }
    };
    fetchDocuments();
  }, []);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(Array.from(e.dataTransfer.files))
    }
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(Array.from(e.target.files))
    }
  }

  const handleFiles = (newFiles: File[]) => {
    const fileObjects = newFiles.map(f => ({ file: f, status: "pending", progress: 0 }))
    setFiles(prev => [...prev, ...fileObjects])
    
    // Start upload for each
    fileObjects.forEach((fObj, idx) => {
      uploadFile(fObj.file, files.length + idx)
    })
  }

  const uploadFile = async (file: File, index: number) => {
    const formData = new FormData()
    formData.append("file", file)

    // Simulate progress for UI (since fetch doesn't have native upload progress easily)
    const progressInterval = setInterval(() => {
      setFiles(prev => {
        const newFiles = [...prev]
        if (newFiles[index] && newFiles[index].progress < 90) {
          newFiles[index].progress += 10
        }
        return newFiles
      })
    }, 200)

    try {
      const res = await fetch("/api/documents/upload", {
        method: "POST",
        body: formData,
      })
      
      clearInterval(progressInterval)

      if (res.ok) {
        setFiles(prev => {
          const newFiles = [...prev]
          newFiles[index].status = "success"
          newFiles[index].progress = 100
          return newFiles
        })
      } else {
        throw new Error("Upload failed")
      }
    } catch (err) {
      clearInterval(progressInterval)
      setFiles(prev => {
        const newFiles = [...prev]
        newFiles[index].status = "error"
        newFiles[index].progress = 0
        return newFiles
      })
    }
  }

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      <div 
        className={`border-2 border-dashed rounded-2xl p-12 text-center transition-all ${
          isDragging ? "border-primary bg-primary/5" : "border-border hover:border-primary/50 hover:bg-muted/50"
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input 
          type="file" 
          ref={fileInputRef} 
          onChange={handleFileInput} 
          className="hidden" 
          multiple 
          accept=".pdf,.docx,.txt"
        />
        <div className="flex justify-center mb-4">
          <div className="p-4 bg-primary/10 rounded-full text-primary">
            <UploadCloud className="w-8 h-8" />
          </div>
        </div>
        <h3 className="text-xl font-semibold mb-2">Click or drag documents to upload</h3>
        <p className="text-muted-foreground text-sm">
          Supports PDF, DOCX, TXT up to 50MB
        </p>
      </div>

      {files.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Uploads</h4>
          {files.map((item, i) => (
            <div key={i} className="flex items-center gap-4 p-4 rounded-xl border bg-card shadow-sm">
              <div className="p-2 bg-primary/10 rounded-lg text-primary">
                <FileIcon className="w-5 h-5" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{item.file.name}</p>
                <div className="flex items-center gap-2 mt-1">
                  <div className="h-1.5 flex-1 bg-secondary rounded-full overflow-hidden">
                    <div 
                      className={`h-full transition-all duration-300 ${
                        item.status === "error" ? "bg-destructive" : "bg-primary"
                      }`}
                      style={{ width: `${item.progress}%` }}
                    />
                  </div>
                  <span className="text-xs text-muted-foreground w-8">{item.progress}%</span>
                </div>
              </div>
              <div>
                {item.status === "success" && <CheckCircle2 className="w-5 h-5 text-green-500" />}
                {item.status === "error" && <AlertCircle className="w-5 h-5 text-destructive" />}
                {item.status === "pending" && (
                  <button onClick={() => removeFile(i)} className="text-muted-foreground hover:text-foreground">
                    <X className="w-5 h-5" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
