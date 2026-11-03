const formatter = new Intl.NumberFormat('es-BO', {
  style: 'currency',
  currency: 'BOB',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const formatterNumero = new Intl.NumberFormat('es-BO', {
  minimumFractionDigits: 0,
  maximumFractionDigits: 2,
});

export function formatMoneda(valor: number | string | null | undefined): string {
  const numero = typeof valor === 'string' ? Number(valor) : (valor ?? 0);
  return formatter.format(Number.isFinite(numero) ? numero : 0);
}

export function formatNumero(valor: number | null | undefined): string {
  return formatterNumero.format(valor ?? 0);
}

export function formatFecha(iso: string | null | undefined): string {
  if (!iso) return '-';
  const fecha = new Date(iso);
  if (Number.isNaN(fecha.getTime())) return '-';
  return new Intl.DateTimeFormat('es-BO', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(fecha);
}

export function formatFechaCorta(iso: string | null | undefined): string {
  if (!iso) return '-';
  const fecha = new Date(iso);
  if (Number.isNaN(fecha.getTime())) return '-';
  return new Intl.DateTimeFormat('es-BO', {
    day: '2-digit',
    month: 'short',
  }).format(fecha);
}

export const MESES = [
  'Enero',
  'Febrero',
  'Marzo',
  'Abril',
  'Mayo',
  'Junio',
  'Julio',
  'Agosto',
  'Septiembre',
  'Octubre',
  'Noviembre',
  'Diciembre',
];

export function mesActual(): { anio: number; mes: number } {
  const ahora = new Date();
  return { anio: ahora.getFullYear(), mes: ahora.getMonth() + 1 };
}

export function nombreMes(mes: number): string {
  return MESES[mes - 1] ?? '';
}
