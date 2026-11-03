import { ChartOptions, type ChartData } from 'chart.js';
import { Doughnut } from 'react-chartjs-2';
import type { CategoriaDistribucion } from '../../types';
import { formatMoneda } from '../../utils/formato';
import { COLOR_REJILLA, COLOR_TEXTO, COLOR_TOOLTIP } from './chartConfig';

export default function CategoriaDoughnut({ datos }: { datos: CategoriaDistribucion[] }) {
  if (datos.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center text-sm text-zinc-500">
        Sin gastos registrados en el periodo
      </div>
    );
  }

  const chartData: ChartData<'doughnut'> = {
    labels: datos.map((item) => item.nombre),
    datasets: [
      {
        data: datos.map((item) => item.monto),
        backgroundColor: datos.map((item) => item.color),
        borderColor: '#101013',
        borderWidth: 2,
        hoverOffset: 6,
      },
    ],
  };

  const options: ChartOptions<'doughnut'> = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '62%',
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: COLOR_TEXTO,
          boxWidth: 10,
          boxHeight: 10,
          padding: 12,
          font: { size: 11 },
        },
      },
      tooltip: {
        backgroundColor: COLOR_TOOLTIP,
        borderColor: '#2a2a32',
        borderWidth: 1,
        padding: 12,
        callbacks: {
          label: (contexto) => {
            const item = datos[contexto.dataIndex];
            const valor = contexto.parsed as number;
            return ` ${formatMoneda(valor)} (${item?.porcentaje ?? 0}%)`;
          },
        },
      },
    },
  };

  return (
    <div className="h-64">
      <Doughnut data={chartData} options={options} />
    </div>
  );
}

export { COLOR_REJILLA };
