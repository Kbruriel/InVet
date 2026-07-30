"use client";

import { useEffect, useState } from "react";
import { ApiError, getApiRoot } from "@/shared/api/http-client";
import { Card } from "@/shared/ui/card";
import { StatePanel } from "@/shared/ui/state-panel";

type StatusState =
  | { status: "loading" }
  | { status: "success"; message: string }
  | { status: "error"; message: string };

export function ApiStatusCard() {
  const [state, setState] = useState<StatusState>({ status: "loading" });

  useEffect(() => {
    let active = true;

    async function loadStatus() {
      try {
        const response = await getApiRoot();

        if (!active) {
          return;
        }

        setState({
          status: "success",
          message: response.message ?? "API base disponible.",
        });
      } catch (error) {
        if (!active) {
          return;
        }

        const message =
          error instanceof ApiError
            ? error.message
            : "No fue posible leer el estado base del API.";

        setState({ status: "error", message });
      }
    }

    void loadStatus();

    return () => {
      active = false;
    };
  }, []);

  return (
    <Card className="space-y-4 bg-white/90">
      <div className="space-y-2">
        <p className="text-sm font-semibold uppercase tracking-[0.25em] text-brand-teal">
          Contrato API base
        </p>
        <h3 className="text-xl font-semibold text-ink-strong">
          Estado del backend desde el frontend
        </h3>
      </div>

      {state.status === "loading" ? (
        <StatePanel
          tone="info"
          title="Cargando estado"
          description="Verificando la raiz versionada del backend para dejar el cliente API listo para iteraciones posteriores."
        />
      ) : null}

      {state.status === "success" ? (
        <StatePanel
          tone="success"
          title="Conexion preparada"
          description={state.message}
        />
      ) : null}

      {state.status === "error" ? (
        <StatePanel
          tone="error"
          title="Backend no disponible en este momento"
          description={state.message}
        />
      ) : null}
    </Card>
  );
}
