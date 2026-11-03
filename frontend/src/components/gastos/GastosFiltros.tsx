import { useEffect, useState } from 'react';
import type { Categoria } from '../../types';
import { Select, Input } from '../ui/Field';
import { IconoBuscar, IconoExportar } from '../ui/Iconos';
import Button from '../ui/Button';
import { MESES, mesActual } from '../../utils/formato';
import { useDebounce } from '../../hooks/useDebounce';

export interface EstadoFiltros {
  mes: number;
  anio: number;
  categoria_id: number | null;
  metodo_pago: string | null;
  q: string;
}

interface Props {
  filtros: EstadoFiltros;
  categorias: Categoria[];
  metodosPago: string[];
  onCambio: (filtros: EstadoFiltros) => void;
  onLimpiar: () => void;
  onExportar: () => void;
  exportando: boolean;
}

const METODOS_FALLBACK = [
  'Efectivo',
  'Tarjeta de débito',
  'Tarjeta de crédito',
  'QR',
  'Transferencia',
  'Otros',
];

export default function GastosFiltros({
  filtros,
  categorias,
  metodosPago,
  onCambio,
  onLimpiar,
  onExportar,
  exportando,
}: Props) {
  const [busqueda, setBusqueda] = useState(filtros.q);
  const busquedaConRetraso = useDebounce(busqueda, 400);
  const actual = mesActual();
  const anios = Array.from({ length: 5 }, (_, indice) => actual.anio + 2 - indice);
  const metodos = metodosPago.length > 0 ? metodosPago : METODOS_FALLBACK;

  const aplicar = (cambios: Partial<EstadoFiltros>) => {
    onCambio({ ...filtros, ...cambios });
  };

  useEffect(() => {
    if (busquedaConRetraso !== filtros.q) {
      aplicar({ q: busquedaConRetraso });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [busquedaConRetraso]);

  return (
    <div className="panel p-4">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-5">
        <div className="relative lg:col-span-2">
          <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500">
            <IconoBuscar />
          </span>
          <Input
            className="pl-9"
            placeholder="Buscar por descripcion..."
            value={busqueda}
            onChange={(evento) => setBusqueda(evento.target.value)}
            onKeyDown={(evento) => {
              if (evento.key === 'Enter') aplicar({ q: busqueda });
            }}
            onBlur={() => aplicar({ q: busqueda })}
          />
        </div>

        <Select
          value={filtros.mes}
          onChange={(evento) => aplicar({ mes: Number(evento.target.value) })}
          aria-label="Mes"
        >
          {MESES.map((nombre, indice) => (
            <option key={nombre} value={indice + 1}>
              {nombre}
            </option>
          ))}
        </Select>

        <Select
          value={filtros.anio}
          onChange={(evento) => aplicar({ anio: Number(evento.target.value) })}
          aria-label="Anio"
        >
          {anios.map((valor) => (
            <option key={valor} value={valor}>
              {valor}
            </option>
          ))}
        </Select>

        <Select
          value={filtros.categoria_id ?? ''}
          onChange={(evento) =>
            aplicar({ categoria_id: evento.target.value ? Number(evento.target.value) : null })
          }
          aria-label="Categoria"
        >
          <option value="">Todas las categorias</option>
          {categorias.map((categoria) => (
            <option key={categoria.id} value={categoria.id}>
              {categoria.nombre}
            </option>
          ))}
        </Select>

        <Select
          value={filtros.metodo_pago ?? ''}
          onChange={(evento) => aplicar({ metodo_pago: evento.target.value || null })}
          aria-label="Metodo de pago"
        >
          <option value="">Todos los metodos de pago</option>
          {metodos.map((metodo) => (
            <option key={metodo} value={metodo}>
              {metodo}
            </option>
          ))}
        </Select>

        <div className="flex gap-2 lg:col-span-2">
          <Button variante="secundario" onClick={onLimpiar} className="flex-1">
            Limpiar
          </Button>
          <Button
            variante="secundario"
            onClick={onExportar}
            cargando={exportando}
            icono={<IconoExportar />}
            className="flex-1"
          >
            Exportar CSV
          </Button>
        </div>
      </div>
    </div>
  );
}
