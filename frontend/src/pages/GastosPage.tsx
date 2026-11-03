import { useState } from 'react';
import GastosFiltros, { type EstadoFiltros } from '../components/gastos/GastosFiltros';
import GastosTable from '../components/gastos/GastosTable';
import GastoFormModal from '../components/gastos/GastoFormModal';
import Button from '../components/ui/Button';
import { Alerta, Card } from '../components/ui/Card';
import { IconoFlecha, IconoMas } from '../components/ui/Iconos';
import { Cargando } from '../components/ui/Modal';
import { useAsync } from '../hooks/useAsync';
import { categoriasService, gastosService, sistemaService } from '../services';
import type { Gasto, GastoInput } from '../types';
import { mesActual } from '../utils/formato';

const LIMITE = 20;

export default function GastosPage() {
  const inicial = mesActual();
  const [filtros, setFiltros] = useState<EstadoFiltros>({
    mes: inicial.mes,
    anio: inicial.anio,
    categoria_id: null,
    metodo_pago: null,
    q: '',
  });
  const [pagina, setPagina] = useState(1);
  const [modalAbierto, setModalAbierto] = useState(false);
  const [gastoEditando, setGastoEditando] = useState<Gasto | null>(null);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [exportando, setExportando] = useState(false);

  const { datos: categorias } = useAsync(
    async () => (await categoriasService.listar()).data,
    [],
  );
  const { datos: metodosPago } = useAsync(
    async () => (await sistemaService.metodosPago()).data,
    [],
  );
  const { datos: listado, cargando, error: errorListado, recargar } = useAsync(
    async () =>
      (
        await gastosService.listar({
          mes: filtros.mes,
          anio: filtros.anio,
          categoria_id: filtros.categoria_id,
          metodo_pago: filtros.metodo_pago,
          q: filtros.q,
          pagina,
          limite: LIMITE,
        })
      ).data,
    [filtros.mes, filtros.anio, filtros.categoria_id, filtros.metodo_pago, filtros.q, pagina],
  );

  const cambiarFiltros = (nuevos: EstadoFiltros) => {
    setFiltros(nuevos);
    setPagina(1);
  };

  const guardar = async (payload: GastoInput) => {
    setError(null);
    try {
      if (gastoEditando) {
        await gastosService.actualizar(gastoEditando.id, payload);
        setMensaje('Gasto actualizado correctamente');
      } else {
        await gastosService.crear(payload);
        setMensaje('Gasto registrado correctamente');
      }
      recargar();
    } catch (fallo) {
      setError(fallo instanceof Error ? fallo.message : 'No se pudo guardar el gasto');
      throw fallo;
    }
  };

  const eliminar = async (gasto: Gasto) => {
    const confirmado = window.confirm(
      `Eliminar "${gasto.descripcion}" por ${gasto.monto.toFixed(2)}? Esta accion no se puede deshacer.`,
    );
    if (!confirmado) return;
    try {
      await gastosService.eliminar(gasto.id);
      setMensaje('Gasto eliminado');
      recargar();
    } catch (fallo) {
      setError(fallo instanceof Error ? fallo.message : 'No se pudo eliminar el gasto');
    }
  };

  const exportar = async () => {
    setExportando(true);
    setError(null);
    try {
      await gastosService.exportarCsv({
        mes: filtros.mes,
        anio: filtros.anio,
        categoria_id: filtros.categoria_id,
        metodo_pago: filtros.metodo_pago,
        q: filtros.q,
      });
      setMensaje('CSV exportado');
    } catch (fallo) {
      setError(fallo instanceof Error ? fallo.message : 'No se pudo exportar el CSV');
    } finally {
      setExportando(false);
    }
  };

  const abrirNuevo = () => {
    setGastoEditando(null);
    setModalAbierto(true);
  };

  const abrirEdicion = (gasto: Gasto) => {
    setGastoEditando(gasto);
    setModalAbierto(true);
  };

  const hayFiltros =
    filtros.categoria_id !== null || filtros.metodo_pago !== null || filtros.q.trim() !== '';

  return (
    <div className="space-y-5">
      <header className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-xl font-semibold text-zinc-50">Historial de gastos</h1>
          <p className="text-sm text-zinc-500">
            {listado ? `${listado.total} gasto(s) en el periodo` : 'Cargando...'}
          </p>
        </div>
        <Button onClick={abrirNuevo} icono={<IconoMas />}>
          Nuevo gasto
        </Button>
      </header>

      {error ? <Alerta mensaje={error} onCerrar={() => setError(null)} /> : null}
      {mensaje ? (
        <Alerta mensaje={mensaje} tipo="exito" onCerrar={() => setMensaje(null)} />
      ) : null}
      {errorListado ? <Alerta mensaje={errorListado} /> : null}

      <GastosFiltros
        filtros={filtros}
        categorias={categorias ?? []}
        metodosPago={metodosPago ?? []}
        onCambio={cambiarFiltros}
        onLimpiar={() =>
          cambiarFiltros({
            mes: filtros.mes,
            anio: filtros.anio,
            categoria_id: null,
            metodo_pago: null,
            q: '',
          })
        }
        onExportar={exportar}
        exportando={exportando}
      />

      <Card>
        {cargando && !listado ? (
          <Cargando texto="Cargando gastos..." />
        ) : (
          <>
            <GastosTable
              gastos={listado?.items ?? []}
              onEditar={abrirEdicion}
              onEliminar={eliminar}
              onBorrarFiltros={() =>
                cambiarFiltros({
                  mes: filtros.mes,
                  anio: filtros.anio,
                  categoria_id: null,
                  metodo_pago: null,
                  q: '',
                })
              }
              hayFiltros={hayFiltros}
            />

            {listado && listado.paginas > 1 ? (
              <div className="mt-4 flex items-center justify-between border-t border-surface-800 pt-4">
                <p className="text-xs text-zinc-500">
                  Pagina {listado.pagina} de {listado.paginas}
                </p>
                <div className="flex gap-2">
                  <Button
                    variante="secundario"
                    tamano="sm"
                    disabled={listado.pagina <= 1}
                    onClick={() => setPagina((valor) => Math.max(1, valor - 1))}
                    icono={<IconoFlecha className="h-4 w-4 rotate-180" />}
                  >
                    Anterior
                  </Button>
                  <Button
                    variante="secundario"
                    tamano="sm"
                    disabled={listado.pagina >= listado.paginas}
                    onClick={() => setPagina((valor) => Math.min(listado.paginas, valor + 1))}
                    icono={<IconoFlecha className="h-4 w-4" />}
                  >
                    Siguiente
                  </Button>
                </div>
              </div>
            ) : null}
          </>
        )}
      </Card>

      {modalAbierto ? (
        <GastoFormModal
          gasto={gastoEditando}
          categorias={categorias ?? []}
          onCerrar={() => setModalAbierto(false)}
          onGuardar={guardar}
        />
      ) : null}
    </div>
  );
}
