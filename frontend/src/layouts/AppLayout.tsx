import { useState } from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { cn } from '../utils/cn';
import {
  IconoCategorias,
  IconoCerrar,
  IconoGastos,
  IconoMenu,
  IconoPanel,
  IconoReglas,
  IconoTelegram,
} from '../components/ui/Iconos';

const ENLACES = [
  { to: '/', label: 'Dashboard', Icono: IconoPanel, exacto: true },
  { to: '/gastos', label: 'Gastos', Icono: IconoGastos, exacto: false },
  { to: '/categorias', label: 'Categorias', Icono: IconoCategorias, exacto: false },
  { to: '/reglas', label: 'Reglas', Icono: IconoReglas, exacto: false },
];

const TITULOS: Record<string, string> = {
  '/': 'Dashboard',
  '/gastos': 'Historial de gastos',
  '/categorias': 'Categorias',
  '/reglas': 'Reglas de categorizacion',
};

export default function AppLayout() {
  const [menuAbierto, setMenuAbierto] = useState(false);
  const ubicacion = useLocation();
  const titulo = TITULOS[ubicacion.pathname] ?? 'Control de gastos';

  const enlaces = (
    <nav className="flex flex-col gap-1">
      {ENLACES.map(({ to, label, Icono, exacto }) => (
        <NavLink
          key={to}
          to={to}
          end={exacto}
          onClick={() => setMenuAbierto(false)}
          className={({ isActive }) =>
            cn(
              'flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition',
              isActive
                ? 'bg-emerald-500/15 text-emerald-300 ring-1 ring-inset ring-emerald-500/30'
                : 'text-zinc-400 hover:bg-surface-800 hover:text-zinc-100',
            )
          }
        >
          <Icono className="h-5 w-5" />
          {label}
        </NavLink>
      ))}
    </nav>
  );

  return (
    <div className="min-h-screen bg-surface-950">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 flex-col border-r border-surface-800 bg-surface-900/60 px-4 py-6 lg:flex">
        <div className="mb-8 flex items-center gap-3 px-2">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/15 text-emerald-300">
            <IconoTelegram className="h-5 w-5" />
          </span>
          <div>
            <p className="text-sm font-semibold text-zinc-100">Control de Gastos</p>
            <p className="text-xs text-zinc-500">Self hosted</p>
          </div>
        </div>
        {enlaces}
        <div className="mt-auto rounded-xl border border-surface-800 bg-surface-950/60 p-3 text-xs text-zinc-500">
          Registra desde Telegram:{' '}
          <span className="text-zinc-300">“almuerzo 50 bs”</span>
        </div>
      </aside>

      <header className="sticky top-0 z-20 flex items-center justify-between gap-3 border-b border-surface-800 bg-surface-950/90 px-4 py-3 backdrop-blur lg:hidden">
        <div className="flex items-center gap-2">
          <button
            type="button"
            className="rounded-lg p-2 text-zinc-300 transition hover:bg-surface-800"
            onClick={() => setMenuAbierto((valor) => !valor)}
            aria-label="Abrir menu"
          >
            {menuAbierto ? <IconoCerrar /> : <IconoMenu />}
          </button>
          <span className="text-sm font-semibold text-zinc-100">{titulo}</span>
        </div>
        <span className="rounded-lg bg-emerald-500/15 px-2 py-1 text-xs font-medium text-emerald-300">
          Bs
        </span>
      </header>

      {menuAbierto ? (
        <div className="border-b border-surface-800 bg-surface-900 px-4 py-3 lg:hidden">{enlaces}</div>
      ) : null}

      <main className="px-4 py-6 sm:px-6 lg:ml-64 lg:px-8">
        <div className="mx-auto w-full max-w-7xl">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
