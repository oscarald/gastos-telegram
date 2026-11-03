import { useState } from 'react';
import MesAnoSelector from '../components/MesAnoSelector';
import CategoriaDoughnut from '../components/charts/CategoriaDoughnut';
import ComparacionMensual from '../components/charts/ComparacionMensual';
import GastosDiariosBar from '../components/charts/GastosDiariosBar';
import { Alerta, Card } from '../components/ui/Card';
import { Cargando } from '../components/ui/Modal';
import { useAsync } from '../hooks/useAsync';
import { dashboardService } from '../services';
import { formatMoneda, formatNumero, mesActual, nombreMes } from '../utils/formato';

function Tarjeta({
  titulo,
  valor,
  detalle,
  acento,
}: {
  titulo: string;
  valor: string;
  detalle?: string;
  acento?: string;
}) {
  return (
    <div className="panel relative overflow-hidden p-5">
      {acento ? (
        <span
          className="absolute inset-x-0 top-0 h-1"
          style={{ backgroundColor: acento }}
          aria-hidden="true"
        />
      ) : null}
      <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">{titulo}</p>
      <p className="mt-2 text-2xl font-semibold text-zinc-50">{valor}</p>
      {detalle ? <p className="mt-1 text-xs text-zinc-500">{detalle}</p> : null}
    </div>
  );
}

export default function DashboardPage() {
  const inicial = mesActual();
  const [anio, setAnio] = useState(inicial.anio);
  const [mes, setMes] = useState(inicial.mes);

  const { datos, cargando, error } = useAsync(
    async () => (await dashboardService.resumen({ anio, mes })).data,
    [anio, mes],
  );

  const comparacion = datos?.comparacion_mes_anterior;
  const variacion = comparacion?.variacion_porcentaje ?? null;

  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-xl font-semibold text-zinc-50">Resumen de gastos</h1>
          <p className="text-sm text-zinc-500">
            {nombreMes(mes)} {anio} · zona horaria America/La_Paz
          </p>
        </div>
        <MesAnoSelector
          anio={anio}
          mes={mes}
          onAnio={setAnio}
          onMes={(valor) => {
            setMes(valor);
            setAnio(anio);
          }}
        />
      </header>

      {error ? <Alerta mensaje={error} /> : null}

      {cargando && !datos ? <Cargando texto="Calculando estadisticas..." /> : null}

      {datos ? (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <Tarjeta
              titulo="Total gastado"
              valor={formatMoneda(datos.total_gastado)}
              detalle={`${datos.cantidad_transacciones} transacciones`}
            />
            <Tarjeta
              titulo="Transacciones"
              valor={formatNumero(datos.cantidad_transacciones)}
              detalle="En el periodo seleccionado"
            />
            <Tarjeta
              titulo="Promedio por gasto"
              valor={formatMoneda(datos.promedio_por_transaccion)}
              detalle="Total / transacciones"
            />
            <Tarjeta
              titulo="Categoria principal"
              valor={datos.categoria_mayor_gasto?.nombre ?? 'Sin datos'}
              detalle={
                datos.categoria_mayor_gasto
                  ? `${formatMoneda(datos.categoria_mayor_gasto.monto)} · ${datos.categoria_mayor_gasto.porcentaje}%`
                  : 'Aun no hay gastos'
              }
              acento={datos.categoria_mayor_gasto?.color}
            />
          </div>

          <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
            <Card
              title="Distribucion por categoria"
              subtitle="Participacion de cada categoria en el total"
              className="xl:col-span-1"
            >
              <CategoriaDoughnut datos={datos.distribucion_por_categoria} />
            </Card>

            <Card
              title="Gastos por dia"
              subtitle="Evolucion diaria dentro del mes"
              className="xl:col-span-2"
            >
              <GastosDiariosBar datos={datos.gastos_por_dia} />
            </Card>
          </div>

          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <Card title="Comparacion mensual" subtitle="Mes actual frente al mes anterior">
              <ComparacionMensual
                mesActual={datos.mes}
                anioActual={datos.anio}
                totalActual={comparacion?.total_actual ?? datos.total_gastado}
                totalAnterior={comparacion?.total_anterior ?? 0}
                variacion={variacion}
              />
            </Card>

            <Card title="Ranking de categorias" subtitle="Ordenado por monto gastado">
              {datos.distribucion_por_categoria.length === 0 ? (
                <p className="py-8 text-center text-sm text-zinc-500">Sin gastos en el periodo</p>
              ) : (
                <ul className="space-y-3">
                  {datos.distribucion_por_categoria.map((item) => (
                    <li key={item.categoria_id} className="flex items-center gap-3">
                      <span
                        className="h-3 w-3 shrink-0 rounded-full"
                        style={{ backgroundColor: item.color }}
                        aria-hidden="true"
                      />
                      <span className="flex-1 truncate text-sm text-zinc-300">{item.nombre}</span>
                      <span className="text-sm font-medium text-zinc-100">
                        {formatMoneda(item.monto)}
                      </span>
                      <span className="w-14 text-right text-xs text-zinc-500">
                        {item.porcentaje}%
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </Card>
          </div>
        </>
      ) : null}
    </div>
  );
}
