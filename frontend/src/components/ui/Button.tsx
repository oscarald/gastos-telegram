import type { ButtonHTMLAttributes, ReactNode } from 'react';
import { cn } from '../../utils/cn';

type Variante = 'primario' | 'secundario' | 'peligro' | 'fantasma';
type Tamano = 'sm' | 'md';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variante?: Variante;
  tamano?: Tamano;
  cargando?: boolean;
  icono?: ReactNode;
}

const VARIANTES: Record<Variante, string> = {
  primario: 'bg-emerald-500 text-emerald-950 hover:bg-emerald-400 focus-visible:outline-emerald-400',
  secundario:
    'border border-surface-700 bg-surface-800 text-zinc-100 hover:bg-surface-700 focus-visible:outline-zinc-400',
  peligro: 'bg-red-500/90 text-white hover:bg-red-500 focus-visible:outline-red-400',
  fantasma: 'text-zinc-300 hover:bg-surface-800 hover:text-zinc-100 focus-visible:outline-zinc-400',
};

const TAMANOS: Record<Tamano, string> = {
  sm: 'px-2.5 py-1.5 text-xs',
  md: 'px-3.5 py-2 text-sm',
};

export default function Button({
  variante = 'primario',
  tamano = 'md',
  cargando = false,
  icono,
  className,
  children,
  disabled,
  ...resto
}: ButtonProps) {
  return (
    <button
      type="button"
      disabled={disabled || cargando}
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-xl font-medium transition',
        'focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2',
        'disabled:cursor-not-allowed disabled:opacity-50',
        VARIANTES[variante],
        TAMANOS[tamano],
        className,
      )}
      {...resto}
    >
      {cargando ? <Spinner className="h-4 w-4" /> : icono}
      {children}
    </button>
  );
}

export function Spinner({ className }: { className?: string }) {
  return (
    <svg
      className={cn('animate-spin', className ?? 'h-5 w-5')}
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
      />
    </svg>
  );
}
