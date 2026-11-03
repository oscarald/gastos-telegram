import { ChartOptions, type ChartData } from 'chart.js';
import { Bar } from 'react-chartjs-2';
import { COLOR_REJILLA, COLOR_TEXTO, COLOR_TOOLTIP } from './chartConfig';
import { formatMoneda, nombreMes } from '../../utils/formato';

interface Props {
  mesActual: number;
  anioActual: number;
  totalActual: number;
  totalAnterior: number;
  variacion: number | null;
}

export default function ComparacionMensual({
  mesActual,
  anioActual,
  totalActual,
  totalAnterior,
  variacion,
}: Props) {
  const anioAnterior = mesActual === 1 ? anioActual - 1 : anioActual;
  const mesAnterior = mesActual === 1 ? 12 : mesActual - 1;

  const chartData: ChartData<'bar'> = {
    labels: [`${nombreMes(mesAnterior)} ${anioAnterior}`, `${nombreMes(mesActual)} ${anioActual}`],
    datasets: [
      {
        label: 'Total',
        data: [totalAnterior, totalActual],
        backgroundColor: ['rgba(113, 113, 122, 0.65)', 'rgba(16, 185, 129, 0.8)'],
        hoverBackgroundColor: ['#71717a', '#10b981'],
        borderRadius: 8,
        maxBarThickness: 70,
      },
    ],
  };

  const options: ChartOptions<'bar'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: COLOR_TOOLTIP,
        borderColor: '#2a2a32',
        borderWidth: 1,
        padding: 12,
        callbacks: {
          label: (contexto) => ` ${formatMoneda(contexto.parsed.y as number)}`,
        },
      },
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { color: COLOR_TEXTO, font: { size: 11 } },
        border: { color: COLOR_REJILLA },
      },
      y: {
        beginAtZero: true,
        grid: { color: COLOR_REJILLA },
        ticks: {
          color: COLOR_TEXTO,
          font: { size: 10 },
          callback: (valor) => Number(valor).toLocaleString('es-BO'),
        },
        border: { display: false },
      },
    },
  };

  const subio = variacion !== null && variacion > 0;
  const textoVariacion =
    variacion === null
      ? 'Sin datos del mes anterior'
      : `${subio ? '+' : ''}${variacion}% respecto al mes anterior`;

  return (
    <div className="space-y-3">
      <div className="h-52">
        <Bar data={chartData} options={options} />
      </div>
      <p className="text-center text-xs text-zinc-500">{textoVariacion}</p>
    </div>
  );
}
