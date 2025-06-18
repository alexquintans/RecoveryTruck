import { useRef, useCallback } from 'react';

interface SoundOptions {
  volume?: number;
  loop?: boolean;
}

interface SoundNotifications {
  play: (soundName: string) => void;
  stop: (soundName: string) => void;
  stopAll: () => void;
  setVolume: (volume: number) => void;
}

const SOUNDS = {
  success: '/sounds/success.mp3',
  error: '/sounds/error.mp3',
  beep: '/sounds/beep.mp3',
  payment: '/sounds/payment.mp3',
  ticket: '/sounds/ticket.mp3',
  call: '/sounds/call.mp3',
};

export function useSoundNotifications(
  initialVolume = 0.5,
  enabled = true
): SoundNotifications {
  const audioRefs = useRef<Record<string, HTMLAudioElement>>({});
  const volumeRef = useRef<number>(initialVolume);

  // Função para carregar um som se ainda não estiver carregado
  const loadSound = useCallback((soundName: string): HTMLAudioElement => {
    if (!audioRefs.current[soundName]) {
      const soundPath = SOUNDS[soundName as keyof typeof SOUNDS] || soundName;
      const audio = new Audio(soundPath);
      audio.volume = volumeRef.current;
      audioRefs.current[soundName] = audio;
    }
    return audioRefs.current[soundName];
  }, []);

  // Função para reproduzir um som
  const play = useCallback((soundName: string, options: SoundOptions = {}) => {
    if (!enabled) return;

    try {
      const audio = loadSound(soundName);
      
      // Configurar opções
      if (options.volume !== undefined) {
        audio.volume = options.volume;
      } else {
        audio.volume = volumeRef.current;
      }
      
      audio.loop = options.loop || false;
      
      // Reiniciar e reproduzir
      audio.currentTime = 0;
      audio.play().catch(error => {
        console.error(`Erro ao reproduzir som ${soundName}:`, error);
      });
    } catch (error) {
      console.error(`Erro ao carregar som ${soundName}:`, error);
    }
  }, [enabled, loadSound]);

  // Função para parar um som específico
  const stop = useCallback((soundName: string) => {
    const audio = audioRefs.current[soundName];
    if (audio) {
      audio.pause();
      audio.currentTime = 0;
    }
  }, []);

  // Função para parar todos os sons
  const stopAll = useCallback(() => {
    Object.values(audioRefs.current).forEach(audio => {
      audio.pause();
      audio.currentTime = 0;
    });
  }, []);

  // Função para ajustar o volume de todos os sons
  const setVolume = useCallback((volume: number) => {
    volumeRef.current = Math.max(0, Math.min(1, volume));
    Object.values(audioRefs.current).forEach(audio => {
      audio.volume = volumeRef.current;
    });
  }, []);

  return {
    play,
    stop,
    stopAll,
    setVolume,
  };
} 