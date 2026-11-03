// Codigo del nodo "Preparar confirmacion" del flujo n8n.
// Traduce la respuesta de la API a un mensaje para Telegram.

const respuesta = $json;
const original = $('Interpretar mensaje').item.json;
const chatId = original.chatId;

const cuerpo = respuesta.body ?? respuesta;
const errorApi = respuesta.error ?? cuerpo.error;

if (errorApi || (respuesta.statusCode && respuesta.statusCode >= 400)) {
  const detalle =
    errorApi?.message ??
    cuerpo?.message ??
    `La API respondio con el estado ${respuesta.statusCode ?? 'desconocido'}`;
  return [{ chatId, texto: `⚠️ No pude registrar el gasto: ${detalle}` }];
}

const data = cuerpo.data ?? {};
const duplicado = Boolean(cuerpo.duplicate);
const monto = Number(data.monto ?? 0).toFixed(2);
const descripcion = data.descripcion ?? '';
const categoria = data.categoria ?? 'Sin categoria';

const texto = duplicado
  ? `ℹ️ Este gasto ya estaba registrado: ${monto} Bs - ${descripcion} (${categoria})`
  : `✅ Gasto registrado: ${monto} Bs - ${descripcion} (${categoria})`;

return [{ chatId, texto }];
