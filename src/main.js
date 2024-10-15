import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import 'splitpanes/dist/splitpanes.css'
import './style.css'

// Vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

//Pinia
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

const vuetify = createVuetify({
  components,
  directives
})

//mdi icons
import '@mdi/font/css/materialdesignicons.css'

createApp(App).use(vuetify).use(router).use(pinia).mount('#app')
