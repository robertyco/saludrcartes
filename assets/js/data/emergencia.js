/* ============================================================================
   saludrcartes — Ficha pública de emergencia
   ----------------------------------------------------------------------------
   Este archivo es el ÚNICO que carga emergencia.html. Contiene solo
   información crítica: grupo sanguíneo, alergias, condiciones que deben
   conocerse de inmediato, medicamentos esenciales y contactos.

   No agregues aquí diagnósticos, documentos ni datos del historial completo.
   Esa separación es intencional: un enlace de emergencia no debe exponer el
   resto del sitio.

   Datos de DEMOSTRACIÓN. Cambia meta.demo a false solo cuando reemplaces
   todos los datos y teléfonos por información real.
   ========================================================================== */

window.EMERGENCIA_DATA = {
  meta: {
    demo: false,
    actualizado: '2026-11-03',
    titular: 'Roberto Carlos Cartes Jiménez',
    sitio: 'saludrcartes',
    publico: true
  },

  perfil: {
    nombre: 'Roberto Carlos Cartes Jiménez',
    preferido: 'Roberto',
    grupoSanguineo: 'O+'
  },

  critico: {
    alergias: [
      {
        sustancia: 'Penicilina',
        severidad: 'Moderada',
        reaccion: 'Urticaria y picazón'
      }
    ],
    condiciones: [
      'Lumbalgia mecánica en seguimiento',
      'Síndrome de túnel carpiano derecho',
      'Dolor de hombro derecho'
    ],
    medicamentos: [
      'Paracetamol 500 mg, según necesidad',
      'Ibuprofeno 400 mg, según necesidad',
      'Vitamina D 1000 UI, diaria'
    ],
    notas: [
      'No se registran alergias graves conocidas.',
      'Confirmar teléfonos de contacto antes de una urgencia.'
    ]
  },

  contactos: [
    {
      id: 'contacto-principal',
      nombre: 'Contacto familiar principal',
      relacion: 'Familiar directo',
      telefono: '+56 9 0000 0001',
      principal: true
    },
    {
      id: 'contacto-medico',
      nombre: 'Dra. Valentina Rojas',
      relacion: 'Médica de cabecera',
      telefono: '+56 9 0000 0002',
      principal: false
    },
    {
      id: 'contacto-centro',
      nombre: 'Hospital de Referencia (ejemplo)',
      relacion: 'Centro de salud',
      telefono: '+56 2 0000 0000',
      principal: false
    },
    {
      id: 'contacto-samu',
      nombre: 'SAMU',
      relacion: 'Ambulancia',
      telefono: '131',
      principal: false,
      publico: true
    },
    {
      id: 'contacto-carabineros',
      nombre: 'Carabineros',
      relacion: 'Emergencias',
      telefono: '133',
      principal: false,
      publico: true
    },
    {
      id: 'contacto-bomberos',
      nombre: 'Bomberos',
      relacion: 'Incendios y rescate',
      telefono: '132',
      principal: false,
      publico: true
    }
  ]
};
