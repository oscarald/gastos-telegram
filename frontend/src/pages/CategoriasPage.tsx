import { useState } from 'react';
import Modal from '../components/ui/Modal';
import Button from '../components/ui/Button';
import { Field, Input, Select, Textarea } from '../components/ui/Field';
import { Alerta, Badge, Card, EstadoVacio } from '../components/ui/Card';
import { IconoBorrar, IconoEditar, IconoMas } from '../components/ui/Iconos';
import { Cargando } from '../components/ui/Modal';
import { useAsync } from '../hooks/useAsync';
import { categoriasService } from '../services';
import type { Categoria, CategoriaInput } from '../types';

interface Props {
  categoria: Categoria | null;
  onCerrar: () => void;
  onGuardar: (payload: CategoriaInput) => Promise<void>;
}

function CategoriaFormModal({ categoria, onCerrar, onGuardar }: Props) {
  const [nombre, setNombre] = useState(() => categoria?.nombre ?? '');
  const [descripcion, setDescripcion] = useState(() => categoria?.descripcion ?? '');
  const [color, setColor] = useState(() => categoria?.color_hex ?? '#6B7280');
  const [activa, setActiva] = useState(() => categoria?.activa ?? true);
  const [error, setError] = useState<string | null>(null);
  const [guardando, setGuardando] = useState(false);

  const enviar = async (evento: React.FormEvent) => {
    evento.preventDefault();
    setError(null);
    if (!nombre.trim()) {
      setError('El nombre es obligatorio.');
      return;
    }
    setGuardando(true);
    try {
      await onGuardar({
        nombre: nombre.trim(),
        descripcion: descripcion.trim() || null,
        color_hex: color,
        activa,
      });
      onCerrar();
    } catch (fallo) {
      setError(fallo instanceof Error ? fallo.message : 'No se pudo guardar la categoria');
    } finally {
      setGuardando(false);
    }
  };

  return (
    <Modal
      abierto
      titulo={categoria ? 'Editar categoria' : 'Nueva categoria'}
      descripcion="Las categorias activas pueden asignarse a los gastos y reglas."
      onCerrar={onCerrar}
      pie={
        <>
          <Button variante="secundario" onClick={onCerrar}>
            Cancelar
          </Button>
          <Button type="submit" form="form-categoria" cargando={guardando}>
            Guardar
          </Button>
        </>
      }
    >
      <form id="form-categoria" onSubmit={enviar} className="space-y-4">
        {error ? <Alerta mensaje={error} /> : null}

        <Field label="Nombre" htmlFor="nombre-categoria">
          <Input
            id="nombre-categoria"
            value={nombre}
            onChange={(evento) => setNombre(evento.target.value)}
            placeholder="Alimentación"
            maxLength={100}
            required
          />
        </Field>

        <Field label="Descripcion" htmlFor="descripcion-categoria">
          <Textarea
            id="descripcion-categoria"
            value={descripcion}
            onChange={(evento) => setDescripcion(evento.target.value)}
            placeholder="Comidas, mercado y despensa"
            maxLength={255}
          />
        </Field>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Field label="Color" htmlFor="color-categoria">
            <div className="flex gap-2">
              <input
                id="color-categoria"
                type="color"
                value={color}
                onChange={(evento) => setColor(evento.target.value)}
                className="h-10 w-14 cursor-pointer rounded-xl border border-surface-700 bg-surface-950 p-1"
              />
              <Input
                value={color}
                onChange={(evento) => setColor(evento.target.value)}
                placeholder="#6B7280"
                maxLength={7}
              />
            </div>
          </Field>

          <Field label="Estado" htmlFor="activa-categoria">
            <Select
              id="activa-categoria"
              value={activa ? '1' : '0'}
              onChange={(evento) => setActiva(evento.target.value === '1')}
            >
              <option value="1">Activa</option>
              <option value="0">Desactivada</option>
            </Select>
          </Field>
        </div>
      </form>
    </Modal>
  );
}

