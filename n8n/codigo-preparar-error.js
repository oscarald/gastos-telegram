// Codigo del nodo "Preparar error" del flujo n8n.
// Mensaje de respuesta cuando el mensaje de Telegram no se puede interpretar.

const original = $('Interpretar mensaje').item.json;

return [
  {
    chatId: original.chatId,
    texto: `⚠️ ${original.error ?? 'No pude interpretar el mensaje.'}`,
  },
];
