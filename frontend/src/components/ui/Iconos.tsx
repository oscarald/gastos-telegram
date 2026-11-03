interface IconoProps {
  className?: string;
}

const base = 'h-5 w-5';

export function IconoPanel({ className }: IconoProps) {
  return (
    <svg className={className ?? base} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7">
      <rect x="3" y="3" width="7" height="9" rx="1.5" />
      <rect x="14" y="3" width="7" height="5" rx="1.5" />
      <rect x="14" y="12" width="7" height="9" rx="1.5" />
      <rect x="3" y="16" width="7" height="5" rx="1.5" />
    </svg>
  );
}

export function IconoGastos({ className }: IconoProps) {
  return (
    <svg className={className ?? base} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7">
      <path d="M6 3h12v18l-2-1.5L14 21l-2-1.5L10 21l-2-1.5L6 21V3z" strokeLinejoin="round" />
      <path d="M9 8h6M9 12h6" strokeLinecap="round" />
    </svg>
  );
}

export function IconoCategorias({ className }: IconoProps) {
  return (
    <svg className={className ?? base} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7">
      <path d="M20.6 13.4l-7.2 7.2a2 2 0 01-2.8 0l-7.2-7.2A2 2 0 013 12V5a2 2 0 012-2h7a2 2 0 011.4.6l7.2 7.2a2 2 0 010 2.6z" strokeLinejoin="round" />
      <circle cx="7.5" cy="7.5" r="1.2" fill="currentColor" stroke="none" />
    </svg>
  );
}

export function IconoReglas({ className }: IconoProps) {
  return (
    <svg className={className ?? base} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7">
      <path d="M3 5h18l-7 8v6l-4 2v-8L3 5z" strokeLinejoin="round" />
    </svg>
  );
}

export function IconoMas({ className }: IconoProps) {
  return (
    <svg className={className ?? base} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M12 5v14M5 12h14" strokeLinecap="round" />
    </svg>
  );
}

export function IconoEditar({ className }: IconoProps) {
  return (
    <svg className={className ?? 'h-4 w-4'} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M4 20h4L19 9a2.8 2.8 0 10-4-4L4 16v4z" strokeLinejoin="round" />
    </svg>
  );
}

export function IconoBorrar({ className }: IconoProps) {
  return (
    <svg className={className ?? 'h-4 w-4'} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M4 7h16M10 11v6M14 11v6" strokeLinecap="round" />
      <path d="M6 7l1 13h10l1-13M9 7V4h6v3" strokeLinejoin="round" />
    </svg>
  );
}

export function IconoBuscar({ className }: IconoProps) {
  return (
    <svg className={className ?? 'h-4 w-4'} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9">
      <circle cx="11" cy="11" r="6.5" />
      <path d="M16 16l4.5 4.5" strokeLinecap="round" />
    </svg>
  );
}

export function IconoExportar({ className }: IconoProps) {
  return (
    <svg className={className ?? 'h-4 w-4'} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M12 4v11M8 11l4 4 4-4" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M5 18v1a2 2 0 002 2h10a2 2 0 002-2v-1" strokeLinecap="round" />
    </svg>
  );
}

export function IconoMenu({ className }: IconoProps) {
  return (
    <svg className={className ?? base} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9">
      <path d="M4 7h16M4 12h16M4 17h16" strokeLinecap="round" />
    </svg>
  );
}

export function IconoCerrar({ className }: IconoProps) {
  return (
    <svg className={className ?? base} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9">
      <path d="M6 6l12 12M18 6L6 18" strokeLinecap="round" />
    </svg>
  );
}

export function IconoTelegram({ className }: IconoProps) {
  return (
    <svg className={className ?? base} viewBox="0 0 24 24" fill="currentColor">
      <path d="M21.7 4.3L2.9 11.5c-.9.35-.9 1.6 0 1.95l4.7 1.55 1.8 5.5c.25.75 1.2.95 1.75.37l2.6-2.85 4.7 3.4c.65.45 1.55.1 1.75-.65l3.3-14.3c.2-.85-.6-1.6-1.4-1.4zM9.5 14.2l8.2-5.7-6.6 6.9-.2 3-1.4-4.2z" />
    </svg>
  );
}

export function IconoFlecha({ className }: IconoProps) {
  return (
    <svg className={className ?? 'h-4 w-4'} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9">
      <path d="M9 6l6 6-6 6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
