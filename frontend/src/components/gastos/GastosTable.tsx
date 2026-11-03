import type { Gasto } from '../../types';
import { formatFecha, formatMoneda } from '../../utils/formato';
import { Badge } from '../ui/Card';
import { IconoBorrar, IconoEditar } from '../ui/Iconos';

interface Props {
  gastos: Gasto[];
  onEditar: (gasto: Gasto) => void;
  onEliminar: (gasto: Gasto) => void;
  onBorrarFiltros: () => void;
  hayFiltros: boolean;
}

export default function GastosTable({
  gastos,
  onEditar,
  onEliminar,
  onBorrarFiltros,
  hayFiltros,
}: Props) {
  if (gastos.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-surface-700 px-6 py-12 text-center">
        <p className="text-sm font-medium text-zinc-300">No hay gastos para mostrar</p>
        <p className="mt-1 text-xs text-zinc-500">
          {hayFiltros
            ? 'Prueba a cambiar los filtros o a limpiarlos.'
            : 'Registra un gasto desde el bot de Telegram o desde el boton "Nuevo gasto".'}
        </p>
        {hayFiltros ? (
          <button
            type="button"
            onClick={onBorrarFiltros}
            className="mt-3 text-xs font-medium text-emerald-400 hover:text-emerald-300"
          >
            Limpiar filtros
          </button>
        ) : null}
      </div>
    );
  }

  return (
    <>
      <div className="hidden overflow-x-auto lg:block">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-surface-800 text-xs uppercase tracking-wide text-zinc-500">
              <th className="py-3 pr-4 font-medium">Fecha</th>
              <th className="py-3 pr-4 font-medium">Descripcion</th>
              <th className="py-3 pr-4 font-medium">Categoria</th>
              <th className="py-3 pr-4 font-medium">Pago</th>
              <th className="py-3 pr-4 font-medium">Origen</th>
              <th className="py-3 pr-4 text-right font-medium">Monto</th>
              <th className="py-3 text-right font-medium">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-800/70">
            {gastos.map((gasto) => (
              <tr key={gasto.id} className="transition hover:bg-surface-800/40">
                <td className="whitespace-nowrap py-3 pr-4 text-zinc-400">{formatFecha(gasto.fecha)}</td>
                <td className="py-3 pr-4 text-zinc-100">{gasto.descripcion}</td>
                <td className="py-3 pr-4">
                  <Badge color={gasto.categoria_color}>{gasto.categoria}</Badge>
                </td>
                <td className="py-3 pr-4 text-zinc-400">{gasto.metodo_pago ?? '-'}</td>
                <td className="py-3 pr-4">
                  <span
                    className={
                      gasto.origen === 'telegram'
                        ? 'text-xs font-medium text-sky-400'
                        : 'text-xs font-medium text-zinc-400'
                    }
                  >
                    {gasto.origen}
                  </span>
                </td>
                <td className="whitespace-nowrap py-3 pr-4 text-right font-medium text-zinc-50">
                  {formatMoneda(gasto.monto)}
                </td>
                <td className="py-3">
                  <div className="flex justify-end gap-1">
                    <button
                      type="button"
                      onClick={() => onEditar(gasto)}
                      className="rounded-lg p-2 text-zinc-400 transition hover:bg-surface-700 hover:text-zinc-100"
                      aria-label={`Editar ${gasto.descripcion}`}
                    >
                      <IconoEditar />
                    </button>
                    <button
                      type="button"
                      onClick={() => onEliminar(gasto)}
                      className="rounded-lg p-2 text-zinc-400 transition hover:bg-red-500/20 hover:text-red-300"
                      aria-label={`Eliminar ${gasto.descripcion}`}
                    >
                      <IconoBorrar />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <ul className="space-y-3 lg:hidden">
        {gastos.map((gasto) => (
          <li key={gasto.id} className="rounded-xl border border-surface-800 bg-surface-900/60 p-4">
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <p className="truncate text-sm font-medium text-zinc-100">{gasto.descripcion}</p>
                <p className="mt-0.5 text-xs text-zinc-500">{formatFecha(gasto.fecha)}</p>
              </div>
              <p className="whitespace-nowrap text-sm font-semibold text-zinc-50">
                {formatMoneda(gasto.monto)}
              </p>
            </div>
            <div className="mt-3 flex flex-wrap items-center gap-2">
              <Badge color={gasto.categoria_color}>{gasto.categoria}</Badge>
              {gasto.metodo_pago ? (
                <span className="text-xs text-zinc-400">{gasto.metodo_pago}</span>
              ) : null}
              <span className="text-xs text-zinc-500">· {gasto.origen}</span>
              <div className="ml-auto flex gap-1">
                <button
                  type="button"
                  onClick={() => onEditar(gasto)}
                  className="rounded-lg p-2 text-zinc-400 transition hover:bg-surface-700 hover:text-zinc-100"
                  aria-label={`Editar ${gasto.descripcion}`}
                >
                  <IconoEditar />
                </button>
                <button
                  type="button"
                  onClick={() => onEliminar(gasto)}
                  className="rounded-lg p-2 text-zinc-400 transition hover:bg-red-500/20 hover:text-red-300"
                  aria-label={`Eliminar ${gasto.descripcion}`}
                >
                  <IconoBorrar />
                </button>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </>
  );
}
