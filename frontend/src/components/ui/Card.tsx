import type { ReactNode } from 'react';
import { cn } from '../../utils/cn';

export function Card({
  children,
  className,
  title,
  subtitle,
  acciones,
}: {
  children: ReactNode;
  className?: string;
  title?: string;
  subtitle?: string;
  acciones?: ReactNode;
}) {
  return (
    <section className={cn('panel p-4 sm:p-5', className)}>
      {(title || acciones) && (
        <header className="mb-4 flex items-start justify-between gap-3">
          <div>
            {title ? <h2 className="text-sm font-semibold text-zinc-100">{title}</h2> : null}
            {subtitle ? <p className="mt-0.5 text-xs text-zinc-500">{subtitle}</p> : null}
          </div>
          {acciones}
        </header>
      )}
      {children}
    </section>
  );
}

export function Badge({
  children,
  color,
  className,
}: {
  children: ReactNode;
  color?: string | null;
  className?: string;
}) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium',
        !color && 'bg-surface-800 text-zinc-300',
        className,
      )}
      style={color ? { backgroundColor: `${color}22`, color } : undefined}
    >
      {color ? (
        <span className="h-2 w-2 rounded-full" style={{ backgroundColor: color }} aria-hidden="true" />
      ) : null}
      {children}
    </span>
  );
}

export function EstadoVacio({ titulo, descripcion }: { titulo: string; descripcion?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 rounded-xl border border-dashed border-surface-700 px-6 py-12 text-center">
      <p className="text-sm font-medium text-zinc-300">{titulo}</p>
      {descripcion ? <p className="max-w-sm text-xs text-zinc-500">{descripcion}</p> : null}
    </div>
  );
}

export function Alerta({
  mensaje,
  tipo = 'error',
  onCerrar,
}: {
  mensaje: string | null;
  tipo?: 'error' | 'exito' | 'info';
  onCerrar?: () => void;
}) {
  if (!mensaje) return null;
  const estilos = {
    error: 'border-red-500/40 bg-red-500/10 text-red-200',
    exito: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-200',
    info: 'border-sky-500/40 bg-sky-500/10 text-sky-200',
  };
  return (
    <div
      role="alert"
      className={cn(
        'flex items-start justify-between gap-3 rounded-xl border px-3 py-2 text-sm',
        estilos[tipo],
      )}
    >
      <span>{mensaje}</span>
      {onCerrar ? (
        <button type="button" onClick={onCerrar} className="text-xs uppercase opacity-70 hover:opacity-100">
          cerrar
        </button>
      ) : null}
    </div>
  );
}
