'use client';

export function HowItWorksSection() {
  const steps = [
    {
      step: '1',
      title: 'Busca',
      description: 'Ingresa el nombre de la clínica, ciudad o servicio que necesitas.',
    },
    {
      step: '2',
      title: 'Compara',
      description: 'Revisa perfiles públicos, servicios disponibles y calificaciones.',
    },
    {
      step: '3',
      title: 'Solicita',
      description: 'Envía tu solicitud de cita directamente desde el perfil de la clínica.',
    },
  ];

  return (
    <section aria-label="Como funciona" className="py-16 sm:py-24">
      <div className="mx-auto max-w-4xl px-4 text-center">
        <h2 className="text-2xl font-extrabold text-slate-900 sm:text-3xl">
          Como funciona InVet
        </h2>
        <p className="mt-3 text-base text-slate-600">
          Un proceso simple para conectar con la mejor atencion veterinaria.
        </p>

        <div className="mt-12 grid gap-8 sm:grid-cols-3">
          {steps.map((s) => (
            <div
              key={s.step}
              className="rounded-2xl bg-white p-6 shadow-sm border border-sandy-300 text-center"
            >
              <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-teal text-xl font-bold text-white">
                {s.step}
              </div>
              <h3 className="mb-2 text-lg font-semibold text-slate-900">{s.title}</h3>
              <p className="text-sm text-slate-600">{s.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
