import express from "express";

const app = express();
app.use(express.json());

const recursosBloqueados = new Set();

app.post("/lock", (req, res) => {
  const { resource_id } = req.body;
  console.log(`Recebido pedido de lock para o recurso ${resource_id}`);

  if (recursosBloqueados.has(resource_id)) {
    console.log(`Recurso ${resource_id} já está em uso, negando lock`);
    return res.status(409).json({
      status: "recurso_ocupado",
      _links: { self: "/lock" },
    });
  }

  recursosBloqueados.add(resource_id);
  console.log(`Lock concedido para o recurso ${resource_id}`);
  return res.status(200).json({
    status: "lock_concedido",
    _links: { unlock: "/unlock" },
  });
});

app.post("/unlock", (req, res) => {
  const { resource_id } = req.body;
  console.log(`Recebido pedido de unlock para o recurso ${resource_id}`);

  if (recursosBloqueados.has(resource_id)) {
    recursosBloqueados.delete(resource_id);
    console.log(`Lock para o recurso ${resource_id} liberado`);
  } else {
    console.log(`Recurso ${resource_id} não estava bloqueado`);
  }

  return res.status(200).json({
    status: "lock_liberado",
    _links: { self: "/unlock", request_lock: "/lock" },
  });
});

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`🟢 Coordenador ativo na porta ${PORT}`);
});
