'use client';

import React, { useState, useRef } from 'react';
import { Mic, Square } from 'lucide-react';

interface VoiceInputProps {
  onTranscribe: (text: string) => void;
  isProcessing?: boolean;
}

export function VoiceInput({ onTranscribe, isProcessing = false }: VoiceInputProps) {
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      
      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
        chunksRef.current = []; // reset
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());

        // Upload to API
        await handleUpload(audioBlob);
      };

      chunksRef.current = [];
      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Error accessing microphone:", err);
      alert("Could not access microphone.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleUpload = async (blob: Blob) => {
    const formData = new FormData();
    formData.append('file', blob, 'recording.webm');

    try {
      // Send to FastAPI
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      const res = await fetch(`${apiUrl}/api/voice/transcribe`, {
        method: 'POST',
        body: formData,
      });
      
      if (res.ok) {
        const data = await res.json();
        onTranscribe(data.text);
      } else {
        console.error("Transcription failed");
      }
    } catch (error) {
      console.error("Upload error", error);
    }
  };

  return (
    <div className="flex items-center space-x-2">
      {isRecording ? (
        <button 
          onClick={stopRecording}
          className="flex h-12 w-12 items-center justify-center rounded-full bg-red-500 text-white hover:bg-red-600 animate-pulse"
          disabled={isProcessing}
        >
          <Square className="h-5 w-5 fill-current" />
        </button>
      ) : (
        <button 
          onClick={startRecording}
          className="flex h-12 w-12 items-center justify-center rounded-full bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
          disabled={isProcessing}
        >
          <Mic className="h-5 w-5" />
        </button>
      )}
      {isRecording && <span className="text-sm text-red-500 font-medium">Recording...</span>}
      {isProcessing && <span className="text-sm text-blue-500 font-medium">Transcribing...</span>}
    </div>
  );
}
