export interface ApiEnvelope<T> {
  success: boolean;
  message: string;
  data: T;
  duplicate?: boolean;
}

export type Origen = 'telegram' | 'web';

export interface Gasto {
  id: number;
  monto: number;
  moneda: string;
  descripcion: string;
  categoria_id: number;
  categoria: string;
  categoria_color: string;
  metodo_pago: string | null;
  origen: Origen;
  identificador_externo: string | null;
  fecha: string;
  created_at: string;
  updated_at: string;
}

export interface GastoPaginado {
  items: Gasto[];
  total: number;
  pagina: number;
  limite: number;
  paginas: number;
}

export interface Categoria {
  id: number;
  nombre: string;
  descripcion: string | null;
  color_hex: string;
  activa: boolean;
  cantidad_gastos: number;
  created_at: string;
  updated_at: string;
}

export interface Regla {
  id: number;
  palabra_clave: string;
  categoria_id: number;
  categoria: string;
  categoria_color: string;
  prioridad: number;
  activa: boolean;
  created_at: string;
  updated_at: string;
}

export interface CategoriaDistribucion {
  categoria_id: number;
  nombre: string;
  color: string;
  monto: number;
  porcentaje: number;
}

export interface GastoPorDia {
  dia: number;
  fecha: string;
  monto: number;
}

export interface ComparacionMes {
  total_actual: number;
  total_anterior: number;
  diferencia: number;
  variacion_porcentaje: number | null;
}

export interface DashboardResumen {
  anio: number;
  mes: number;
  moneda: string;
  total_gastado: number;
  cantidad_transacciones: number;
  promedio_por_transaccion: number;
  categoria_mayor_gasto: CategoriaDistribucion | null;
  distribucion_por_categoria: CategoriaDistribucion[];
  gastos_por_dia: GastoPorDia[];
  comparacion_mes_anterior: ComparacionMes;
}

export interface GastoInput {
  monto: number | string;
  descripcion: string;
  categoria_id?: number | null;
  fecha?: string | null;
  metodo_pago?: string | null;
  moneda?: string;
}

export interface GastoUpdateInput {
  monto?: number | string;
  descripcion?: string;
  categoria_id?: number | null;
  fecha?: string | null;
  metodo_pago?: string | null;
  moneda?: string;
}

export interface CategoriaInput {
  nombre: string;
  descripcion?: string | null;
  color_hex: string;
  activa?: boolean;
}

export interface CategoriaUpdateInput {
  nombre?: string;
  descripcion?: string | null;
  color_hex?: string;
  activa?: boolean;
}

export interface ReglaInput {
  palabra_clave: string;
  categoria_id: number;
  prioridad: number;
  activa?: boolean;
}

export interface ReglaUpdateInput {
  palabra_clave?: string;
  categoria_id?: number;
  prioridad?: number;
  activa?: boolean;
}

export interface FiltrosGastos {
  mes?: number | null;
  anio?: number | null;
  fecha_desde?: string | null;
  fecha_hasta?: string | null;
  categoria_id?: number | null;
  metodo_pago?: string | null;
  origen?: Origen | null;
  q?: string | null;
  orden?: 'fecha_asc' | 'fecha_desc' | 'monto_asc' | 'monto_desc' | 'categoria_asc';
  pagina?: number;
  limite?: number;
}