export default function CategoriasPage() {
  const { datos: categorias, cargando, error, recargar } = useAsync(
    async () => (await categoriasService.listar()).data,
    [],
  );

  const [modalAbierto, setModalAbierto] = useState(false);
  const [categoriaEditando, setCategoriaEditando] = useState<Categoria | null>(null);
  const [destino, setDestino] = useState<Categoria | null>(null);
  const [reemplazarPor, setReemplazarPor] = useState('');
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [errorAccion, setErrorAccion] = useState<string | null>(null);

  const abrirNueva = () => {
    setCategoriaEditando(null);
    setModalAbierto(true);
  };

  const abrirEdicion = (categoria: Categoria) => {
    setCategoriaEditando(categoria);
    setModalAbierto(true);
  };

  const guardar = async (payload: CategoriaInput) => {
    setErrorAccion(null);
    try {
      if (categoriaEditando) {
        await categoriasService.actualizar(categoriaEditando.id, payload);
        setMensaje('Categoria actualizada');
      } else {
        await categoriasService.crear(payload);
        setMensaje('Categoria creada');
      }
      recargar();
    } catch (fallo) {
      setErrorAccion(fallo instanceof Error ? fallo.message : 'No se pudo guardar la categoria');
      throw fallo;
    }
  };

  const alternarActiva = async (categoria: Categoria) => {
    try {
      await categoriasService.actualizar(categoria.id, { activa: !categoria.activa });
      recargar();
    } catch (fallo) {
      setErrorAccion(fallo instanceof Error ? fallo.message : 'No se pudo actualizar la categoria');
    }
  };

  const eliminar = async (categoria: Categoria) => {
    setErrorAccion(null);
    const confirmado = window.confirm(
      `Eliminar la categoria "${categoria.nombre}"? Si tiene gastos o reglas deberas reasignarlos.`,
    );
    if (!confirmado) return;
    try {
      await categoriasService.eliminar(categoria.id);
      setMensaje('Categoria eliminada');
      recargar();
    } catch (fallo) {
      if (fallo instanceof Error && fallo.message.includes('gastos')) {
        setDestino(categoria);
        setReemplazarPor('');
        return;
      }
      setErrorAccion(fallo instanceof Error ? fallo.message : 'No se pudo eliminar la categoria');
    }
  };

  const confirmarReasignacion = async () => {
    if (!destino || !reemplazarPor) return;
    try {
      await categoriasService.eliminar(destino.id, Number(reemplazarPor));
      setMensaje('Categoria eliminada y gastos reasignados');
      setDestino(null);
      recargar();
    } catch (fallo) {
      setErrorAccion(fallo instanceof Error ? fallo.message : 'No se pudo eliminar la categoria');
    }
  };

  return (
    <div className="space-y-5">
      <header className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-xl font-semibold text-zinc-50">Categorias</h1>
          <p className="text-sm text-zinc-500">
            Agrupa tus gastos y define el color con el que aparecen en los graficos.
          </p>
        </div>
        <Button onClick={abrirNueva} icono={<IconoMas />}>
          Nueva categoria
        </Button>
      </header>

      {error ? <Alerta mensaje={error} /> : null}
      {errorAccion ? <Alerta mensaje={errorAccion} onCerrar={() => setErrorAccion(null)} /> : null}
      {mensaje ? <Alerta mensaje={mensaje} tipo="exito" onCerrar={() => setMensaje(null)} /> : null}

      <Card>
        {cargando && !categorias ? (
          <Cargando texto="Cargando categorias..." />
        ) : categorias && categorias.length > 0 ? (
          <ul className="divide-y divide-surface-800/70">
            {categorias.map((categoria) => (
              <li
                key={categoria.id}
                className="flex flex-wrap items-center gap-3 py-3 first:pt-0 last:pb-0"
              >
                <span
                  className="h-9 w-9 shrink-0 rounded-xl"
                  style={{ backgroundColor: `${categoria.color_hex}22` }}
                >
                  <span
                    className="mx-auto mt-3 block h-3 w-3 rounded-full"
                    style={{ backgroundColor: categoria.color_hex }}
                    aria-hidden="true"
                  />
                </span>
                <div className="min-w-0 flex-1">
                  <p className="flex items-center gap-2 text-sm font-medium text-zinc-100">
                    {categoria.nombre}
                    {!categoria.activa ? (
                      <span className="rounded-full bg-surface-800 px-2 py-0.5 text-[10px] uppercase text-zinc-500">
                        inactiva
                      </span>
                    ) : null}
                  </p>
                  <p className="truncate text-xs text-zinc-500">
                    {categoria.descripcion ?? 'Sin descripcion'} ·{' '}
                    {categoria.cantidad_gastos} gasto(s)
                  </p>
                </div>
                <Badge color={categoria.color_hex}>{categoria.color_hex}</Badge>
                <div className="flex gap-1">
                  <Button
                    variante="secundario"
                    tamano="sm"
                    onClick={() => alternarActiva(categoria)}
                  >
                    {categoria.activa ? 'Desactivar' : 'Activar'}
                  </Button>
                  <button
                    type="button"
                    onClick={() => abrirEdicion(categoria)}
                    className="rounded-lg p-2 text-zinc-400 transition hover:bg-surface-700 hover:text-zinc-100"
                    aria-label={`Editar ${categoria.nombre}`}
                  >
                    <IconoEditar />
                  </button>
                  <button
                    type="button"
                    onClick={() => eliminar(categoria)}
                    className="rounded-lg p-2 text-zinc-400 transition hover:bg-red-500/20 hover:text-red-300"
                    aria-label={`Eliminar ${categoria.nombre}`}
                  >
                    <IconoBorrar />
                  </button>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <EstadoVacio titulo="Todavia no hay categorias" />
        )}
      </Card>

      {modalAbierto ? (
        <CategoriaFormModal
          categoria={categoriaEditando}
          onCerrar={() => setModalAbierto(false)}
          onGuardar={guardar}
        />
      ) : null}

      <Modal
        abierto={destino !== null}
        titulo="Reasignar antes de eliminar"
        descripcion={`La categoria "${destino?.nombre ?? ''}" tiene gastos o reglas asociados.`}
        onCerrar={() => setDestino(null)}
        pie={
          <>
            <Button variante="secundario" onClick={() => setDestino(null)}>
              Cancelar
            </Button>
            <Button variante="peligro" onClick={confirmarReasignacion} disabled={!reemplazarPor}>
              Reasignar y eliminar
            </Button>
          </>
        }
      >
        <Field label="Mover gastos y reglas a" htmlFor="categoria-destino">
          <Select
            id="categoria-destino"
            value={reemplazarPor}
            onChange={(evento) => setReemplazarPor(evento.target.value)}
          >
            <option value="">Selecciona una categoria</option>
            {(categorias ?? [])
              .filter((categoria) => categoria.id !== destino?.id)
              .map((categoria) => (
                <option key={categoria.id} value={categoria.id}>
                  {categoria.nombre}
                </option>
              ))}
          </Select>
        </Field>
      </Modal>
    </div>
  );
}
