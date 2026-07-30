export type ClinicCardModel = {
  slug: string;
  name: string;
  city: string;
  category: "Veterinaria" | "Estetica" | "Urgencias";
  services: string[];
  badge: string;
  responseTime: string;
};
