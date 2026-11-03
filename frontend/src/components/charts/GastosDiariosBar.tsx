import { ChartOptions, type ChartData } from 'chart.js';
import { Bar } from 'react-chartjs-2';
import type { GastoPorDia } from '../../types';
import { formatMoneda } from '../../utils/formato';
import { COLOR_REJILLA, COLOR_TEXTO, COLOR_TOOLTIP } from './chartConfig';

export default function GastosDiariosBar({ datos }: { datos: GastoPorDia[] }) {
  const chartData: ChartData<'bar'> = {
    labels: datos.map((item) => String(item.dia)),
    datasets: [
      {
        label: 'Gasto',
        data: datos.map((item) => item.monto),
        backgroundColor: 'rgba(16, 185, 129, 0.75)',
        hoverBackgroundColor: '#10b981',
        borderRadius: 6,
        maxBarThickness: 26,
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
          title: (items) => `Dia ${items[0]?.label ?? ''}`,
          label: (contexto) => ` ${formatMoneda(contexto.parsed.y as number)}`,
        },
      },
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { color: COLOR_TEXTO, font: { size: 10 }, maxRotation: 0, autoSkipPadding: 8 },
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

  return (
    <div className="h-64">
      <Bar data={chartData} options={options} />
    </div>
  );
}
