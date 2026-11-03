import { useEffect, type ReactNode } from 'react';
import { cn } from '../../utils/cn';
import { Spinner } from './Button';

interface ModalProps {
  abierto: boolean;
  titulo: string;
  descripcion?: string;
  onCerrar: () => void;
  children: ReactNode;
  pie?: ReactNode;
  ancho?: 'md' | 'lg';
}

export default function Modal({
  abierto,
  titulo,
  descripcion,
  onCerrar,
  children,
  pie,
  ancho = 'md',
}: ModalProps) {
  useEffect(() => {
    if (!abierto) return undefined;
    const onTecla = (evento: KeyboardEvent) => {
      if (evento.key === 'Escape') onCerrar();
    };
    document.addEventListener('keydown', onTecla);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', onTecla);
      document.body.style.overflow = '';
    };
  }, [abierto, onCerrar]);

  if (!abierto) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/70 p-0 backdrop-blur-sm sm:items-center sm:p-4">
      <button
        type="button"
        aria-label="Cerrar"
        className="absolute inset-0 cursor-default"
        onClick={onCerrar}
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-label={titulo}
        className={cn(
          'panel relative z-10 max-h-[92vh] w-full overflow-y-auto rounded-b-none sm:rounded-2xl',
          ancho === 'lg' ? 'sm:max-w-3xl' : 'sm:max-w-lg',
        )}
      >
        <header className="flex items-start justify-between gap-4 border-b border-surface-800 px-5 py-4">
          <div>
            <h2 className="text-base font-semibold text-zinc-100">{titulo}</h2>
            {descripcion ? <p className="mt-1 text-xs text-zinc-500">{descripcion}</p> : null}
          </div>
          <button
            type="button"
            onClick={onCerrar}
            className="rounded-lg p-1 text-zinc-500 transition hover:bg-surface-800 hover:text-zinc-200"
            aria-label="Cerrar"
          >
            <svg viewBox="0 0 20 20" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.8">
              <path d="M5 5l10 10M15 5L5 15" strokeLinecap="round" />
            </svg>
          </button>
        </header>
        <div className="px-5 py-4">{children}</div>
        {pie ? <footer className="flex justify-end gap-2 border-t border-surface-800 px-5 py-4">{pie}</footer> : null}
      </div>
    </div>
  );
}

export function Cargando({ texto = 'Cargando...' }: { texto?: string }) {
  return (
    <div className="flex items-center justify-center gap-3 py-12 text-sm text-zinc-500">
      <Spinner className="h-5 w-5" />
      {texto}
    </div>
  );
}
