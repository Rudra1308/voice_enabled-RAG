export class TTSEngine {
  private synth: SpeechSynthesis;
  private voice: SpeechSynthesisVoice | null = null;

  constructor() {
    this.synth = window.speechSynthesis;
    this.initVoice();
  }

  private initVoice() {
    // Attempt to pick a good English voice
    const voices = this.synth.getVoices();
    this.voice = voices.find(v => v.lang.includes('en-GB') || v.lang.includes('en-US')) || voices[0] || null;
    
    // Voices might load async in some browsers
    if (voices.length === 0) {
      this.synth.onvoiceschanged = () => {
        const asyncVoices = this.synth.getVoices();
        this.voice = asyncVoices.find(v => v.lang.includes('en-GB') || v.lang.includes('en-US')) || asyncVoices[0] || null;
      };
    }
  }

  public speak(text: string) {
    if (!this.synth) return;
    
    // Stop any ongoing speech
    this.synth.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    if (this.voice) {
      utterance.voice = this.voice;
    }
    
    // Academic/calm tone tweaks
    utterance.rate = 0.95; 
    utterance.pitch = 1.0;

    this.synth.speak(utterance);
  }

  public stop() {
    if (this.synth) {
      this.synth.cancel();
    }
  }
}

// Singleton for easy use
export const ttsEngine = typeof window !== "undefined" ? new TTSEngine() : null;
