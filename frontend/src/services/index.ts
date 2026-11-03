import { downloadCsv, get, post, put, remove } from './api';
import type {
  Categoria,
  DashboardResumen,
  FiltrosGastos,
  Gasto,
  GastoInput,
  GastoPaginado,
  GastoUpdateInput,
  Regla,
  ReglaInput,
  ReglaUpdateInput,
  CategoriaInput,
  CategoriaUpdateInput,
} from '../types';

export const gastosService = {
  listar: (filtros: FiltrosGastos = {}) => get<GastoPaginado>('/gastos', { ...filtros }),
  obtener: (id: number) => get<Gasto>(`/gastos/${id}`),
  crear: (payload: GastoInput) => post<Gasto>('/gastos', payload),
  actualizar: (id: number, payload: GastoUpdateInput) => put<Gasto>(`/gastos/${id}`, payload),
  eliminar: (id: number) => remove<Gasto>(`/gastos/${id}`),
  exportarCsv: (filtros: FiltrosGastos = {}) => downloadCsv('/gastos/export/csv', { ...filtros }),
};

export const categoriasService = {
  listar: (soloActivas = false) => get<Categoria[]>('/categorias', { solo_activas: soloActivas }),
  crear: (payload: CategoriaInput) => post<Categoria>('/categorias', payload),
  actualizar: (id: number, payload: CategoriaUpdateInput) =>
    put<Categoria>(`/categorias/${id}`, payload),
  eliminar: (id: number, reemplazarPor?: number | null) =>
    remove<Categoria>(`/categorias/${id}`, reemplazarPor ? { reemplazar_por: reemplazarPor } : undefined),
};

export const reglasService = {
  listar: (soloActivas = false) => get<Regla[]>('/reglas', { solo_activas: soloActivas }),
  crear: (payload: ReglaInput) => post<Regla>('/reglas', payload),
  actualizar: (id: number, payload: ReglaUpdateInput) => put<Regla>(`/reglas/${id}`, payload),
  eliminar: (id: number) => remove<Regla>(`/reglas/${id}`),
};

export const dashboardService = {
  resumen: (params: { anio?: number; mes?: number; categoria_id?: number | null; metodo_pago?: string | null }) =>
    get<DashboardResumen>('/dashboard/resumen', { ...params }),
};

export const sistemaService = {
  metodosPago: () => get<string[]>('/metodos-pago'),
  health: () => get<{ status: string; database: string }>('/health'),
};
