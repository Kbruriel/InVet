import type { ClinicCardModel } from "@/entities/clinic/model";

export const mockClinics: ClinicCardModel[] = [
  {
    slug: "vet-norte",
    name: "InVet Norte",
    city: "Ciudad de Mexico",
    category: "Veterinaria",
    services: ["Consulta general", "Vacunacion", "Control preventivo"],
    badge: "Agenda guiada",
    responseTime: "Responde en 10 min",
  },
  {
    slug: "estetica-santa-fe",
    name: "InVet Santa Fe",
    city: "Ciudad de Mexico",
    category: "Estetica",
    services: ["Bano medicado", "Corte higienico", "Spa felino"],
    badge: "Atencion amable",
    responseTime: "Responde en 20 min",
  },
  {
    slug: "urgencias-monterrey",
    name: "InVet Monterrey 24h",
    city: "Monterrey",
    category: "Urgencias",
    services: ["Trauma", "Observacion", "Laboratorio urgente"],
    badge: "24/7",
    responseTime: "Respuesta inmediata",
  },
];
