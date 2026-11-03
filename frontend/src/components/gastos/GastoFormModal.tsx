import { useState } from 'react';
import Modal from '../ui/Modal';
import Button from '../ui/Button';
import { Field, Input, Select } from '../ui/Field';
import { Alerta } from '../ui/Card';
import type { Categoria, Gasto, GastoInput } from '../../types';

const METODOS = ['Efectivo', 'Tarjeta de débito', 'Tarjeta de crédito', 'QR', 'Transferencia', 'Otros'];

function toDateTimeLocal(iso: string | null | undefined): string {
  if (!iso) return '';
  const fecha = new Date(iso);
  if (Number.isNaN(fecha.getTime())) return '';
  const offset = fecha.getTimezoneOffset();
  const local = new Date(fecha.getTime() - offset * 60000);
  return local.toISOString().slice(0, 16);
}

interface Props {
  gasto: Gasto | null;
  categorias: Categoria[];
  onCerrar: () => void;
  onGuardar: (payload: GastoInput) => Promise<void>;
}

export default function GastoFormModal({ gasto, categorias, onCerrar, onGuardar }: Props) {
  const [monto, setMonto] = useState(() => (gasto ? String(gasto.monto) : ''));
  const [descripcion, setDescripcion] = useState(() => gasto?.descripcion ?? '');
  const [categoriaId, setCategoriaId] = useState(() => (gasto ? String(gasto.categoria_id) : ''));
  const [fecha, setFecha] = useState(() => toDateTimeLocal(gasto?.fecha));
  const [metodoPago, setMetodoPago] = useState(() => gasto?.metodo_pago ?? '');
  const [error, setError] = useState<string | null>(null);
  const [guardando, setGuardando] = useState(false);

  const enviar = async (evento: React.FormEvent) => {
    evento.preventDefault();
    setError(null);

    const valor = Number(monto.replace(',', '.'));
    if (!Number.isFinite(valor) || valor <= 0) {
      setError('El monto debe ser un numero mayor que cero.');
      return;
    }
    if (!descripcion.trim()) {
      setError('La descripcion es obligatoria.');
      return;
    }

    setGuardando(true);
    try {
      await onGuardar({
        monto: valor,
        descripcion: descripcion.trim(),
        categoria_id: categoriaId ? Number(categoriaId) : null,
        fecha: fecha ? new Date(fecha).toISOString() : null,
        metodo_pago: metodoPago || null,
      });
      onCerrar();
    } catch (fallo) {
      setError(fallo instanceof Error ? fallo.message : 'No se pudo guardar el gasto');
    } finally {
      setGuardando(false);
    }
  };

  const categoriasActivas = categorias.filter((categoria) => categoria.activa || categoria.id === gasto?.categoria_id);

  return (
    <Modal
      abierto
      titulo={gasto ? 'Editar gasto' : 'Nuevo gasto'}
      descripcion={
        gasto
          ? 'Modifica los datos y guarda los cambios.'
          : 'Registra un gasto manualmente. La categoria puede definirse por las reglas.'
      }
      onCerrar={onCerrar}
      pie={
        <>
          <Button variante="secundario" onClick={onCerrar}>
            Cancelar
          </Button>
          <Button type="submit" form="form-gasto" cargando={guardando}>
            {gasto ? 'Guardar cambios' : 'Registrar gasto'}
          </Button>
        </>
      }
    >
      <form id="form-gasto" onSubmit={enviar} className="space-y-4">
        {error ? <Alerta mensaje={error} /> : null}

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Field label="Monto (Bs)" htmlFor="monto">
            <Input
              id="monto"
              type="number"
              step="0.01"
              min="0.01"
              inputMode="decimal"
              value={monto}
              onChange={(evento) => setMonto(evento.target.value)}
              placeholder="0.00"
              required
            />
          </Field>

          <Field label="Fecha" htmlFor="fecha">
            <Input
              id="fecha"
              type="datetime-local"
              value={fecha}
              onChange={(evento) => setFecha(evento.target.value)}
            />
          </Field>
        </div>

        <Field label="Descripcion" htmlFor="descripcion">
          <Input
            id="descripcion"
            value={descripcion}
            onChange={(evento) => setDescripcion(evento.target.value)}
            placeholder="Almuerzo en restaurante"
            maxLength={255}
            required
          />
        </Field>

        <Field
          label="Categoria"
          htmlFor="categoria"
          hint="Selecciona 'Automatico' para aplicar las reglas configuradas."
        >
          <Select
            id="categoria"
            value={categoriaId}
            onChange={(evento) => setCategoriaId(evento.target.value)}
          >
            <option value="">Automatico (según reglas)</option>
            {categoriasActivas.map((categoria) => (
              <option key={categoria.id} value={categoria.id}>
                {categoria.nombre}
              </option>
            ))}
          </Select>
        </Field>

        <Field label="Metodo de pago" htmlFor="metodo">
          <Select
            id="metodo"
            value={metodoPago}
            onChange={(evento) => setMetodoPago(evento.target.value)}
          >
            <option value="">Sin especificar</option>
            {METODOS.map((metodo) => (
              <option key={metodo} value={metodo}>
                {metodo}
              </option>
            ))}
          </Select>
        </Field>
      </form>
    </Modal>
  );
}
