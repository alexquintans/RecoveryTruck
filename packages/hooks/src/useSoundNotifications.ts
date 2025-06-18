import { useCallback, useEffect, useRef, useState } from 'react';

interface SoundConfig {
  src: string;
  volume?: number;
  loop?: boolean;
}

interface SoundOptions {
  volume?: number;
  loop?: boolean;
}

interface UseSoundNotificationsOptions {
  sounds: Record<string, SoundConfig>;
  enabled?: boolean;
  defaultVolume?: number;
}

export function useSoundNotifications({
  sounds,
  enabled: initialEnabled = true,
  defaultVolume = 1.0
}: UseSoundNotificationsOptions) {
  const [enabled, setEnabled] = useState(initialEnabled);
  const [volume, setVolume] = useState(defaultVolume);
  const audioRefs = useRef<Record<string, HTMLAudioElement>>({});

  // Inicializar os elementos de áudio
  useEffect(() => {
    // Limpar áudios anteriores
    Object.values(audioRefs.current).forEach(audio => {
      audio.pause();
      audio.remove();
    });
    
    audioRefs.current = {};
    
    // Criar novos elementos de áudio
    Object.entries(sounds).forEach(([key, config]) => {
      const audio = new Audio(config.src);
      audio.volume = config.volume ?? volume;
      audio.loop = config.loop ?? false;
      audio.preload = 'auto';
      audioRefs.current[key] = audio;
    });
    
    // Cleanup
    return () => {
      Object.values(audioRefs.current).forEach(audio => {
        audio.pause();
        audio.remove();
      });
    };
  }, [sounds, volume]);

  // Tocar um som
  const play = useCallback((soundKey: string, options?: SoundOptions) => {
    if (!enabled) return false;
    
    const audio = audioRefs.current[soundKey];
    if (!audio) {
      console.warn(`Som "${soundKey}" não encontrado`);
      return false;
    }
    
    // Aplicar opções
    if (options?.volume !== undefined) {
      audio.volume = options.volume;
    }
    
    if (options?.loop !== undefined) {
      audio.loop = options.loop;
    }
    
    // Reiniciar o áudio se já estiver tocando
    audio.currentTime = 0;
    
    // Tocar
    return audio.play()
      .then(() => true)
      .catch(error => {
        console.error(`Erro ao tocar som "${soundKey}":`, error);
        return false;
      });
  }, [enabled]);

  // Parar um som
  const stop = useCallback((soundKey: string) => {
    const audio = audioRefs.current[soundKey];
    if (!audio) return false;
    
    audio.pause();
    audio.currentTime = 0;
    return true;
  }, []);

  // Parar todos os sons
  const stopAll = useCallback(() => {
    Object.values(audioRefs.current).forEach(audio => {
      audio.pause();
      audio.currentTime = 0;
    });
  }, []);

  // Alternar estado de habilitado/desabilitado
  const toggle = useCallback(() => {
    setEnabled(prev => {
      const newState = !prev;
      
      // Se desabilitado, para todos os sons
      if (!newState) {
        stopAll();
      }
      
      return newState;
    });
  }, [stopAll]);

  return {
    enabled,
    setEnabled,
    volume,
    setVolume,
    play,
    stop,
    stopAll,
    toggle
  };
} 