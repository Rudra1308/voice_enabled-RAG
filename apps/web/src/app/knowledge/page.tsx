import { FileUploader } from "@/components/file-uploader"

export default function KnowledgeBasePage() {
  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight mb-2">Knowledge Base</h1>
        <p className="text-muted-foreground">Upload and manage your academic documents to construct the retrieval context.</p>
      </div>
      
      <FileUploader />
    </div>
  )
}
