# Alineación visual frontend InVet

## Resultado visual objetivo

El HTML de referencia define una landing con:
- Header público.
- Hero con búsqueda.
- Chips de categoría: Veterinaria, Estética, Urgencias.
- Visual tipo bento.
- Sección “Cómo funciona”.
- CTA para registrar clínica.
- Footer.
- Navegación móvil de referencia.

## Ajustes obligatorios

- `PetCare` debe normalizarse a `InVet`.
- `Sign In` → `Iniciar sesión`.
- `Sign Up` → `Registrarse`.
- `Clinics` → `Clínicas`.
- `Grooming` → `Estética`.
- `Emergency` → `Urgencias`.
- “Reserva al instante” debe evitarse si backend no confirma disponibilidad en tiempo real. Usar “Solicita tu cita”.
- Enlaces `#` deben reemplazarse por rutas reales.
- La navegación móvil privada no debe mostrarse a visitantes anónimos si apunta a Bookings/Pets/Profile.

## Implementación esperada

No copiar HTML estático. Convertir a componentes:

```text
features/public-landing/
  components/PublicHeader.tsx
  components/HeroSection.tsx
  components/PublicSearchBar.tsx
  components/CategoryChips.tsx
  components/HeroBentoVisual.tsx
  components/HowItWorksSection.tsx
  components/ProfessionalCtaSection.tsx
  components/PublicFooter.tsx
```

## Tokens visuales

Usar Tailwind local con:
- Primary teal `#006065`.
- Secondary mint `#bcedda`.
- Warm sandy surfaces `#fff8f0`, `#faf3e8`, `#f4ede2`.
- Plus Jakarta Sans.
- Spacing base 8px.
- Containers max 1280px.
- Radius pill para botones/chips.
- Cards flotantes con sombra suave.

## Estados requeridos

- Loading.
- Error.
- Empty.
- Success.
- Disabled/submitting.

## Accesibilidad mínima

- Labels en inputs.
- Botones reales para acciones.
- Links reales para navegación.
- Focus visible.
- Contraste suficiente.
- Navegación por teclado.
