'use client'

import type {
  BranchPublicProfile,
  RatingSummaryPublic,
  SchedulePublic,
  ServicePublic,
} from '@/shared/api/types'

interface Props {
  branch: BranchPublicProfile
}

export function BranchProfile({ branch }: Props) {
  const isCurrentlyOpen = checkIfOpen(branch.schedules)

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <section aria-labelledby="branch-name" className="mb-6">
        <h1 id="branch-name" className="text-2xl font-semibold text-gray-900 mb-2">
          {branch.name}
        </h1>
        <p className="text-gray-600">
          {branch.address}, {branch.city}
        </p>
        {branch.phone && (
          <a href={`tel:${branch.phone}`} aria-label={`Llamar a ${branch.name}`}>
            📞 {branch.phone}
          </a>
        )}
      </section>

      <section aria-labelledby="services-heading" className="mb-6">
        <h2 id="services-heading" className="text-lg font-medium text-gray-900 mb-3">
          Servicios
        </h2>
        {branch.services.length === 0 ? (
          <p className="text-gray-500 text-sm">No hay servicios publicados.</p>
        ) : (
          <ul role="list" aria-label="Lista de servicios">
            {branch.services.map((service: ServicePublic) => (
              <li key={service.id} className="flex items-center gap-2 mb-1 text-gray-700">
                <span aria-hidden="true">•</span> {service.name}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section aria-labelledby="schedule-heading" className="mb-6">
        <h2 id="schedule-heading" className="text-lg font-medium text-gray-900 mb-3">
          Horarios de atención
        </h2>
        <span
          className={`inline-block px-3 py-1 rounded-full text-sm ${
            isCurrentlyOpen ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
          }`}
          role="status"
          aria-live="polite"
        >
          {isCurrentlyOpen ? 'Abierto ahora' : 'Cerrado ahora'}
        </span>

        <TableSchedule schedules={branch.schedules} />
      </section>

      <section aria-labelledby="rating-heading" className="mb-6">
        <h2 id="rating-heading" className="text-lg font-medium text-gray-900 mb-3">
          Calificaciones
        </h2>
        {ratingContent(branch.rating_summary)}
      </section>

      <CtaAppointment branchId={branch.id} />
    </div>
  )
}

function TableSchedule({ schedules }: { schedules: SchedulePublic[] }) {
  return (
    <table aria-label="Horarios de la sucursal" className="w-full mt-3 text-sm">
      <thead>
        <tr className="border-b border-gray-200">
          <th className="text-left py-1 pr-4 font-medium text-gray-600">Día</th>
          <th className="text-left py-1 px-4 font-medium text-gray-600">Abre</th>
          <th className="text-left py-1 pl-4 font-medium text-gray-600">Cierra</th>
        </tr>
      </thead>
      <tbody>
        {schedules.length === 0 ? (
          <tr>
            <td colSpan={3} className="py-2 text-gray-500 italic">
              Sin horarios definidos.
            </td>
          </tr>
        ) : (
          schedules
            .slice()
            .sort((a, b) => a.day_of_week - b.day_of_week)
            .map((schedule) => (
              <tr key={schedule.id} className="border-b border-gray-100">
                <td className="py-1 pr-4 text-gray-700">{DayLabel(schedule.day_of_week)}</td>
                <td className="py-1 px-4 text-gray-600">{schedule.open_time}</td>
                <td className="py-1 pl-4 text-gray-600">{schedule.close_time}</td>
              </tr>
            ))
        )}
      </tbody>
    </table>
  )
}

function CtaAppointment({ branchId }: { branchId: number }) {
  return (
    <a
      href={`/clinics/booking?branch=${branchId}`}
      aria-label="Solicitar cita para esta sucursal"
      className="inline-flex items-center justify-center rounded-lg bg-teal-600 px-5 py-3 text-white font-medium cursor-pointer hover:bg-teal-700 transition-colors"
    >
      Solicitar cita
    </a>
  )
}

function ratingContent(rating?: RatingSummaryPublic | null) {
  if (rating == null || rating.total_reviews === 0) {
    return <p className="text-gray-500 text-sm">Sin calificaciones aún.</p>
  }

  const average = rating.average_rating ?? 0

  return (
    <div aria-label={`Calificación: ${average} sobre 5 basada en ${rating.total_reviews} opiniones`}>
      <span className="text-xl font-semibold text-gray-900">{average}</span>
      <span className="ml-1 text-sm text-gray-600">({rating.total_reviews} opiniones)</span>

      {rating.review_distribution && (
        <div aria-hidden="true" role="img" className="mt-2 flex gap-1">
          ★★★★★
        </div>
      )}
    </div>
  )
}

function checkIfOpen(schedules: SchedulePublic[]): boolean {
  return schedules.some((schedule) => {
    const now = new Date()
    const today = (now.getDay() + 6) % 7
    if (schedule.day_of_week !== today) return false

    const [startH, startM] = schedule.open_time.split(':').map(Number)
    const [endH, endM] = schedule.close_time.split(':').map(Number)
    const currentMinutes = now.getHours() * 60 + now.getMinutes()
    const openMinutes = startH * 60 + startM
    const closeMinutes = endH * 60 + endM

    return currentMinutes >= openMinutes && currentMinutes <= closeMinutes
  })
}

function DayLabel(dayOfWeek: number): string {
  const days = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
  return days[dayOfWeek] ?? ''
}
