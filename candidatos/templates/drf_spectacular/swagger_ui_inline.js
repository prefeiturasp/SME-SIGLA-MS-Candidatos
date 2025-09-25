"use strict";

const swaggerSettings = {{ settings|safe }};

window.ui = SwaggerUIBundle({
  spec: {{ schema|safe }},
  dom_id: '#swagger-ui',
  presets: [SwaggerUIBundle.presets.apis],
  layout: 'BaseLayout',
  ...swaggerSettings,
}); 